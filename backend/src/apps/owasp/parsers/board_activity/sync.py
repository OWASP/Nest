"""Board activity sync orchestration."""

from __future__ import annotations

import logging
import os
import re
import sys
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

import requests
from requests.exceptions import RequestException

from apps.common.open_ai import OpenAi
from apps.github.utils import get_repository_file_content
from apps.owasp.models.board_meeting import BoardMeeting
from apps.owasp.parsers.board_activity import translator
from apps.owasp.parsers.board_activity.schemas import ParsedMeeting

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o"
DEFAULT_MAX_TOKENS = 16000
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TIMEOUT = 60

REPO_OWNER = "OWASP"
REPO_NAME = "www-board"
REPO_BRANCH = "master"

TREE_URL = (
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{REPO_BRANCH}?recursive=1"
)
RAW_FILE_URL_TEMPLATE = (
    f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/{{path}}"
)

MEETING_DIRS: tuple[str, ...] = (
    "meetings-historical/",
    "minutes-deprecated/",
)
YEARMONTH_PREFIX_LEN = 6  # YYYY + MM
FILENAME_PREFIX_RE = re.compile(rf"^\d{{{YEARMONTH_PREFIX_LEN}}}")

SYSTEM_PROMPT = """\
You extract structured data from OWASP Board of Directors meeting minutes (unstructured Markdown)
into the provided schema. Board minutes are a legal record; the goal is to preserve every agenda
item and every decision faithfully.

## Section boundaries

Every markdown heading (`##`, `###`, `####`) introduces a new section. Each substantive heading
maps to its own action. NEVER merge content from different headings into a single description,
even if they share a parent heading (e.g. six H4 sub-sections under "Executive Director Report"
are SIX separate discussions, not one big one). When in doubt, split.

## Meeting structure

Meetings follow a fairly consistent shape. Typical top-level sections (H2/H3):
- CALL TO ORDER - a roster of board members present and guests. Extract into `attendees` and
  `guests`. Board members explicitly listed as absent (or implied by omission with an "Absent:"
  note) go in `absentees`. Does not produce any action - do not emit as a discussion.

- CONFLICT OF INTEREST / ANTI-TRUST STATEMENT - boilerplate. Skip. The typical text starts with:
  "As the Board consists of individuals from many competing organizations, OWASP and its Board
  shall abide by all applicable anti-trust and competition laws..." Any body matching this shape
  (or wholly consisting of policy links + the phrase "must recuse themselves") produces zero
  actions. If a specific disclosure IS made in the section ("Andrew and Dawn to review the
  conflict"), extract only that as its own outcome; do not also emit the boilerplate as a
  discussion.

- CHANGES TO THE AGENDA - if there's real content (e.g. "add discussion on X"), emit as a
  discussion. If the body is only the standard policy paragraph starting with "Changes to the
  agenda - unless otherwise prohibited by anti-trust or competition laws - including adding,
  altering, or tabling of motions is permitted by following Roberts Rules of Order", skip entirely.

- APPROVAL OF MINUTES - a vote on the previous meeting's minutes. Synthesize a stub motion
  (see "Votes" below).

- PRE-READING MATERIAL - a list of links. Add each link to `attachments`, do NOT emit as a
  discussion/motion/outcome unless the section also has narrative content (multi-sentence prose
  beyond a link caption). A bare bulleted link list like
      - [Executive Director Board Summary](https://...)
      - [Finance Board Narrative](/attachments/...)
  produces zero actions - only attachments.

- REPORTS - subsections (usually H4) like "Executive Director report", "Finance report",
  "Committee reports". Each substantive subsection is a `discussion`. Don't collapse them into one.

- NEW BUSINESS - mix of motions, discussions, and status updates. Each H3/H4 subsection
  is its own action.

- COMMENTS, ANNOUNCEMENTS - usually thin. If empty, skip.

- ADJOURNMENT - a motion, usually with sponsor+second but often no formal vote tally.
  Emit as a motion; vote is null if no tally is given.

## Action kinds

Every substantive subsection maps to exactly one action:

- `discussion`: any narrative topic without a formal vote - status updates, ED/finance reports,
  working group updates, executive session summaries, policy deliberations, etc. Populate `topic
  (the heading) and `description` (the paragraph text).

  Populate `participants` from ALL of:
    - names in the section heading (e.g. "#### Andrew van der Stock -
      Executive Director" -> Andrew van der Stock)
    - names in the body prose ("Andrew presented...", "Sam highlighted...")
    - role references that can be resolved against the meeting's known people
      ("The Executive Director" -> Andrew van der Stock if Andrew is listed as ED)
    - explicit sponsors of a discussion (e.g. "Discussion on X (sponsored by Ricardo)" -> Ricardo)
  If no specific person is named or resolvable, leave empty.

  Do NOT enumerate all attendees when the source refers to the group as a whole. Treat these
  phrases as "the whole group" and leave the corresponding participant/assignee list empty:
    - "the Board", "The Board of Directors"
    - "All Board Members", "all directors", "every board director"
    - "the Directors" (when unqualified)
    - "the Board members present", "attending directors"
  Only enumerate individuals when the source itself names them.

- `motion`: a formal proposal, usually phrased "Motion:" or "Resolved, that...". Almost always has
  a sponsor + second and (usually) a vote. Populate `title` (a short label), `description` (the
  resolved-that clause), `background` (any explanatory prose before the motion),
  `sponsor`, `second`, and `vote`.

- `outcome`: an action item - an explicit commitment for someone (or a group) to do something after
  the meeting. Populate `description` with the action text and `assignees` with the named person(s)
  `status` defaults to "pending".

  Action items appear in TWO places:
    a) explicit "Action Items:" / "Board Comments & Actions" bullet blocks.
    b) INLINE within discussion prose, e.g. "Andrew to confirm SLA with Belgian authorities",
    "directors Diego and Ashwini to provide ID by 9 September", "Sam and Andrew to consolidate
    proposed edits".

  Extract BOTH. For (b), scan every discussion description for sentences of the form
  "<named person(s)> to <verb> <object>" (future commitment) or "<named person(s)> will <verb>",
  and emit each as a separate `outcome` action that follows the parent discussion in agenda order.

  `due_date`: parse deadlines from phrases like "by <date>", "before <date>",
  "no later than <date>". Populate as ISO 8601 date (YYYY-MM-DD). Rules:
    - "by 9 September" in a 2025 meeting -> "2025-09-09" (infer year from
      the meeting date, month always closer future).
    - "by February" (bare month, no day) -> null. Do not guess a day.
    - "by end of Q1" / "by next meeting" / vague relative dates -> null.
    - Absolute dates ("by March 15, 2026") -> "2026-03-15".

Emit actions in the order they appear in the source. Be exhaustive: every substantive subsection
should produce an action, and every embedded commitment should produce its own outcome.

## Structured content in descriptions

When a section body contains structured data - bulleted stat lists (KPIs, finance figures, dollar
amounts, percentages, counts), tables, or numeric enumerations - keep the raw list/table content
in the `description` as-is rather than summarizing to prose. Join bullets with newlines.
This applies only within a single section; do not merge multiple sections into one description.

## Votes

Every vote must be attached to a motion (`ParsedVote` is nested under `ParsedMotion`). If a vote
appears without a formal motion - most commonly for "APPROVAL OF MINUTES" -
synthesize a stub motion:
    title: "Approve <Month YYYY> meeting minutes"
    description: "Resolved, that the <Month YYYY> meeting minutes are approved."
    sponsor / second: null

For each vote, populate the four cast lists (`in_favor`, `against`, `abstain`, `recused`)
from the individual member votes in the source.

`tally`: dash-separated counts in the order in_favor-against-abstain(-recused). Always include the
abstain and recused counts if any member abstained or recused
- e.g. 6 yes + 0 no + 1 abstain -> "6-0-1", NOT "6-0". Only omit trailing zeros
(so "7-0" is fine when nobody voted against, abstained, or recused).

## Names

Preserve people's names exactly as they appear in the source, with one exception: when the source
uses a first-name-only reference (e.g. "Dave", "Ricardo") inside a vote record, discussion,
or outcome, resolve it to the corresponding full name from the meeting's attendees/guests roster
IF the mapping is unambiguous. Example:
    Roster: "Dave Wichers", "Eoin Keary", "Matt Tesauro"
    Source: "(Approve: Dave, Eoin, Matt)"
    -> in_favor: ["Dave Wichers", "Eoin Keary", "Matt Tesauro"]

If a short-form name matches multiple people in the roster (e.g. two "Daves"), keep it as-is rather
than guessing. Do not normalize casing or fix typos.

The same person may be referenced multiple times in one meeting - use identical strings each time
so downstream deduplication works.

## Attachments and references

Links appear throughout: pre-reading material, motion supporting docs, next-meeting pointers,
video recordings. Extract every labeled Markdown link `[label](url)` as `{label, url}`. Meeting
level links go in `attachments`, motion-specific supporting docs go in the motion's `references`.

## Metadata

- `date`: ISO 8601 UTC (e.g. "2025-08-26T13:00:00+00:00"). If only the date
  is known, use 00:00:00 UTC for time.
- `type`: public (default), private, special, or summit - infer from the
  title or filename hints (e.g. "-special" suffix).
- `quorum_present`: null unless explicitly stated.
- `location`, `call_in_url`, `recording_url`: populate from the "Meeting Details" block.
If the only URL is a YouTube recording, put it in `recording_url`.

## Editor annotations

Wiki-style editor notes such as `[ ajv edit 2021-01-27: adding financial packages ]`,
`[TODO: fill in]`, or `<!-- ... -->` HTML comments are housekeeping, not meeting content.
Skip them entirely; do not emit as discussions and do not include in any description.

## Unknown fields

If a field is unknown, use the schema default (empty string, null, or empty list).
Do not fabricate.

## Example - outcome extraction from a discussion section

Input:
    #### EU Entity Status
    **Background** The ED will update on the new EU entity.
    - Belgian Government approval pending.
    - Directors Diego and Ashwini to provide ID by 9 September for Regus offices.
    - Andrew to confirm SLA with Belgian authorities.
    - Board to review draft charter by November - Board Meeting.
    - Sam to send meeting invites on October 25.

Meeting date: 2025-08-26

Output (in agenda order):
    discussion:
        topic: "EU Entity Status"
        description: "The ED will update on the new EU entity.
                      Belgian Government approval pending."
        participants: []
    outcome:
        description: "Diego and Ashwini to provide ID for Regus offices."
        assignees: [Diego Silva Martins, Ashwini Siddhi]
        due_date: "2025-09-09"    # "by 9 September" -> specific day, year inferred
    outcome:
        description: "Andrew to confirm SLA with Belgian authorities."
        assignees: [Andrew van der Stock]
        due_date: null            # no deadline stated
    outcome:
        description: "Review draft charter."
        assignees: []             # "Board" is a group reference; keep empty
        due_date: null            # "November - Board Meeting" is bare month; NEVER guess a day
    outcome:
        description: "Sam to send meeting invites."
        assignees: [Sam Stepanyan]
        due_date: "2025-10-25"    # "on <date>" is a deadline
"""


class SyncStatus(StrEnum):
    """Terminal status codes for a per-file sync."""

    CREATED = "created"
    ERRORED = "errored"
    SKIPPED = "skipped"
    UNCHANGED = "unchanged"
    UPDATED = "updated"
    WOULD_UPDATE = "would_update"


@dataclass
class SyncStats:
    """Aggregate status counters for a sync run."""

    counts: dict[str, int] = field(default_factory=dict)

    def record(self, status: str) -> None:
        """Increment the counter for the given status.

        Args:
            status (str): A SyncStatus value.

        """
        self.counts[status] = self.counts.get(status, 0) + 1


def fetch_tree() -> dict[str, str]:
    """Fetch the recursive git tree for the www-board repository.

    Returns:
        dict[str, str]: Map of file path to git blob SHA.

    Raises:
        RequestException: If the GitHub API call fails.

    """
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(TREE_URL, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()

    return {
        item["path"]: item["sha"] for item in payload.get("tree", []) if item["type"] == "blob"
    }


def target_paths(
    tree: dict[str, str],
    *,
    year: int | None = None,
    month: int | None = None,
    path: str | None = None,
) -> Iterable[str]:
    """Yield meeting markdown file paths matching the given filters.

    Args:
        tree (dict[str, str]): Map of path to blob SHA.
        year (int, optional): Restrict to files whose filename begins with the given 4-digit year.
        month (int, optional): Restrict to files whose filename begins with
            year and month. Requires year.
        path (str, optional): Return only the given path if present in the tree.

    Yields:
        str: A matching file path.

    """
    if path:
        if path in tree:
            yield path
        return

    prefix = ""
    if year is not None:
        prefix = str(year)
        if month is not None:
            prefix = f"{year}{month:02d}"

    for tree_path in tree:
        if not tree_path.endswith(".md"):
            continue
        if not any(tree_path.startswith(d) for d in MEETING_DIRS):
            continue

        filename = tree_path.rsplit("/", 1)[-1]
        if filename.startswith("_"):
            continue
        if not FILENAME_PREFIX_RE.match(filename):
            continue
        if prefix and not filename.startswith(prefix):
            continue

        yield tree_path


def fetch_file_content(path: str) -> str:
    """Fetch the raw content of a file from the www-board repository.

    Args:
        path (str): Repo-relative path of the file.

    Returns:
        str: The file content, or empty string if the fetch failed.

    """
    return get_repository_file_content(RAW_FILE_URL_TEMPLATE.format(path=path))


def sync_file(
    path: str,
    blob_sha: str,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> SyncStatus:
    """Sync a single meeting file into the database.

    Args:
        path (str): Repo-relative path of the file.
        blob_sha (str): Current git blob SHA for the file.
        force (bool, optional): Re-parse even when the stored checksum matches. Defaults to False.
        dry_run (bool, optional): Skip DB writes. Defaults to False.

    Returns:
        SyncStatus: A SyncStatus value.

    """
    existing = BoardMeeting.objects.filter(source_path=path).first()
    if existing and existing.source_checksum == blob_sha and not force:
        return SyncStatus.UNCHANGED

    content = fetch_file_content(path)
    if not content:
        logger.warning("Empty content for %s; skipping", path)
        return SyncStatus.SKIPPED

    client = OpenAi(
        model=DEFAULT_MODEL,
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
        timeout=DEFAULT_TIMEOUT,
    )
    parsed = client.set_prompt(SYSTEM_PROMPT).set_input(content).parse(ParsedMeeting)

    if parsed is None:
        logger.error("LLM parse failed for %s", path)
        return SyncStatus.ERRORED

    if dry_run:
        sys.stdout.write(f"\n=== Parsed {path} ===\n")
        sys.stdout.write(parsed.model_dump_json(indent=2))
        sys.stdout.write("\n")
        return SyncStatus.WOULD_UPDATE

    translator.upsert(parsed, source_path=path, source_checksum=blob_sha)
    return SyncStatus.UPDATED if existing else SyncStatus.CREATED


def run(
    *,
    year: int | None = None,
    month: int | None = None,
    path: str | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> SyncStats:
    """Run a board activity sync against the www-board repository.

    Args:
        year (int, optional): Restrict to files matching a 4-digit year prefix.
        month (int, optional): Further restrict to a month. Requires year.
        path (str, optional): Sync only a single repo-relative file path.
        force (bool, optional): Re-parse even when checksums match. Defaults to False.
        dry_run (bool, optional): Skip DB writes. Defaults to False.

    Returns:
        SyncStats: Aggregate status counters.

    """
    stats = SyncStats()

    try:
        tree = fetch_tree()
    except RequestException:
        logger.exception("Failed to fetch git tree for %s/%s", REPO_OWNER, REPO_NAME)
        stats.record(SyncStatus.ERRORED)
        return stats

    for target_path in target_paths(tree, year=year, month=month, path=path):
        blob_sha = tree[target_path]
        try:
            status = sync_file(
                target_path,
                blob_sha,
                force=force,
                dry_run=dry_run,
            )
        except Exception:
            logger.exception("Sync failed for %s", target_path)
            status = SyncStatus.ERRORED

        stats.record(status)
        logger.info("board-activity: %s -> %s", target_path, status)

    return stats

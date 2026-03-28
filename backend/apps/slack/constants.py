"""Slack app constants."""

from apps.common.constants import NL

NEST_BOT_NAME = "NestBot"

OWASP_APPSEC_CHANNEL_ID = "#C0F7D6DFH"
OWASP_ASKOWASP_CHANNEL_ID = "#C04TQ3TAB"
OWASP_CHAPTER_LONDON_CHANNEL_ID = "#C1WAV9UKY"
OWASP_COMMUNITY_CHANNEL_ID = "#C04T40NND"
OWASP_CONTRIBUTE_CHANNEL_ID = "#C04DH8HEPTR"
OWASP_DEVELOPERS_CHANNEL_ID = "#C04V77UNH"
OWASP_DEVSECOPS_CHANNEL_ID = "#C1KF6H39T"
OWASP_GSOC_CHANNEL_ID = "#CFJLZNFN1"
OWASP_JOBS_CHANNEL_ID = "#C0Y12A3FC"
OWASP_LEADERS_CHANNEL_ID = "#C66R5JF6V"
OWASP_MENTORS_CHANNEL_ID = "#C1H191DEE"
OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID = "#C255XSY04"
OWASP_PROJECT_NEST_CHANNEL_ID = "#C07JLLG2GFQ"
OWASP_PROJECT_NETTACKER_CHANNEL_ID = "#CQZGG24FQ"
OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID = "#CURE8PQ68"
OWASP_SPONSORSHIP_CHANNEL_ID = "#C08EGFDD9L2"
OWASP_THREAT_MODELING_CHANNEL_ID = "#C1CS3C6AF"

OWASP_KEYWORDS = {
    "api security",
    "appsec",
    "application security",
    "assessment",
    "authentication",
    "authorization",
    "cheat sheet series",
    "chapter",
    "code review",
    "committee",
    "cryptography",
    "csrf",
    "defectdojo",
    "dependency",
    "devops",
    "devsecops",
    "dynamic analysis",
    "encryption",
    "event",
    "firewall",
    "injection",
    "juice shop",
    "mobile security",
    "nest",
    "nettacker",
    "owasp",
    "penetration",
    "project",
    "rasp",
    "red team",
    "risk",
    "sbom",
    "secure",
    "secure coding",
    "security",
    "security best practice",
    "security bug",
    "security fix",
    "security framework",
    "security guideline",
    "security patch",
    "security policy",
    "security standard",
    "security testing",
    "security tools",
    "static analysis",
    "threat",
    "threat modeling",
    "top 10",
    "top10",
    "vulnerabilities",
    "vulnerability",
    "web security",
    "webgoat",
    "xss",
}

OWASP_WORKSPACE_ID = "T04T40NHX"

VIEW_PROJECTS_ACTION = "view_projects_action"
VIEW_PROJECTS_ACTION_NEXT = "view_projects_action_next"
VIEW_PROJECTS_ACTION_PREV = "view_projects_action_prev"

VIEW_COMMITTEES_ACTION = "view_committees_action"
VIEW_COMMITTEES_ACTION_NEXT = "view_committees_action_next"
VIEW_COMMITTEES_ACTION_PREV = "view_committees_action_prev"

VIEW_CHAPTERS_ACTION = "view_chapters_action"
VIEW_CHAPTERS_ACTION_NEXT = "view_chapters_action_next"
VIEW_CHAPTERS_ACTION_PREV = "view_chapters_action_prev"

VIEW_CONTRIBUTE_ACTION = "view_contribute_action"
VIEW_CONTRIBUTE_ACTION_NEXT = "view_contribute_action_next"
VIEW_CONTRIBUTE_ACTION_PREV = "view_contribute_action_prev"


FEEDBACK_SHARING_INVITE = (
    f"💬 You can share feedback on your {NEST_BOT_NAME} experience "
    f"in the <{OWASP_PROJECT_NEST_CHANNEL_ID}|project-nest> channel.{NL}"
)

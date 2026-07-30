"""Recursive character text splitting (LangChain-compatible behavior).

Implements the same splitting strategy as LangChain's RecursiveCharacterTextSplitter
without requiring the langchain package for chunk embedding workflows.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

logger = logging.getLogger(__name__)


def _split_text_with_regex(
    text: str,
    separator: str,
    *,
    keep_separator: bool | Literal["start", "end"],
) -> list[str]:
    """Split text on a regex separator, optionally keeping the delimiter."""
    if separator:
        if keep_separator:
            _splits = re.split(f"({separator})", text)
            splits = (
                ([_splits[i] + _splits[i + 1] for i in range(0, len(_splits) - 1, 2)])
                if keep_separator == "end"
                else ([_splits[i] + _splits[i + 1] for i in range(1, len(_splits), 2)])
            )
            if len(_splits) % 2 == 0:
                splits += _splits[-1:]
            splits = (
                ([*splits, _splits[-1]]) if keep_separator == "end" else ([_splits[0], *splits])
            )
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]


@dataclass(frozen=True, slots=True)
class _SplitterParams:
    """Parameters for recursive splitting (mirrors LangChain TextSplitter fields)."""

    chunk_size: int
    chunk_overlap: int
    length_function: Callable[[str], int]
    keep_separator: bool | Literal["start", "end"]
    is_separator_regex: bool
    strip_whitespace: bool


def _join_docs(
    docs: list[str],
    separator: str,
    *,
    strip_whitespace: bool,
) -> str | None:
    joined = separator.join(docs)
    if strip_whitespace:
        joined = joined.strip()
    if joined == "":
        return None
    return joined


def _merge_splits(
    splits: Iterable[str],
    separator: str,
    params: _SplitterParams,
) -> list[str]:
    """Combine smaller pieces into chunks up to chunk_size with overlap."""
    separator_len = params.length_function(separator)
    docs: list[str] = []
    current_doc: list[str] = []
    total = 0
    for d in splits:
        part_len = params.length_function(d)
        if total + part_len + (separator_len if len(current_doc) > 0 else 0) > params.chunk_size:
            if total > params.chunk_size:
                logger.warning(
                    "Created a chunk of size %s, which is longer than the specified %s",
                    total,
                    params.chunk_size,
                )
            if len(current_doc) > 0:
                doc = _join_docs(
                    current_doc,
                    separator,
                    strip_whitespace=params.strip_whitespace,
                )
                if doc is not None:
                    docs.append(doc)
                while total > params.chunk_overlap or (
                    total + part_len + (separator_len if len(current_doc) > 0 else 0)
                    > params.chunk_size
                    and total > 0
                ):
                    total -= params.length_function(current_doc[0]) + (
                        separator_len if len(current_doc) > 1 else 0
                    )
                    current_doc = current_doc[1:]
        current_doc.append(d)
        total += part_len + (separator_len if len(current_doc) > 1 else 0)
    doc = _join_docs(current_doc, separator, strip_whitespace=params.strip_whitespace)
    if doc is not None:
        docs.append(doc)
    return docs


def _split_recursive(
    text: str,
    separators: list[str],
    params: _SplitterParams,
) -> list[str]:
    """Recursively split on separators, then merge / recurse for oversized pieces."""
    final_chunks: list[str] = []
    separator = separators[-1]
    new_separators: list[str] = []
    for i, _s in enumerate(separators):
        _sep_pat = _s if params.is_separator_regex else re.escape(_s)
        if _s == "":
            separator = _s
            break
        if re.search(_sep_pat, text):
            separator = _s
            new_separators = separators[i + 1 :]
            break

    _sep = separator if params.is_separator_regex else re.escape(separator)
    splits = _split_text_with_regex(text, _sep, keep_separator=params.keep_separator)

    merge_sep = "" if params.keep_separator else separator
    good_splits: list[str] = []
    for s in splits:
        if params.length_function(s) < params.chunk_size:
            good_splits.append(s)
        else:
            if good_splits:
                final_chunks.extend(_merge_splits(good_splits, merge_sep, params))
                good_splits = []
            if not new_separators:
                final_chunks.append(s)
            else:
                final_chunks.extend(_split_recursive(s, new_separators, params))
    if good_splits:
        final_chunks.extend(_merge_splits(good_splits, merge_sep, params))
    return final_chunks


def split_recursive_character_text(
    text: str,
    *,
    chunk_size: int = 200,
    chunk_overlap: int = 20,
    separators: list[str] | None = None,
    length_function: Callable[[str], int] = len,
    keep_separator: bool | Literal["start", "end"] = True,
    is_separator_regex: bool = False,
    strip_whitespace: bool = True,
) -> list[str]:
    """Split text into chunks using recursive separator splitting and overlap.

    Mirrors LangChain's ``RecursiveCharacterTextSplitter.split_text`` for the same
    parameters used by :meth:`apps.ai.models.chunk.Chunk.split_text`.
    """
    if chunk_size <= 0:
        msg = f"chunk_size must be > 0, got {chunk_size}"
        raise ValueError(msg)
    if chunk_overlap < 0:
        msg = f"chunk_overlap must be >= 0, got {chunk_overlap}"
        raise ValueError(msg)
    if chunk_overlap > chunk_size:
        msg = (
            f"Got a larger chunk overlap ({chunk_overlap}) than chunk size "
            f"({chunk_size}), should be smaller."
        )
        raise ValueError(msg)

    seps = separators if separators is not None else ["\n\n", "\n", " ", ""]
    params = _SplitterParams(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function,
        keep_separator=keep_separator,
        is_separator_regex=is_separator_regex,
        strip_whitespace=strip_whitespace,
    )
    return _split_recursive(text, seps, params)

"""Decide which Markdown source text a reader actually sees rendered.

The output-contract oracle must not accept text a reader never sees: fenced
or indented code, raw HTML blocks, and anything a browser swallows inside a
comment, a raw-text element such as ``<script>``, a ``<template>``, or a
hidden element. Two hand-rolled attempts at this diverged from CommonMark in
both directions (docs/wordpress/oracle-raw-html-stripping-2026-09-27.md), so
this module does no Markdown parsing of its own: block structure comes from
markdown-it-py, and the HTML it emits is read by a small model of the browser
states that display nothing.

``visible_source(text)`` returns the source with every character a reader
cannot see replaced by a space (or its whole line emptied), keeping one output
line per CommonMark source line.
"""

from __future__ import annotations

import functools
import re

try:
    from markdown_it import MarkdownIt
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "markdown-it-py is required by the WordPress output-contract oracle. Run it "
        "through the locked validation environment: `uv sync --locked`, then "
        "`uv run python evals/harness/validate_wordpress_skill_output.py ...` "
        f"({exc})"
    ) from exc


_MARKDOWN = MarkdownIt("commonmark")


def _html_inline_fail_fast(state, silent: bool) -> bool:
    """markdown-it's ``html_inline`` rule, rejecting impossible matches in O(1).

    The stock rule runs its tag regex from every ``<``; on an unclosed ``<!--``
    the comment alternative scans to the end of the paragraph, so a paragraph
    of many unclosed openers costs quadratic time (a 175 KB one took 30 s).
    No alternative of that regex can match without a closer later in the
    source, so the last closer position is computed once per paragraph and a
    ``<`` with no closer after it is rejected before the regex runs. Every
    rejection here is one the stock rule would make too.
    """
    src, pos = state.src, state.pos
    if pos + 2 >= state.posMax or src[pos] != "<":
        return False
    closers = state.env.get("_visibility_closers")
    if closers is None or closers[0] is not src:
        closers = (src, src.rfind("-->"), src.rfind("?>"), src.rfind("]]>"), src.rfind(">"))
        state.env["_visibility_closers"] = closers
    if src.startswith("<!--", pos):
        last = closers[1]
    elif src[pos + 1] == "?":
        last = closers[2]
    elif src.startswith("<![CDATA[", pos):
        last = closers[3]
    else:
        last = closers[4]
    if last < pos:
        return False
    return _STOCK_HTML_INLINE(state, silent)


_STOCK_HTML_INLINE = _MARKDOWN.inline.ruler.__rules__[
    [rule.name for rule in _MARKDOWN.inline.ruler.__rules__].index("html_inline")
].fn
_MARKDOWN.inline.ruler.at("html_inline", _html_inline_fail_fast)

# Python's str.splitlines() breaks on these; CommonMark does not, so they stay
# inside a line and are replaced by spaces in the returned text.
_NON_MARKDOWN_LINE_BREAKS_RE = re.compile("[\x0b\x0c\x1c\x1d\x1e\x85  ]")

# Elements whose content the tokenizer reads as text up to the matching end
# tag. None of it is displayed as document text.
RAW_TEXT_ELEMENTS = frozenset(
    {"script", "style", "xmp", "iframe", "noembed", "noframes", "noscript", "textarea", "title"}
)
VOID_ELEMENTS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "keygen", "link",
     "meta", "param", "source", "track", "wbr"}
)
_HIDING_STYLE_RE = re.compile(
    r"display\s*:\s*none|visibility\s*:\s*hidden|content-visibility\s*:\s*hidden",
    re.IGNORECASE,
)
_TAG_NAME_RE = re.compile(r"[A-Za-z][^\t\n\f\r />]*")
_ATTRIBUTE_RE = re.compile(
    r"""([^\t\n\f\r />"'=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\t\n\f\r >]*)))?"""
)


class BrowserModel:
    """The part of an HTML parser that decides whether emitted text is shown.

    It reads the renderer's HTML as one stream, in document order, and reports
    for each character whether a browser would display it. Content is hidden
    inside comments, bogus comments (``<?``, ``<!x``, ``<![CDATA[`` in HTML
    content, which end at the first ``>``), doctypes, an unterminated tag,
    raw-text elements, ``<plaintext>``, ``<template>``, and any element that is
    ``hidden``, ``display: none``, or a ``<details>`` without ``open``. Tags
    themselves count as shown so the oracle's line rules can still see them.
    Where the tree builder would close an element implicitly, the model keeps
    it open, which hides more, never less.
    """

    def __init__(self) -> None:
        self.buffer = ""
        self.position = 0
        self.state = "data"
        self.construct_start = 0
        self.raw_text_end: re.Pattern[str] | None = None
        self.tag_quote: str | None = None
        self.tag_is_end = False
        self.tag_name = ""
        self.hiding_stack: list[str] = []

    def _hidden_context(self) -> bool:
        return bool(self.hiding_stack)

    def feed(self, html: str) -> list[bool]:
        """Consume ``html`` and return, per character, whether it is hidden."""
        start = len(self.buffer)
        self.buffer += html
        hidden = [False] * len(html)
        while self.position < len(self.buffer):
            before = self.position
            self._step(hidden, start)
            if self.position == before:
                break
        return hidden

    def _mark(self, hidden: list[bool], start: int, begin: int, end: int, value: bool) -> None:
        for index in range(max(begin, start), end):
            hidden[index - start] = value

    def _step(self, hidden: list[bool], start: int) -> None:
        buffer, position = self.buffer, self.position
        if self.state == "plaintext":
            self._mark(hidden, start, position, len(buffer), True)
            self.position = len(buffer)
        elif self.state == "comment":
            ends = [index for index in (buffer.find("-->", position), buffer.find("--!>", position)) if index != -1]
            if ends:
                end = min(ends) + (3 if buffer.startswith("-->", min(ends)) else 4)
                self._mark(hidden, start, position, end, True)
                self.state, self.position = "data", end
            else:
                # Keep the last characters in play: the end string may be split
                # across feeds. feed() stops once a step makes no progress.
                self._mark(hidden, start, position, len(buffer), True)
                self.position = max(self.construct_start, len(buffer) - 3)
        elif self.state == "bogus":
            end = buffer.find(">", position)
            if end == -1:
                self._mark(hidden, start, position, len(buffer), True)
                self.position = len(buffer)
            else:
                self._mark(hidden, start, position, end + 1, True)
                self.state, self.position = "data", end + 1
        elif self.state == "raw_text":
            match = self.raw_text_end.search(buffer, position)
            if match is None:
                self._mark(hidden, start, position, len(buffer), True)
                self.position = max(self.construct_start, len(buffer) - 16)
            else:
                self._mark(hidden, start, position, match.start(), True)
                self.state, self.position = "data", match.start()
        elif self.state == "tag":
            self._step_tag(hidden, start)
        else:
            self._step_data(hidden, start)

    def _step_data(self, hidden: list[bool], start: int) -> None:
        buffer, position = self.buffer, self.position
        opener = buffer.find("<", position)
        text_end = len(buffer) if opener == -1 else opener
        self._mark(hidden, start, position, text_end, self._hidden_context())
        if opener == -1:
            self.position = len(buffer)
            return
        rest = buffer[opener:opener + 10]
        if rest.startswith("<!--"):
            self.construct_start = opener + 4
            if buffer.startswith(">", opener + 4) or buffer.startswith("->", opener + 4):
                end = opener + (5 if buffer.startswith(">", opener + 4) else 6)
                self._mark(hidden, start, opener, end, True)
                self.position = end
                return
            self._mark(hidden, start, opener, opener + 4, True)
            self.state, self.position = "comment", opener + 4
        elif rest.startswith("<!") or rest.startswith("<?"):
            self._mark(hidden, start, opener, opener + 2, True)
            self.state, self.position = "bogus", opener + 2
        elif rest.startswith("</"):
            name = _TAG_NAME_RE.match(buffer, opener + 2)
            if name:
                self._begin_tag(opener, name.group(0), is_end=True)
                self.position = name.end()
            elif buffer.startswith(">", opener + 2):
                self.position = opener + 3
            elif opener + 2 < len(buffer):
                self._mark(hidden, start, opener, opener + 2, True)
                self.state, self.position = "bogus", opener + 2
            else:
                self._mark(hidden, start, opener, opener + 2, self._hidden_context())
                self.position = opener + 2
        else:
            name = _TAG_NAME_RE.match(buffer, opener + 1)
            if name:
                self._begin_tag(opener, name.group(0), is_end=False)
                self.position = name.end()
            else:
                self._mark(hidden, start, opener, opener + 1, self._hidden_context())
                self.position = opener + 1

    def _begin_tag(self, opener: int, name: str, *, is_end: bool) -> None:
        self.state = "tag"
        self.construct_start = opener
        self.tag_is_end = is_end
        self.tag_name = name.lower()
        self.tag_quote = None

    def _step_tag(self, hidden: list[bool], start: int) -> None:
        buffer, position = self.buffer, self.position
        # A tag that began in an earlier feed is swallowing this feed's HTML
        # (an unterminated raw tag reads on until the next ">", which may be
        # the following heading's), so none of these characters are shown.
        swallowed = self.construct_start < start
        index = position
        while index < len(buffer):
            character = buffer[index]
            if self.tag_quote is not None:
                close = buffer.find(self.tag_quote, index)
                if close == -1:
                    index = len(buffer)
                    break
                self.tag_quote = None
                index = close + 1
                continue
            if character == ">":
                self._mark(hidden, start, position, index + 1, swallowed or self._hidden_context())
                self.position = index + 1
                self.state = "data"
                self._finish_tag(buffer[self.construct_start:index + 1])
                return
            if character in "\"'" and buffer[self.construct_start:index].rstrip().endswith("="):
                self.tag_quote = character
            index += 1
        # The tag does not end inside the HTML seen so far: a browser reads
        # everything up to its ``>`` as part of the tag, so none of it shows.
        self._mark(hidden, start, position, len(buffer), True)
        self.position = len(buffer)

    def _finish_tag(self, tag: str) -> None:
        name = self.tag_name
        if self.tag_is_end:
            if name in self.hiding_stack:
                depth = len(self.hiding_stack) - 1 - self.hiding_stack[::-1].index(name)
                # A template end tag inside an element it contains would close
                # the template per the HTML spec; the model keeps it open, which
                # hides more, never less, and matches html5lib's tree.
                if name != "template" or depth == len(self.hiding_stack) - 1:
                    del self.hiding_stack[depth:]
            return
        attributes = {}
        for match in _ATTRIBUTE_RE.finditer(tag, 1 + len(name)):
            value = next((group for group in match.groups()[1:] if group is not None), "")
            attributes.setdefault(match.group(1).lower(), value)
        if name in RAW_TEXT_ELEMENTS:
            self.state = "raw_text"
            self.construct_start = self.position
            self.raw_text_end = re.compile(rf"</{re.escape(name)}[\t\n\f\r />]", re.IGNORECASE)
            return
        if name == "plaintext":
            self.state = "plaintext"
            return
        hides = (
            name == "template"
            or "hidden" in attributes
            or bool(_HIDING_STYLE_RE.search(attributes.get("style", "")))
            or (name == "details" and "open" not in attributes)
        )
        if name in VOID_ELEMENTS:
            return
        if hides or self.hiding_stack:
            self.hiding_stack.append(name)


def _line_breaks(child) -> int:
    if child.type in ("softbreak", "hardbreak"):
        return 1
    return child.content.count("\n")


def normalized_lines(text: str) -> list[str]:
    """Source lines as CommonMark counts them (``\\n``, ``\\r\\n``, or ``\\r``)."""
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


@functools.lru_cache(maxsize=64)
def visible_source(text: str) -> str:
    lines = normalized_lines(text)
    source = "\n".join(lines)
    env: dict = {}
    tokens = _MARKDOWN.parse(source, env)
    model = BrowserModel()
    blank: set[int] = set()
    covered: set[int] = set()
    hidden_columns: dict[int, set[int]] = {}
    renderer, options = _MARKDOWN.renderer, _MARKDOWN.options
    for token in tokens:
        if token.type == "inline":
            covered.update(range(*token.map))
            _read_inline(token, model, lines, blank, hidden_columns, env)
            continue
        mask = model.feed(renderer.render([token], options, env))
        if token.type in ("fence", "code_block", "html_block"):
            covered.update(range(*token.map))
            blank.update(range(*token.map))
        elif token.type == "hr":
            covered.update(range(*token.map))
        elif token.map is not None and token.nesting == 1 and any(mask):
            # The block's own open tag is not shown: it sits inside a hidden
            # element, or an earlier raw construct swallowed it (a bogus
            # comment ends at the first ">", which may be the heading's). The
            # text may still appear, but not as the structure it claims.
            blank.update(range(*token.map))
    output = []
    for index, line in enumerate(lines):
        if index in blank or (index not in covered and line.strip()):
            output.append("")
        elif index in hidden_columns:
            columns = hidden_columns[index]
            output.append("".join(" " if column in columns else character
                                  for column, character in enumerate(line)))
        else:
            output.append(line)
    return _NON_MARKDOWN_LINE_BREAKS_RE.sub(" ", "\n".join(output))


def _read_inline(token, model, lines, blank, hidden_columns, env) -> None:
    """Feed one inline token's children to the model and record hidden text.

    Children carry no source positions, so a child's line is counted from the
    line breaks before it. When that count does not reproduce the token's line
    count (a code span or link title spanning a line break), or a hidden piece
    cannot be located exactly once in its source line, every line it could be
    on is emptied instead.
    """
    first = token.map[0]
    content_lines = token.content.count("\n") + 1
    offset = 0
    hidden_children = []
    renderer, options = _MARKDOWN.renderer, _MARKDOWN.options
    for child in token.children or []:
        html = renderer.renderInline([child], options, env)
        mask = model.feed(html)
        breaks = _line_breaks(child)
        if any(mask):
            hidden_children.append((offset, offset + breaks, child, html, mask))
        offset += breaks
    if not hidden_children:
        return
    if offset != content_lines - 1:
        blank.update(range(first, first + content_lines))
        return
    for begin, end, child, html, mask in hidden_children:
        line_index = first + begin
        if child.type == "html_inline" and begin == end and html == child.content:
            line = lines[line_index]
            if line.count(child.content) == 1:
                column = line.index(child.content)
                hidden_columns.setdefault(line_index, set()).update(
                    column + position for position, is_hidden in enumerate(mask) if is_hidden
                )
                continue
        blank.update(range(first + begin, first + end + 1))

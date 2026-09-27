"""The oracle may count only what a reader sees: checked against real parsers.

``truth(doc)`` renders with markdown-it (CommonMark) and parses the HTML with
html5lib, a browser-grade tree builder. It reports the probes a reader sees:
``## H<n>`` headings as displayed ``<h2>`` elements, and ``R<n>: value``
decision-record lines as displayed, non-code text. The oracle's stripping must
never count a probe the reader cannot see (a hiding vector). It may blank a
probe the reader sees (a false failure) only where its rules are deliberately
stricter than a renderer; on the repository's saved outputs it must not.
"""

from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path

import pytest

import markdown_visibility
import validate_wordpress_skill_output as oracle

html5lib = pytest.importorskip("html5lib")
markdown_it = pytest.importorskip("markdown_it")

ROOT = Path(__file__).resolve().parents[3]
RENDERER = markdown_it.MarkdownIt("commonmark")
NEVER_DISPLAYED = {
    "template", "script", "style", "textarea", "title", "xmp", "iframe",
    "noembed", "noframes", "plaintext", "noscript", "head",
}
HIDING_STYLE_RE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden", re.IGNORECASE)
RECORD_RE = re.compile(r"R\d+:")
H2_RE = re.compile(r"(?m)^ {0,3}##(?!#)[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")


def _element_hidden(element) -> bool:
    tag = element.tag if isinstance(element.tag, str) else None
    if tag is None or tag in NEVER_DISPLAYED or "hidden" in element.attrib:
        return True
    if HIDING_STYLE_RE.search(element.attrib.get("style", "")):
        return True
    return tag == "details" and "open" not in element.attrib


def truth(doc: str) -> set[str]:
    """Probes a reader sees: displayed <h2> headings and displayed record lines.

    Displayed text inside code (a fence, or a raw ``<code>``) counts as seen:
    the oracle may refuse it as non-authoritative, but counting it is not a
    hiding vector.
    """
    tree = html5lib.parse(RENDERER.render(doc), treebuilder="etree", namespaceHTMLElements=False)
    probes: set[str] = set()
    text_lines: list[str] = []

    def walk(element, hidden):
        hidden = hidden or _element_hidden(element)
        if element.tag == "h2" and not hidden:
            probes.add("".join(element.itertext()).strip())
        if not hidden and element.text:
            text_lines.extend(element.text.split("\n"))
        for child in element:
            walk(child, hidden)
            if not hidden and child.tail:
                text_lines.extend(child.tail.split("\n"))

    walk(tree, False)
    # A record inside a multi-line code span is displayed with its line break
    # collapsed to a space, so search displayed text rather than line starts.
    probes.update(match.group(0)[:-1] for match in RECORD_RE.finditer("\n".join(text_lines)))
    return probes


def oracle_probes(doc: str) -> set[str]:
    headings = {h for h in oracle.found_headings(doc) if re.fullmatch(r"H\d+", h)}
    stripped = oracle._strip_non_authoritative_markdown(doc)
    return headings | {m.group(1) for m in re.finditer(r"(?m)^ {0,3}(R\d+):", stripped)}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[`*_\\]", "", text)).strip()


def visible_h2(doc: str) -> set[str]:
    tree = html5lib.parse(RENDERER.render(doc), treebuilder="etree", namespaceHTMLElements=False)
    found: set[str] = set()

    def walk(element, hidden):
        hidden = hidden or _element_hidden(element)
        if element.tag == "h2" and not hidden:
            found.add(_normalize("".join(element.itertext())))
        for child in element:
            walk(child, hidden)

    walk(tree, False)
    return found


def oracle_h2(doc: str) -> set[str]:
    stripped = oracle._strip_non_authoritative_markdown(doc)
    return {_normalize(m.group(1)) for m in H2_RE.finditer(stripped)}


# --- pinned counterexamples -------------------------------------------------
# Every document below was found by adversarial review or differential
# testing of an earlier stripping implementation. "hidden" means a renderer
# plus browser shows no heading; "shown" means they show it.

HIDDEN_HEADING = {
    "comment opened in a list item": "- <!--\n\n## Hidden\n",
    "comment opened in a blockquote": "> <!--\n\n## Hidden\n",
    "comment opened after a div": "<div><!--\n\n## Hidden\n",
    "fence closed by its list item": "- item\n  ```\n<!--\n```\n## Hidden\n-->\n",
    "fence marker inside a div block": "<div>\n```\n\n<!--\n## Hidden\n-->\n",
    "form feed is not a line break": "x\x0c```\n<!--\n```\n## Hidden\n-->\n",
    "escaped backtick and script": "Intro \\` <script> `\n\n## Hidden\n",
    "comment inside pre": "<pre><!--</pre>\n\n## Hidden\n",
    "comment inside code": "<code>\n<!--\n</code>\n\n## Hidden\n",
    "unterminated attribute value": '<div class="\n\n## Hidden\n',
    "hidden attribute": "<div hidden>\n\n## Hidden\n\n</div>\n",
    "display none": '<div style="display:none">\n\n## Hidden\n\n</div>\n',
    "closed details": "<details>\n\n## Hidden\n\n</details>\n",
    "template": "<template>\n\n## Hidden\n\n</template>\n",
    "unfenced line-start php": "<?php\nexit;\n## Hidden\n",
    "raw closing tag then code span": "</style>\n`<!--`\n\n## Hidden\n",
    "raw closing tag then fence": "</textarea>\n````\n\n  <?php\n## Hidden\n",
    "code span tag then fence": "`<script>`\n````\n## Hidden\n\n## Hidden\n",
    "fake fence then real fence": "``` `\n\n```\n## Hidden\n",
    "whole document in comment": "<!--\n## Hidden\n-->\n",
    "whole document in cdata": "<![CDATA[\n## Hidden\n]]>\n",
    "whole document in pi": "<?raw\n## Hidden\n?>\n",
    "script swallows later markdown": "text <script> y\n\n## Hidden\n",
}

SHOWN_HEADING = {
    "php file without closing tag in fence": "```php\n<?php\nexit;\n```\n\n## Shown\n",
    "php in tilde fence": "~~~php\n<?php\nexit;\n~~~\n\n## Shown\n",
    "php inside json string in fence": '```json\n{"data": "<?php\\nexit;\\n"}\n```\n\n## Shown\n',
    "php in indented code": "    <?php\n    exit;\n\n## Shown\n",
    "raw-text element name in code span": "Notes carry `<script>` or `<iframe>` tags.\n\n## Shown\n",
    "unclosed inline comment is text": "Legacy markers look like <!--\n## Shown\nand end with -->\n",
    "unclosed inline php is text": "Files begin with <?php and omit the closer.\n\n## Shown\n",
    "comment closed before fence": "<!--\n```php\n-->\n## Shown\n",
    "escaped backtick, heading interrupts": "Intro \\` <!-- `\n## Shown\n-->\n",
    "hidden div closed before heading": "<div hidden>\n\n</div>\n\n## Shown\n",
    "details open": "<details open>\n\n## Shown\n\n</details>\n",
}

HIDDEN_RECORD = {
    "escaped backtick comment": "Prose \\` <!-- `\nR1: value\n-->\n",
    "code span across lines": "a ` b\n` <!-- `\nR1: value\n-->\n",
    "autolink backtick": "<http://x.y/`> <!-- `\nR1: value\n-->\n",
    "closed inline comment": "Prose <!--\nR1: value\n-->\n",
    "closed inline pi": "Prose <?php\nR1: value\n?>\n",
    "inline script": "Prose <script>\nR1: value\n</script>\n",
    "reference definition title": '[x]: /u "\nR1: value\n"\n',
}


@pytest.mark.parametrize("doc", HIDDEN_HEADING.values(), ids=HIDDEN_HEADING.keys())
def test_heading_a_reader_cannot_see_is_not_counted(doc):
    assert visible_h2(doc) == set(), "fixture error: the renderer shows the heading"
    assert "Hidden" not in oracle.found_headings(doc)


@pytest.mark.parametrize("doc", SHOWN_HEADING.values(), ids=SHOWN_HEADING.keys())
def test_heading_a_reader_sees_is_counted(doc):
    assert visible_h2(doc) == {"Shown"}, "fixture error: the renderer hides the heading"
    assert "Shown" in oracle.found_headings(doc)


@pytest.mark.parametrize("doc", HIDDEN_RECORD.values(), ids=HIDDEN_RECORD.keys())
def test_record_a_reader_cannot_see_is_not_counted(doc):
    assert "R1" not in truth(doc), "fixture error: the renderer shows the record"
    assert "R1" not in oracle_probes(doc)


def test_partially_hidden_line_keeps_its_shown_text():
    # A browser ends a bogus comment at the first ">", so the words after it show.
    stripped = oracle._strip_non_authoritative_markdown("Text <?x a > shown words ?>\n")
    assert "shown words" in stripped
    assert "<?x a >" not in stripped


# --- random differential ----------------------------------------------------

FRAGMENTS = [
    "```", "```php", "~~~", "~~~php", "````", "``` `", "   ```", "    ```", "\t```", "```\t",
    "<?php", "<?php echo 1; ?>", "?>", "  <?php", "    <?php", "text <?php", "text <?php x ?> y",
    '"data": "<?php\\nexit;\\n"',
    "<!--", "-->", "<!-- x -->", "text <!-- x", "text <!-- x --> y", "<!-- a", "b -->",
    "<![CDATA[", "]]>", "<!DOCTYPE html>", "<!X", "text <!X y",
    "<script>", "</script>", "text <script> y", "`<script>`", "``<script>``", "`<!--`", "`<?php`",
    "`a", "b`", "``a", "b``", "\\`<!--`", "<style>", "</style>", "<template>", "</template>",
    "<textarea>", "</textarea>", "<pre>", "</pre>", "text <code> y", "</code>",
    "<div>", "</div>", "<span>x", "text <span> y", "<div hidden>", '<div class="',
    "<details>", "</details>", "[x]: /u \"", '"',
    "plain prose", "prose with `code` span", "    indented code line", "  two-space prose",
    "> quoted", "- list item", "> <!--", "- <?php", "x\x0c```", "\\<!-- y",
]


def random_document(rng: random.Random) -> str:
    parts = []
    probe = 0
    for _ in range(rng.randint(4, 14)):
        roll = rng.random()
        if roll < 0.3:
            parts.append(f"## H{probe}")
            probe += 1
        elif roll < 0.45:
            parts.append(f"R{probe}: value")
            probe += 1
        else:
            parts.append(rng.choice(FRAGMENTS))
        parts.append("\n" if rng.random() < 0.7 else "\n\n")
    parts.append(f"## H{probe}\n")
    return "".join(parts)


def test_random_documents_never_count_a_probe_the_reader_cannot_see():
    rng = random.Random(20260927)
    hiding = []
    for _ in range(2000):
        doc = random_document(rng)
        counted_but_unseen = oracle_probes(doc) - truth(doc)
        if counted_but_unseen:
            hiding.append((doc, sorted(counted_but_unseen)))
    assert hiding == [], f"{len(hiding)} hiding vectors, first: {hiding[0]!r}"


# --- saved outputs ----------------------------------------------------------

def saved_outputs() -> list[Path]:
    paths = [
        path for path in (ROOT / "evidence").rglob("*.md")
        if "/raw/" in str(path)
    ]
    paths += list((ROOT / "evals" / "suites").glob("*-executor/examples/*.md"))
    paths += list((ROOT / "evals" / "handoff").glob("*/packet.md"))
    return sorted(paths)


@pytest.mark.parametrize("path", saved_outputs(), ids=lambda path: str(path.relative_to(ROOT)))
def test_saved_output_headings_match_the_renderer(path):
    doc = path.read_text(encoding="utf-8")
    shown, counted = visible_h2(doc), oracle_h2(doc)
    assert counted - shown == set(), "counted a heading the reader cannot see"
    assert shown - counted == set(), "blanked a heading the reader sees"


# --- runtime ----------------------------------------------------------------

@pytest.mark.parametrize(
    "doc",
    [
        "a <!-- " * 25000,
        "a <? b " * 25000,
        "<!-- x -->\n" * 20000,
        "`" * 50000,
        ("```php\n<?php\n" + "add_action( 'init', 'acme_init' );\n" * 40 + "```\n\n## H\n") * 200,
    ],
    ids=("unclosed-comments", "unclosed-pis", "closed-comment-lines", "backticks", "packet"),
)
def test_pathological_inputs_strip_in_bounded_time(doc):
    markdown_visibility.visible_source.cache_clear()
    started = time.perf_counter()
    oracle.found_headings(doc)
    assert time.perf_counter() - started < 2.0

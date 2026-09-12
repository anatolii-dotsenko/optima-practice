#!/usr/bin/env python3
"""Validate a practice report (.docx) against the machine-readable specification set.

The validator is data-driven: formatting expectations come from ``spec/style-profile.yaml``
and rule metadata (identifier, clause, normative level) from ``spec/dstu-3008-2015.rules.yaml``.
No expectation is hardcoded here except the mapping between a rule and the code that
implements it.

Usage:
    python tools/validate_report.py --docx report.docx --spec spec/
    python tools/validate_report.py --docx report.docx --spec spec/ --format json --strict

Exit codes:
    0 - no errors (warnings may be present)
    1 - at least one error
    2 - invalid invocation or unreadable input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - dependency guard
    sys.exit("Missing dependency: PyYAML. Install with `pip install pyyaml`.")

try:
    from docx import Document
    from docx.shared import Emu
except ImportError:  # pragma: no cover - dependency guard
    sys.exit("Missing dependency: python-docx. Install with `pip install python-docx`.")


# --------------------------------------------------------------------------- #
# Domain model
# --------------------------------------------------------------------------- #

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

EMU_PER_MM = 36000
EMU_PER_CM = 360000

# Ukrainian letters that may designate an appendix (ДСТУ 7.15.1).
APPENDIX_LETTER_CLASS = "АБВГДЕЖИКЛМНПРСТУФХЦШЩЮЯ"


@dataclass(frozen=True)
class Finding:
    """A single validation result tied to a rule identifier."""

    rule_id: str
    clause: str
    severity: str
    message: str
    location: str = ""

    def render(self) -> str:
        where = f" [{self.location}]" if self.location else ""
        return f"{self.severity.upper():7} {self.rule_id} (п. {self.clause}){where}: {self.message}"


@dataclass
class Spec:
    """Loaded specification set."""

    profile: dict[str, Any]
    rules: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, spec_dir: Path) -> "Spec":
        profile = _read_yaml(spec_dir / "style-profile.yaml")
        rule_file = _read_yaml(spec_dir / "dstu-3008-2015.rules.yaml")
        rules = {rule["id"]: rule for rule in rule_file.get("rules", [])}
        if not rules:
            raise ValueError("Rule set is empty or malformed")
        return cls(profile=profile, rules=rules)

    def normative(self, rule_id: str) -> str:
        return self.rules.get(rule_id, {}).get("normative", "MUST")

    def clause(self, rule_id: str) -> str:
        return self.rules.get(rule_id, {}).get("clause", "—")


@dataclass
class DocumentModel:
    """Flattened view of the document that all checks operate on."""

    document: Any
    paragraphs: list[Any] = field(default_factory=list)
    body_text: str = ""

    @classmethod
    def build(cls, path: Path) -> "DocumentModel":
        document = Document(str(path))
        paragraphs = [p for p in document.paragraphs]
        body_text = "\n".join(p.text for p in paragraphs)
        return cls(document=document, paragraphs=paragraphs, body_text=body_text)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Specification file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _emu_to_mm(value: Emu | int | None) -> float | None:
    return None if value is None else round(int(value) / EMU_PER_MM, 2)


def _emu_to_cm(value: Emu | int | None) -> float | None:
    return None if value is None else round(int(value) / EMU_PER_CM, 3)


def _template_to_regex(template: str) -> re.Pattern[str]:
    """Convert a caption template such as ``"Рисунок {n} — {title}"`` into a regex."""
    placeholders = {
        "{n}": rf"(?P<n>\d+(?:\.\d+)?|[{APPENDIX_LETTER_CLASS}]\.\d+)",
        "{letter}": rf"(?P<letter>[{APPENDIX_LETTER_CLASS}])",
        "{title}": r"(?P<title>.+?)",
    }
    pattern = ""
    index = 0
    while index < len(template):
        for token, replacement in placeholders.items():
            if template.startswith(token, index):
                pattern += replacement
                index += len(token)
                break
        else:
            char = template[index]
            pattern += r"\s+" if char == " " else re.escape(char)
            index += 1
    return re.compile(rf"^{pattern}\s*$")


def _is_heading(paragraph: Any) -> bool:
    style_name = (paragraph.style.name or "").lower()
    return style_name.startswith("heading") or style_name.startswith("заголовок")


def _heading_level(paragraph: Any) -> int:
    match = re.search(r"(\d+)$", paragraph.style.name or "")
    return int(match.group(1)) if match else 1


def _resolve_font_name(paragraph: Any, run: Any, document: Any) -> str | None:
    """Resolve the effective font name through run -> paragraph style -> Normal style."""
    if run.font.name:
        return run.font.name
    style = paragraph.style
    while style is not None:
        if style.font.name:
            return style.font.name
        style = style.base_style
    try:
        return document.styles["Normal"].font.name
    except KeyError:
        return None


def _resolve_font_size_pt(paragraph: Any, run: Any, document: Any) -> float | None:
    if run.font.size is not None:
        return run.font.size.pt
    style = paragraph.style
    while style is not None:
        if style.font.size is not None:
            return style.font.size.pt
        style = style.base_style
    try:
        size = document.styles["Normal"].font.size
        return size.pt if size else None
    except KeyError:
        return None


def _resolve_bold(paragraph: Any, run: Any | None = None) -> bool:
    """Resolve the effective bold flag through run -> paragraph style -> base styles."""
    if run is not None and run.font.bold is not None:
        return bool(run.font.bold)
    style = paragraph.style
    while style is not None:
        if style.font.bold is not None:
            return bool(style.font.bold)
        style = style.base_style
    return False


def _numbered_heading(text: str) -> bool:
    return bool(re.match(r"^\d+(\.\d+)*\.?\s+\S", text.strip()))


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

CheckFn = Callable[[DocumentModel, Spec], Iterable[Finding]]
CHECKS: dict[str, CheckFn] = {}


def check(rule_id: str) -> Callable[[CheckFn], CheckFn]:
    """Register a check function under the rule identifier it implements."""

    def decorator(function: CheckFn) -> CheckFn:
        CHECKS[rule_id] = function
        return function

    return decorator


def _finding(spec: Spec, rule_id: str, message: str, location: str = "",
             severity: str | None = None) -> Finding:
    level = spec.normative(rule_id)
    resolved = severity or (SEVERITY_ERROR if level == "MUST" else SEVERITY_WARNING)
    return Finding(rule_id, spec.clause(rule_id), resolved, message, location)


@check("DSTU.7.1.6.page_format")
def check_page_size(model: DocumentModel, spec: Spec) -> list[Finding]:
    page = spec.profile["page"]
    expected = (page["width_mm"], page["height_mm"])
    findings: list[Finding] = []
    for index, section in enumerate(model.document.sections, start=1):
        actual = (_emu_to_mm(section.page_width), _emu_to_mm(section.page_height))
        if any(a is None or abs(a - e) > 1 for a, e in zip(actual, expected)):
            findings.append(_finding(
                spec, "DSTU.7.1.6.page_format",
                f"Page size is {actual[0]}×{actual[1]} mm, expected {expected[0]}×{expected[1]} mm",
                location=f"section {index}",
            ))
    return findings


@check("DSTU.7.1.11.margins")
def check_margins(model: DocumentModel, spec: Spec) -> list[Finding]:
    expected = spec.profile["page"]["margins_mm"]
    findings: list[Finding] = []
    for index, section in enumerate(model.document.sections, start=1):
        actual = {
            "top": _emu_to_mm(section.top_margin),
            "bottom": _emu_to_mm(section.bottom_margin),
            "left": _emu_to_mm(section.left_margin),
            "right": _emu_to_mm(section.right_margin),
        }
        for side, expected_mm in expected.items():
            value = actual.get(side)
            if value is None or abs(value - expected_mm) > 0.5:
                findings.append(_finding(
                    spec, "DSTU.7.1.11.margins",
                    f"{side} margin is {value} mm, expected {expected_mm} mm "
                    f"(resolved profile value; DSTU minimum is a lower bound)",
                    location=f"section {index}",
                    severity=SEVERITY_ERROR,
                ))
    return findings


@check("DSTU.7.1.5.font")
def check_font(model: DocumentModel, spec: Spec) -> list[Finding]:
    typography = spec.profile["typography"]
    expected_family = typography["font_family"]
    expected_size = typography["font_size_pt"]
    small_size = typography.get("small_text", {}).get("font_size_pt")
    low, high = typography["line_spacing_allowed_range"]

    findings: list[Finding] = []
    seen_families: set[str] = set()
    seen_sizes: set[float] = set()
    spacing_offenders: list[str] = []

    for index, paragraph in enumerate(model.paragraphs, start=1):
        if not paragraph.text.strip():
            continue
        for run in paragraph.runs:
            if not run.text.strip():
                continue
            family = _resolve_font_name(paragraph, run, model.document)
            size = _resolve_font_size_pt(paragraph, run, model.document)
            if family and family != expected_family:
                seen_families.add(family)
            if size and size not in (expected_size, small_size):
                seen_sizes.add(size)
            if run.italic and not _is_heading(paragraph):
                findings.append(_finding(
                    spec, "DSTU.7.1.5.font",
                    "Italic typeface in body text; upright is required",
                    location=f"paragraph {index}",
                ))
        spacing = paragraph.paragraph_format.line_spacing
        if isinstance(spacing, (int, float)) and not (low - 1e-6 <= spacing <= high + 1e-6):
            spacing_offenders.append(str(index))

    if seen_families:
        findings.append(_finding(
            spec, "DSTU.7.1.5.font",
            f"Foreign typefaces found: {', '.join(sorted(seen_families))}; expected {expected_family}",
        ))
    if seen_sizes:
        findings.append(_finding(
            spec, "DSTU.7.1.5.font",
            f"Unexpected font sizes: {', '.join(str(s) for s in sorted(seen_sizes))} pt; "
            f"expected {expected_size} pt (or {small_size} pt for notes and footnotes)",
        ))
    if spacing_offenders:
        findings.append(_finding(
            spec, "DSTU.7.1.5.font",
            f"Line spacing outside [{low}; {high}] in paragraphs: "
            f"{', '.join(spacing_offenders[:15])}"
            f"{' …' if len(spacing_offenders) > 15 else ''}",
        ))
    return findings


@check("DSTU.7.1.22.paragraph_indent")
def check_first_line_indent(model: DocumentModel, spec: Spec) -> list[Finding]:
    expected = spec.profile["typography"]["first_line_indent_cm"]
    tolerance = 0.1
    offenders: list[str] = []
    for index, paragraph in enumerate(model.paragraphs, start=1):
        if not paragraph.text.strip() or _is_heading(paragraph):
            continue
        indent = _emu_to_cm(paragraph.paragraph_format.first_line_indent)
        if indent is None:
            continue  # inherited from the style; reported only when explicitly wrong
        if abs(indent - expected) > tolerance:
            offenders.append(f"{index} ({indent} cm)")
    if not offenders:
        return []
    return [_finding(
        spec, "DSTU.7.1.22.paragraph_indent",
        f"First-line indent must be {expected} cm; deviations in paragraphs: "
        f"{', '.join(offenders[:15])}{' …' if len(offenders) > 15 else ''}",
    )]


@check("DSTU.7.1.20.section_heading_style")
def check_section_headings(model: DocumentModel, spec: Spec) -> list[Finding]:
    rules = spec.profile["headings"]["sections"]
    findings: list[Finding] = []
    for index, paragraph in enumerate(model.paragraphs, start=1):
        if not _is_heading(paragraph) or _heading_level(paragraph) != 1:
            continue
        text = paragraph.text.strip()
        if not text:
            continue
        if rules.get("case") == "upper" and text != text.upper():
            findings.append(_finding(
                spec, "DSTU.7.1.20.section_heading_style",
                f"Level-1 heading must be uppercase: {text!r}", location=f"paragraph {index}"))
        runs = [r for r in paragraph.runs if r.text.strip()]
        if rules.get("bold") and not any(_resolve_bold(paragraph, r) for r in runs):
            findings.append(_finding(
                spec, "DSTU.7.1.20.section_heading_style",
                f"Level-1 heading must be bold: {text!r}", location=f"paragraph {index}"))
        if not rules.get("trailing_dot") and text.endswith("."):
            findings.append(_finding(
                spec, "DSTU.7.1.20.section_heading_style",
                f"Level-1 heading must not end with a dot: {text!r}",
                location=f"paragraph {index}"))
    return findings


@check("DSTU.7.1.21.subsection_heading_style")
def check_subsection_headings(model: DocumentModel, spec: Spec) -> list[Finding]:
    findings: list[Finding] = []
    for index, paragraph in enumerate(model.paragraphs, start=1):
        if not _is_heading(paragraph) or _heading_level(paragraph) < 2:
            continue
        text = paragraph.text.strip()
        if text.endswith("."):
            findings.append(_finding(
                spec, "DSTU.7.1.21.subsection_heading_style",
                f"Subsection heading must not end with a dot: {text!r}",
                location=f"paragraph {index}"))
        if text and text == text.upper() and len(text) > 3:
            findings.append(_finding(
                spec, "DSTU.7.1.21.subsection_heading_style",
                f"Subsection heading must be sentence case, not uppercase: {text!r}",
                location=f"paragraph {index}", severity=SEVERITY_WARNING))
    return findings


@check("DSTU.7.1.23.heading_hyphenation")
def check_heading_hyphenation(model: DocumentModel, spec: Spec) -> list[Finding]:
    findings: list[Finding] = []
    for index, paragraph in enumerate(model.paragraphs, start=1):
        if not _is_heading(paragraph):
            continue
        if "\u00ad" in paragraph.text:  # soft hyphen
            findings.append(_finding(
                spec, "DSTU.7.1.23.heading_hyphenation",
                "Heading contains a soft hyphen; hyphenation in headings is forbidden",
                location=f"paragraph {index}"))
    return findings


@check("DSTU.7.1.18.unnumbered_elements")
def check_unnumbered_structural_elements(model: DocumentModel, spec: Spec) -> list[Finding]:
    rule = spec.rules.get("DSTU.7.1.18.unnumbered_elements", {})
    names = {n.upper() for n in rule.get("check", {}).get("headings", [])}
    findings: list[Finding] = []
    for index, paragraph in enumerate(model.paragraphs, start=1):
        text = paragraph.text.strip()
        stripped = re.sub(r"^\d+(\.\d+)*\.?\s+", "", text).upper()
        if stripped in names and _numbered_heading(text):
            findings.append(_finding(
                spec, "DSTU.7.1.18.unnumbered_elements",
                f"Structural element must not be numbered: {text!r}",
                location=f"paragraph {index}"))
    return findings


@check("DSTU.3.5.1.mandatory_elements")
def check_mandatory_sections(model: DocumentModel, spec: Spec) -> list[Finding]:
    required = {
        "РЕФЕРАТ": "abstract",
        "ЗМІСТ": "toc",
        "ВСТУП": "introduction",
        "ВИСНОВКИ": "conclusions",
    }
    upper_text = model.body_text.upper()
    findings = []
    for heading, key in required.items():
        if heading not in upper_text:
            findings.append(_finding(
                spec, "DSTU.3.5.1.mandatory_elements",
                f"Mandatory structural element is missing: {heading} ({key})"))
    return findings


@check("DSTU.4.3.8.keywords")
def check_keywords(model: DocumentModel, spec: Spec) -> list[Finding]:
    """Locate the keyword paragraph inside РЕФЕРАТ and count the entries."""
    abstract_index = next(
        (i for i, p in enumerate(model.paragraphs) if p.text.strip().upper() == "РЕФЕРАТ"),
        None,
    )
    if abstract_index is None:
        return []
    window = model.paragraphs[abstract_index + 1: abstract_index + 12]
    for paragraph in window:
        text = paragraph.text.strip()
        if len(text) < 10 or text != text.upper():
            continue
        keywords = [item.strip() for item in text.rstrip(".").split(",") if item.strip()]
        if len(keywords) < 5 or len(keywords) > 15:
            return [_finding(
                spec, "DSTU.4.3.8.keywords",
                f"Keyword list contains {len(keywords)} entries; 5 to 15 are required")]
        if keywords != sorted(keywords):
            return [_finding(
                spec, "DSTU.4.3.8.keywords",
                "Keywords must be sorted alphabetically", severity=SEVERITY_WARNING)]
        return []
    return [_finding(
        spec, "DSTU.4.3.8.keywords",
        "Uppercase keyword list not found in РЕФЕРАТ")]


def _caption_paragraphs(model: DocumentModel, prefixes: Sequence[str]) -> list[tuple[int, str]]:
    result = []
    for index, paragraph in enumerate(model.paragraphs, start=1):
        text = paragraph.text.strip()
        if any(text.startswith(prefix) for prefix in prefixes):
            result.append((index, text))
    return result


def _check_captions(model: DocumentModel, spec: Spec, rule_id: str, kind: str,
                    prefixes: Sequence[str], template: str,
                    reference_patterns: Sequence[str]) -> list[Finding]:
    pattern = _template_to_regex(template)
    findings: list[Finding] = []
    numbers: list[str] = []

    for index, text in _caption_paragraphs(model, prefixes):
        match = pattern.match(text)
        if not match:
            findings.append(_finding(
                spec, rule_id,
                f"{kind} caption does not match the required format "
                f"{template!r}: {text!r}", location=f"paragraph {index}"))
            continue
        if text.endswith("."):
            findings.append(_finding(
                spec, rule_id, f"{kind} caption must not end with a dot: {text!r}",
                location=f"paragraph {index}"))
        numbers.append(match.group("n"))

    plain = [n for n in numbers if "." not in n]
    expected = [str(i) for i in range(1, len(plain) + 1)]
    if plain and plain != expected:
        findings.append(_finding(
            spec, rule_id,
            f"{kind} numbering is not sequential: found {plain}, expected {expected}"))

    for number in numbers:
        if not any(re.search(p.format(n=re.escape(number)), model.body_text, re.IGNORECASE)
                   for p in reference_patterns):
            findings.append(_finding(
                spec, rule_id,
                f"{kind} {number} is never referenced in the body text",
                severity=SEVERITY_WARNING))
    return findings


@check("DSTU.7.5.1.figure_label")
def check_figure_captions(model: DocumentModel, spec: Spec) -> list[Finding]:
    template = spec.profile["figures"]["caption_template"]
    return _check_captions(
        model, spec, "DSTU.7.5.1.figure_label", "Figure",
        prefixes=("Рисунок", "Рис.", "Рисунку"),
        template=template,
        reference_patterns=(r"рисун\w*\s+{n}\b", r"рис\.\s*{n}\b"),
    )


@check("DSTU.7.6.8.table_caption_position")
def check_table_captions(model: DocumentModel, spec: Spec) -> list[Finding]:
    template = spec.profile["tables"]["caption_template"]
    return _check_captions(
        model, spec, "DSTU.7.6.8.table_caption_position", "Table",
        prefixes=("Таблиця", "Табл."),
        template=template,
        reference_patterns=(r"таблиц\w*\s+{n}\b", r"табл\.\s*{n}\b"),
    )


@check("DSTU.7.15.1.appendix_letters")
def check_appendix_letters(model: DocumentModel, spec: Spec) -> list[Finding]:
    forbidden = set(spec.profile["appendices"]["letters_forbidden"])
    allowed_order = spec.profile["appendices"]["letters_allowed"]
    findings: list[Finding] = []
    used: list[str] = []

    for index, paragraph in enumerate(model.paragraphs, start=1):
        match = re.match(r"^ДОДАТОК\s+([А-ЯҐЄІЇA-Z])\s*$", paragraph.text.strip())
        if not match:
            continue
        letter = match.group(1)
        used.append(letter)
        if letter in forbidden:
            findings.append(_finding(
                spec, "DSTU.7.15.1.appendix_letters",
                f"Letter {letter!r} may not designate an appendix",
                location=f"paragraph {index}"))

    cyrillic = [letter for letter in used if letter in allowed_order]
    expected = allowed_order[: len(cyrillic)]
    if cyrillic and cyrillic != expected:
        findings.append(_finding(
            spec, "DSTU.7.15.1.appendix_letters",
            f"Appendix letters must run consecutively: found {cyrillic}, expected {expected}"))
    return findings


@check("DSTU.5.5.1.reference_order")
def check_reference_order(model: DocumentModel, spec: Spec) -> list[Finding]:
    """Citations must appear in ascending order of first occurrence."""
    citations = [int(n) for n in re.findall(r"\[(\d{1,3})\]", model.body_text)]
    if not citations:
        return [_finding(
            spec, "DSTU.5.5.1.reference_order",
            "No numeric citations of the form [n] were found in the text",
            severity=SEVERITY_WARNING)]

    first_occurrence: list[int] = []
    for number in citations:
        if number not in first_occurrence:
            first_occurrence.append(number)

    findings: list[Finding] = []
    if first_occurrence != sorted(first_occurrence):
        findings.append(_finding(
            spec, "DSTU.5.5.1.reference_order",
            f"Sources must be numbered in order of first mention; "
            f"order of first occurrence is {first_occurrence}"))
    gaps = sorted(set(range(1, max(first_occurrence) + 1)) - set(first_occurrence))
    if gaps:
        findings.append(_finding(
            spec, "DSTU.5.5.1.reference_order",
            f"Sources {gaps} are never cited in the text; the reference list must "
            f"contain only cited sources", severity=SEVERITY_WARNING))
    if first_occurrence and first_occurrence[0] != 1:
        findings.append(_finding(
            spec, "DSTU.5.5.1.reference_order",
            f"The first cited source must be [1], found [{first_occurrence[0]}]"))
    return findings


@check("DSTU.7.3.1.page_numbers")
def check_page_numbering(model: DocumentModel, spec: Spec) -> list[Finding]:
    """Detect a PAGE field in any header of any section."""
    for section in model.document.sections:
        for header in (section.header, section.first_page_header, section.even_page_header):
            if header is None:
                continue
            xml = header._element.xml if hasattr(header, "_element") else ""
            if "PAGE" in xml:
                return []
    return [_finding(
        spec, "DSTU.7.3.1.page_numbers",
        "No PAGE field found in the page headers; page numbers must be placed "
        "in the top right corner")]


@check("DSTU.7.10.6.symbol_legend")
def check_formula_legend(model: DocumentModel, spec: Spec) -> list[Finding]:
    """The legend keyword must not be followed by a colon (ДСТУ 7.10.6)."""
    findings: list[Finding] = []
    for index, paragraph in enumerate(model.paragraphs, start=1):
        text = paragraph.text.strip()
        if re.match(r"^де\s*:", text):
            findings.append(_finding(
                spec, "DSTU.7.10.6.symbol_legend",
                "Symbol legend must start with 'де' without a colon",
                location=f"paragraph {index}"))
    return findings


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

def run_checks(model: DocumentModel, spec: Spec,
               only: Sequence[str] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    for rule_id, function in CHECKS.items():
        if only and rule_id not in only:
            continue
        if rule_id not in spec.rules:
            findings.append(Finding(
                rule_id, "—", SEVERITY_INFO,
                "Check is implemented but the rule is absent from the rule set"))
            continue
        try:
            findings.extend(function(model, spec))
        except Exception as error:  # defensive: one broken check must not abort the run
            findings.append(Finding(
                rule_id, spec.clause(rule_id), SEVERITY_INFO,
                f"Check failed to execute: {error!r}"))
    return findings


def report_unresolved_conflicts(spec: Spec) -> list[Finding]:
    findings = []
    for conflict in spec.profile.get("conflicts", []):
        if conflict.get("owner") == "user":
            continue  # administrative decision, outside the agent's scope
        resolution = conflict.get("resolution", {})
        if resolution.get("requires_human_confirmation"):
            findings.append(Finding(
                conflict["id"], "—", SEVERITY_INFO,
                f"{conflict['topic']}: applied default {resolution.get('default')!r}; "
                "confirm with the supervisor"))
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docx", required=True, type=Path, help="Report file to validate")
    parser.add_argument("--spec", required=True, type=Path, help="Directory with the YAML specs")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    parser.add_argument("--rule", action="append", dest="rules",
                        help="Run only the given rule id (repeatable)")
    args = parser.parse_args(argv)

    if not args.docx.is_file():
        print(f"Report not found: {args.docx}", file=sys.stderr)
        return 2

    try:
        spec = Spec.load(args.spec)
        model = DocumentModel.build(args.docx)
    except (FileNotFoundError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    findings = run_checks(model, spec, only=args.rules)
    findings.extend(report_unresolved_conflicts(spec))

    errors = [f for f in findings if f.severity == SEVERITY_ERROR]
    warnings = [f for f in findings if f.severity == SEVERITY_WARNING]

    if args.format == "json":
        print(json.dumps({
            "document": str(args.docx),
            "summary": {
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(findings) - len(errors) - len(warnings),
            },
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
    else:
        for finding in sorted(findings, key=lambda f: (f.severity, f.rule_id)):
            print(finding.render())
        print(f"\nErrors: {len(errors)}  Warnings: {len(warnings)}  "
              f"Checks executed: {len(CHECKS)}")

    if errors:
        return 1
    return 1 if (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

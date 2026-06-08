#!/usr/bin/env python3
"""CSL file validator with three validation stages.

Usage:
    python validate_csl.py <file.csl>
    python validate_csl.py --verbose <file.csl>

Stages:
    1. XML Syntax check (well-formed, UTF-8)
    2. CSL RelaxNG Schema validation (downloads & caches schema)
    3. Logic rules check (R1-R6)
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

from lxml import etree

# CSL namespace
CSL_NS = "http://purl.org/net/xbiblio/csl"
NS = {"csl": CSL_NS}

# Schema download URLs (raw GitHub content)
# Use v1.0.2 tag for CSL 1.0 files (the vast majority of existing styles)
# Note: The official schema doesn't fully cover all CSL 1.0.2 features
# (e.g., multi-layout with locale attributes). Schema errors for such
# features are expected and should be interpreted with this in mind.
SCHEMA_BRANCHES = {
    "1.0": "v1.0.2",
    "1.1": "master",  # master tracks the upcoming 1.1 spec
}
SCHEMA_BASE_URL_TEMPLATE = "https://raw.githubusercontent.com/citation-style-language/schema/{branch}/schemas/styles"
SCHEMA_FILES = [
    "csl.rnc",
    "csl-categories.rnc",
    "csl-choose.rnc",
    "csl-terms.rnc",
    "csl-types.rnc",
    "csl-variables.rnc",
]

SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = SCRIPT_DIR / "schema"


def log_verbose(msg, verbose=False):
    if verbose:
        print(f"  [verbose] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Stage 1: XML Syntax Check
# ---------------------------------------------------------------------------

def stage1_xml_syntax(filepath, verbose=False):
    """Check well-formed XML and UTF-8 encoding."""
    errors = []

    # Check encoding declaration
    try:
        with open(filepath, "rb") as f:
            raw = f.read(200)
        # Try to detect encoding from XML declaration
        header = raw.decode("ascii", errors="replace")
        if "encoding=" in header.lower():
            match = re.search(r'encoding=["\']([^"\']+)["\']', header, re.IGNORECASE)
            if match:
                declared = match.group(1).lower().replace("-", "")
                if declared not in ("utf8",):
                    errors.append({
                        "rule": "XML",
                        "message": f"Encoding declared as '{match.group(1)}', expected 'utf-8'",
                        "severity": "error",
                    })
        # Try parsing as UTF-8
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
    except UnicodeDecodeError as e:
        errors.append({
            "rule": "XML",
            "message": f"File is not valid UTF-8: {e}",
            "severity": "error",
        })

    # Parse XML
    try:
        parser = etree.XMLParser(recover=False)
        tree = etree.parse(filepath, parser)
        log_verbose("XML parsed successfully", verbose)
    except etree.XMLSyntaxError as e:
        errors.append({
            "rule": "XML",
            "message": f"XML syntax error: {e}",
            "severity": "error",
        })
        return {"stage": 1, "name": "XML Syntax", "passed": len(errors) == 0, "errors": errors}, None

    passed = len(errors) == 0
    return {"stage": 1, "name": "XML Syntax", "passed": passed, "errors": errors}, tree


# ---------------------------------------------------------------------------
# Stage 2: CSL Schema Validation (RelaxNG)
# ---------------------------------------------------------------------------

def _get_schema_dir(version):
    """Return version-specific schema cache directory."""
    branch = SCHEMA_BRANCHES.get(version, SCHEMA_BRANCHES["1.0"])
    return SCHEMA_DIR / branch


def download_schema_files(version="1.0", verbose=False):
    """Download CSL .rnc schema files and cache them locally."""
    branch = SCHEMA_BRANCHES.get(version, SCHEMA_BRANCHES["1.0"])
    base_url = SCHEMA_BASE_URL_TEMPLATE.format(branch=branch)
    schema_dir = _get_schema_dir(version)
    schema_dir.mkdir(parents=True, exist_ok=True)
    log_verbose(f"Schema branch: {branch} (CSL version {version})", verbose)
    for fname in SCHEMA_FILES:
        target = schema_dir / fname
        if target.exists():
            log_verbose(f"Schema file cached: {fname}", verbose)
            continue
        url = f"{base_url}/{fname}"
        log_verbose(f"Downloading {url}", verbose)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CSL-Validator/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            target.write_bytes(data)
            log_verbose(f"Saved {fname} ({len(data)} bytes)", verbose)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            raise RuntimeError(f"Failed to download {fname}: {e}")


def convert_rnc_to_rng(version="1.0", verbose=False):
    """Convert csl.rnc to csl.rng using rnc2rng library. Returns path or None."""
    schema_dir = _get_schema_dir(version)
    rng_path = schema_dir / "csl.rng"
    rnc_path = schema_dir / "csl.rnc"

    if rng_path.exists():
        log_verbose("Using cached csl.rng", verbose)
        return rng_path

    try:
        import rnc2rng
    except ImportError:
        return None

    log_verbose("Converting csl.rnc -> csl.rng via rnc2rng", verbose)
    try:
        # rnc2rng.load() resolves include directives relative to cwd,
        # so we need to change to the schema directory temporarily.
        old_cwd = os.getcwd()
        os.chdir(str(schema_dir))
        try:
            tree = rnc2rng.load(str(rnc_path))
            rng_xml = rnc2rng.dumps(tree)
        finally:
            os.chdir(old_cwd)
        rng_path.write_text(rng_xml, encoding="utf-8")
        log_verbose("Conversion successful", verbose)
        return rng_path
    except Exception as e:
        log_verbose(f"rnc2rng conversion failed: {e}", verbose)
        return None


def stage2_schema_validation(tree, verbose=False):
    """Validate against CSL RelaxNG schema."""
    if tree is None:
        return {
            "stage": 2, "name": "CSL Schema", "passed": False,
            "errors": [{"rule": "Schema", "message": "Skipped: XML parse failed in Stage 1", "severity": "error"}],
            "skipped": True,
        }

    # Detect CSL version from the root element
    root = tree.getroot()
    csl_version = root.get("version", "1.0")
    # Normalize: "1.0" stays "1.0", "1.1" stays "1.1", anything else defaults to "1.0"
    if csl_version not in SCHEMA_BRANCHES:
        log_verbose(f"Unknown CSL version '{csl_version}', defaulting to 1.0 schema", verbose)
        csl_version = "1.0"

    # Download schema files
    try:
        download_schema_files(version=csl_version, verbose=verbose)
    except RuntimeError as e:
        msg = f"Schema download failed: {e}"
        log_verbose(msg, verbose)
        print(f"  WARNING: {msg}", file=sys.stderr)
        return {
            "stage": 2, "name": "CSL Schema", "passed": False,
            "errors": [{"rule": "Schema", "message": msg, "severity": "warning"}],
            "skipped": True,
        }

    # Convert .rnc to .rng
    rng_path = convert_rnc_to_rng(version=csl_version, verbose=verbose)
    if rng_path is None:
        msg = "rnc2rng library not available; cannot convert .rnc to .rng. Install with: pip install rnc2rng"
        log_verbose(msg, verbose)
        print(f"  WARNING: {msg}", file=sys.stderr)
        return {
            "stage": 2, "name": "CSL Schema", "passed": False,
            "errors": [{"rule": "Schema", "message": msg, "severity": "warning"}],
            "skipped": True,
        }

    # Validate
    errors = []
    try:
        rng_doc = etree.parse(str(rng_path))
        rng_schema = etree.RelaxNG(rng_doc)
        valid = rng_schema.validate(tree)
        if not valid:
            for err in rng_schema.error_log:
                errors.append({
                    "rule": "Schema",
                    "message": str(err),
                    "severity": "error",
                })
        log_verbose(f"Schema validation: {'PASS' if valid else 'FAIL'}", verbose)
    except etree.RelaxNGParseError as e:
        msg = f"Failed to parse RelaxNG schema: {e}"
        log_verbose(msg, verbose)
        print(f"  WARNING: {msg}", file=sys.stderr)
        return {
            "stage": 2, "name": "CSL Schema", "passed": False,
            "errors": [{"rule": "Schema", "message": msg, "severity": "warning"}],
            "skipped": True,
        }

    passed = len(errors) == 0
    return {"stage": 2, "name": "CSL Schema", "passed": passed, "errors": errors, "skipped": False}


# ---------------------------------------------------------------------------
# Stage 3: Logic Rules
# ---------------------------------------------------------------------------

def stage3_logic_rules(tree, verbose=False):
    """Custom logic rules R1-R6."""
    if tree is None:
        return {
            "stage": 3, "name": "Logic Rules", "passed": False,
            "errors": [{"rule": "R0", "message": "Skipped: XML parse failed in Stage 1", "severity": "error"}],
        }

    root = tree.getroot()
    errors = []

    # ---- R1: Structure completeness ----
    _check_r1(root, errors, verbose)

    # ---- R2: Macro reference integrity ----
    _check_r2(root, errors, verbose)

    # ---- R3: Class consistency ----
    _check_r3(root, errors, verbose)

    # ---- R4: et-al parameter validity ----
    _check_r4(root, errors, verbose)

    # ---- R5: Bilingual layout ordering ----
    _check_r5(root, errors, verbose)

    # ---- R6: No residual placeholders or empty macros ----
    _check_r6(root, errors, verbose)

    has_error = any(e["severity"] == "error" for e in errors)
    return {"stage": 3, "name": "Logic Rules", "passed": not has_error, "errors": errors}


def _check_r1(root, errors, verbose):
    """R1: Structural completeness."""
    # style must have class and version
    style_class = root.get("class")
    style_version = root.get("version")
    if not style_class:
        errors.append({"rule": "R1", "message": "<style> missing 'class' attribute", "severity": "error"})
    if not style_version:
        errors.append({"rule": "R1", "message": "<style> missing 'version' attribute", "severity": "error"})

    # info must have title, id, updated
    info = root.find("csl:info", NS)
    if info is None:
        errors.append({"rule": "R1", "message": "<info> element not found", "severity": "error"})
    else:
        for tag in ("title", "id", "updated"):
            el = info.find(f"csl:{tag}", NS)
            if el is None or not (el.text and el.text.strip()):
                errors.append({"rule": "R1", "message": f"<info> missing or empty <{tag}>", "severity": "error"})

    # citation must exist with layout
    citation = root.find("csl:citation", NS)
    if citation is None:
        errors.append({"rule": "R1", "message": "<citation> element not found", "severity": "error"})
    else:
        layouts = citation.findall("csl:layout", NS)
        if not layouts:
            errors.append({"rule": "R1", "message": "<citation> has no <layout> child", "severity": "error"})

    log_verbose(f"R1: {len([e for e in errors if e['rule'] == 'R1'])} issues", verbose)


def _check_r2(root, errors, verbose):
    """R2: Macro reference integrity."""
    # Collect defined macros
    defined = set()
    for macro in root.findall("csl:macro", NS):
        name = macro.get("name")
        if name:
            defined.add(name)

    # Collect referenced macros (text[@macro] anywhere in the tree)
    referenced = set()
    for el in root.iter(f"{{{CSL_NS}}}text"):
        macro_ref = el.get("macro")
        if macro_ref:
            referenced.add(macro_ref)

    # Also check <names> with <substitute> -> <names> pattern is ok, but
    # text[@macro] in any element
    for el in root.iter():
        macro_ref = el.get("macro")
        if macro_ref and el.tag == f"{{{CSL_NS}}}text":
            referenced.add(macro_ref)

    # Referenced but not defined -> error
    for name in sorted(referenced - defined):
        errors.append({
            "rule": "R2",
            "message": f"Macro '{name}' referenced but not defined",
            "severity": "error",
        })

    # Defined but never referenced -> warning
    for name in sorted(defined - referenced):
        errors.append({
            "rule": "R2",
            "message": f"Macro '{name}' defined but never referenced",
            "severity": "warning",
        })

    log_verbose(f"R2: defined={len(defined)}, referenced={len(referenced)}", verbose)


def _check_r3(root, errors, verbose):
    """R3: Class consistency — citation-format should match class."""
    style_class = root.get("class")
    if not style_class:
        return

    # Find citation-format from <category citation-format="..."/>
    citation_format = None
    for cat in root.iter(f"{{{CSL_NS}}}category"):
        cf = cat.get("citation-format")
        if cf:
            citation_format = cf
            break

    if citation_format is None:
        log_verbose("R3: No citation-format category found, skipping", verbose)
        return

    if style_class == "in-text":
        valid_formats = ("numeric", "author-date", "author", "label")
        if citation_format not in valid_formats:
            errors.append({
                "rule": "R3",
                "message": f"class='in-text' but citation-format='{citation_format}' "
                           f"(expected one of: {', '.join(valid_formats)})",
                "severity": "error",
            })
    elif style_class == "note":
        if citation_format != "note":
            errors.append({
                "rule": "R3",
                "message": f"class='note' but citation-format='{citation_format}' (expected 'note')",
                "severity": "error",
            })

    log_verbose(f"R3: class={style_class}, citation-format={citation_format}", verbose)


def _check_r4(root, errors, verbose):
    """R4: et-al-min > et-al-use-first for all <name> elements and inherited attributes."""
    count = 0

    # Gather elements that can carry et-al-min / et-al-use-first:
    # <name>, <style>, <citation>, <bibliography>
    targets = []
    for tag in ("name", "style", "citation", "bibliography"):
        for el in root.iter(f"{{{CSL_NS}}}{tag}"):
            targets.append((tag, el))

    for tag, el in targets:
        ea_min_str = el.get("et-al-min")
        ea_first_str = el.get("et-al-use-first")

        if ea_min_str is not None and ea_first_str is not None:
            try:
                ea_min = int(ea_min_str)
                ea_first = int(ea_first_str)
            except ValueError:
                errors.append({
                    "rule": "R4",
                    "message": f"<{tag}> has non-integer et-al-min='{ea_min_str}' or et-al-use-first='{ea_first_str}'",
                    "severity": "error",
                })
                continue

            if ea_min <= ea_first:
                errors.append({
                    "rule": "R4",
                    "message": f"<{tag}> has et-al-min={ea_min} <= et-al-use-first={ea_first} "
                               f"(et-al-min must be greater)",
                    "severity": "error",
                })
            count += 1

    log_verbose(f"R4: checked {count} elements with et-al attributes", verbose)


def _check_r5(root, errors, verbose):
    """R5: Bilingual layout ordering — layouts with locale attribute should come before those without."""
    for parent_tag in ("citation", "bibliography"):
        parent = root.find(f"csl:{parent_tag}", NS)
        if parent is None:
            continue

        layouts = parent.findall("csl:layout", NS)
        if len(layouts) <= 1:
            continue

        # Check ordering: locale-specific layouts should precede the generic one
        found_generic = False
        for layout in layouts:
            has_locale = layout.get("locale") is not None
            if not has_locale:
                found_generic = True
            elif found_generic:
                # A locale-specific layout appears after a generic one
                locale_val = layout.get("locale", "")
                errors.append({
                    "rule": "R5",
                    "message": f"In <{parent_tag}>: layout with locale='{locale_val}' "
                               f"appears after a layout without locale attribute "
                               f"(locale-specific layouts should come first)",
                    "severity": "warning",
                })

    log_verbose("R5: layout ordering checked", verbose)


def _check_r6(root, errors, verbose):
    """R6: No residual placeholders or empty macros."""
    # Check for placeholder text patterns like [占位符], [placeholder], [TODO], etc.
    placeholder_pattern = re.compile(r"\[.*?占位.*?\]|\[placeholder\]|\[TODO\]|\[FIXME\]|\[TBD\]", re.IGNORECASE)

    for el in root.iter():
        if not isinstance(el.tag, str):
            continue  # skip comments and processing instructions
        tag_local = etree.QName(el.tag).localname
        # Check text content
        if el.text:
            matches = placeholder_pattern.findall(el.text)
            for m in matches:
                errors.append({
                    "rule": "R6",
                    "message": f"Residual placeholder text found: '{m}' in <{tag_local}>",
                    "severity": "error",
                })
        # Check attribute values
        for attr_name, attr_val in el.attrib.items():
            matches = placeholder_pattern.findall(attr_val)
            for m in matches:
                errors.append({
                    "rule": "R6",
                    "message": f"Residual placeholder in attribute {attr_name}='{attr_val}' of <{tag_local}>",
                    "severity": "error",
                })
        # Check tail text
        if el.tail:
            matches = placeholder_pattern.findall(el.tail)
            for m in matches:
                errors.append({
                    "rule": "R6",
                    "message": f"Residual placeholder text found in tail: '{m}'",
                    "severity": "error",
                })

    # Check for empty macros (macros with no child elements)
    for macro in root.findall("csl:macro", NS):
        name = macro.get("name", "(unnamed)")
        if len(macro) == 0:
            # No child elements at all
            errors.append({
                "rule": "R6",
                "message": f"Empty macro '{name}' (no child elements)",
                "severity": "error",
            })

    log_verbose("R6: placeholder and empty macro check done", verbose)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_csl(filepath, verbose=False):
    """Run all validation stages and return the result dict."""
    filepath = str(Path(filepath).resolve())

    if not os.path.isfile(filepath):
        return {
            "file": filepath,
            "stages": [],
            "overall": "FAIL",
            "error": f"File not found: {filepath}",
        }

    stages = []

    # Stage 1
    if verbose:
        print("Stage 1: XML Syntax Check...", file=sys.stderr)
    s1_result, tree = stage1_xml_syntax(filepath, verbose)
    stages.append(s1_result)

    # Stage 2
    if verbose:
        print("Stage 2: CSL Schema Validation...", file=sys.stderr)
    s2_result = stage2_schema_validation(tree, verbose)
    stages.append(s2_result)

    # Stage 3
    if verbose:
        print("Stage 3: Logic Rules Check...", file=sys.stderr)
    s3_result = stage3_logic_rules(tree, verbose)
    stages.append(s3_result)

    # Determine overall result
    all_errors = []
    for s in stages:
        all_errors.extend(s.get("errors", []))

    has_error = any(e["severity"] == "error" for e in all_errors)
    has_warning = any(e["severity"] == "warning" for e in all_errors)

    # Skipped stages don't count as errors for overall if they only have warnings
    skipped_only_warnings = True
    for s in stages:
        if s.get("skipped"):
            if any(e["severity"] == "error" for e in s.get("errors", [])):
                skipped_only_warnings = False

    # Recalculate has_error excluding skipped-stage warnings
    real_errors = []
    for s in stages:
        if s.get("skipped"):
            continue
        real_errors.extend(e for e in s.get("errors", []) if e["severity"] == "error")

    real_warnings = []
    for s in stages:
        if s.get("skipped"):
            # Skipped stage warnings are informational
            real_warnings.extend(e for e in s.get("errors", []) if e["severity"] == "warning")
        else:
            real_warnings.extend(e for e in s.get("errors", []) if e["severity"] == "warning")

    if real_errors:
        overall = "FAIL"
    elif real_warnings:
        overall = "WARN"
    else:
        overall = "PASS"

    return {
        "file": filepath,
        "stages": stages,
        "overall": overall,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate a CSL (Citation Style Language) file.",
        epilog="Example: python validate_csl.py --verbose style.csl",
    )
    parser.add_argument("file", help="Path to the CSL file to validate")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed progress on stderr")
    args = parser.parse_args()

    result = validate_csl(args.file, verbose=args.verbose)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Exit code
    if result["overall"] == "FAIL":
        sys.exit(1)
    elif result["overall"] == "WARN":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

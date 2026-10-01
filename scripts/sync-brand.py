#!/usr/bin/env python3
"""Generate the brand CSS and browser manifest, or check them without writing.

Requires Python >= 3.9, with no third-party dependencies.
Run from any directory: python3 /path/to/couli/scripts/sync-brand.py [--check]
Inputs are declared in brand.config.json; all paths stay inside this repository.
"""

import argparse
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "brand.config.json"
SEGMENT = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HEX_COLOR = re.compile(r"#[0-9A-F]{6}\Z")
REQUIRED_ASSETS = frozenset({
    "logoMark", "logoHorizontal", "logoVertical", "logoMono", "logoInverse",
    "logoHorizontalInverse", "logoVerticalInverse", "iconDefault", "iconDark",
    "iconTinted", "iconPng", "iconForeground", "iconBackground", "iconMonochrome",
})
REQUIRED_SEMANTICS = frozenset({
    "brandPrimary", "brandEmphasis", "canvas", "surface", "textPrimary",
    "textSecondary", "link", "price", "pendingText", "pendingBackground",
    "successText", "successBackground", "warningText", "warningBackground",
    "errorText", "errorBackground", "primaryAction", "primaryActionText",
    "controlBorder", "focusRing",
})


class BrandError(ValueError):
    """A source or configuration is invalid; no outputs should be written."""


def require(condition, message):
    if not condition:
        raise BrandError(message)


def object_value(value, label):
    require(isinstance(value, dict), f"{label}: expected an object")
    return value


def require_keys(value, required, label):
    missing = required - value.keys()
    require(not missing, f"{label}: missing required keys: {', '.join(sorted(missing))}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"JSON contains duplicate key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise BrandError(f"JSON contains non-finite number: {value}")


def read_json(path):
    return object_value(
        json.loads(path.read_text(encoding="utf-8"),
                   object_pairs_hook=unique_object, parse_constant=reject_constant),
        str(path.relative_to(ROOT)),
    )


def repo_path(value, label, must_exist=True):
    require(isinstance(value, str) and value, f"{label}: expected a relative path")
    relative = PurePosixPath(value)
    require(not relative.is_absolute() and "\\" not in value and "\0" not in value,
            f"{label}: use a repository-relative POSIX path")
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f"{label}: path escapes repository: {value}")
    if must_exist:
        require(path.is_file(), f"{label}: file does not exist: {value}")
    else:
        require(not path.exists() or path.is_file(), f"{label}: output is not a file")
        require(path.parent.is_dir(), f"{label}: parent directory does not exist")
    return path


def number(value, label, minimum=None, maximum=None, positive=False):
    require(type(value) in (int, float), f"{label}: expected a number, not a boolean")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    require(finite, f"{label}: number must be finite")
    require(minimum is None or value >= minimum, f"{label}: must be >= {minimum}")
    require(maximum is None or value <= maximum, f"{label}: must be <= {maximum}")
    require(not positive or value > 0, f"{label}: must be positive")
    return value


def numeric_text(value):
    # Keep integers and current fractional values stable without exponent notation.
    text = str(value)
    if "e" in text.lower():
        from decimal import Decimal
        text = format(Decimal(text), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def color(value, label):
    require(isinstance(value, str) and HEX_COLOR.fullmatch(value) is not None,
            f"{label}: expected uppercase #RRGGBB sRGB color")
    return value


def convert_token(token, path, font_base):
    kind = token["type"]
    value = token["value"]
    if kind == "color":
        return color(value, path)
    if kind in ("dimension", "fontSize"):
        require(token.get("unit") == "logical", f"{path}: expected unit=logical")
        value = number(value, path, minimum=0, positive=kind == "fontSize")
        if kind == "fontSize":
            value = number(value / font_base, path + " / cssFontBase", positive=True)
            return numeric_text(value) + "rem"
        return numeric_text(value) + "px"
    if kind == "lineHeight":
        return numeric_text(number(value, path, positive=True))
    if kind == "fontWeight":
        return numeric_text(number(value, path, minimum=1, maximum=1000))
    if kind == "fontFamily":
        require(isinstance(value, list) and value, f"{path}: expected font family list")
        families = []
        for family in value:
            require(isinstance(family, str) and family and
                    all(ord(char) >= 32 and ord(char) != 127 for char in family),
                    f"{path}: invalid font family")
            if re.fullmatch(r"-?[A-Za-z_][A-Za-z0-9_-]*", family):
                families.append(family)
            else:
                escaped = family.replace("\\", "\\\\").replace('"', '\\"')
                families.append('"' + escaped + '"')
        return ", ".join(families)
    if kind == "shadow":
        require(isinstance(value, list), f"{path}: expected shadow array")
        shadows = []
        for index, shadow in enumerate(value):
            label = f"{path}[{index}]"
            object_value(shadow, label)
            require(set(shadow) == {"x", "y", "blur", "spread", "color", "opacity"},
                    f"{label}: expected x/y/blur/spread/color/opacity")
            dimensions = []
            for key in ("x", "y", "blur", "spread"):
                length = number(shadow[key], label + "." + key,
                                minimum=0 if key == "blur" else None)
                dimensions.append(numeric_text(length) + "px")
            shade = color(shadow["color"], label + ".color")
            rgb = ", ".join(str(int(shade[i:i + 2], 16)) for i in (1, 3, 5))
            opacity = numeric_text(number(shadow["opacity"], label + ".opacity", 0, 1))
            shadows.append(" ".join(dimensions) + f" rgba({rgb}, {opacity})")
        return ", ".join(shadows) if shadows else "none"
    raise BrandError(f"{path}: unsupported token type: {kind!r}")


def flatten_tokens(tree, font_base):
    tokens, variables = {}, {}

    def walk(node, segments):
        path = ".".join(segments)
        object_value(node, path or "tokens")
        if "type" in node or "value" in node:
            require(segments and "type" in node and "value" in node,
                    f"{path}: token needs both type and value")
            variable = "--" + "-".join(segments)
            require(variable not in variables, f"duplicate CSS variable: {variable}")
            variables[variable] = convert_token(node, path, font_base)
            tokens[path] = (node, variable)
            return
        require(node, f"{path or 'tokens'}: empty token group")
        for segment, child in node.items():
            require(SEGMENT.fullmatch(segment) is not None,
                    f"{path}: invalid token path segment: {segment!r}")
            walk(child, segments + [segment])

    walk(tree, [])
    return tokens, variables


def relative_url(target, entry):
    return quote(Path(os.path.relpath(target, entry.parent)).as_posix(), safe="/.-_")


def validate_entry_links(entry, css_output, js_output):
    class EntryLinks(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stylesheets = []
            self.scripts = []
            self.base_href = None
            self.inert_depth = 0

        def handle_starttag(self, tag, attributes):
            attributes = dict(attributes)
            if tag in ("template", "noscript"):
                self.inert_depth += 1
            if self.inert_depth:
                return
            if tag == "base" and "href" in attributes:
                self.base_href = attributes["href"]
            if tag == "link" and "stylesheet" in (attributes.get("rel") or "").lower().split():
                if "disabled" not in attributes:
                    self.stylesheets.append(attributes.get("href"))
            if tag == "script":
                self.scripts.append(attributes.get("src"))

        def handle_endtag(self, tag):
            if tag in ("template", "noscript") and self.inert_depth:
                self.inert_depth -= 1

    links = EntryLinks()
    links.feed(entry.read_text(encoding="utf-8"))
    links.close()
    require(links.base_href is None,
            "preview.entry: <base href> is not supported; brand URLs are relative to the entry HTML")

    def points_to(url, target):
        if not isinstance(url, str):
            return False
        parsed = urlsplit(url.strip())
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
            return False
        relative = unquote(parsed.path)
        if PurePosixPath(relative).is_absolute() or "\\" in relative:
            return False
        path = (entry.parent / relative).resolve()
        return path.is_relative_to(ROOT) and path == target

    for label, urls, target, tag in (
        ("tokens.css", links.stylesheets, css_output, 'link rel="stylesheet" href'),
        ("preview.browserConfig", links.scripts, js_output, "script src"),
    ):
        expected = relative_url(target, entry)
        require(any(points_to(url, target) for url in urls),
                f'{label}: {entry.relative_to(ROOT)} must load {tag}="{expected}" '
                "(or a relative URL resolving to the same repository file)")


def build_outputs():
    config = read_json(repo_path("brand.config.json", "brand.config"))
    require(config.get("schemaVersion") == "couli.brand.v1", "unsupported brand schema")
    identity = object_value(config.get("identity"), "identity")
    require_keys(identity, {"name", "projectId", "englishName", "tagline"}, "identity")
    for field in ("name", "projectId"):
        require(isinstance(identity[field], str) and identity[field].strip(),
                f"identity.{field}: expected a non-empty string")
    for field in ("englishName", "tagline"):
        require(identity[field] is None or isinstance(identity[field], str),
                f"identity.{field}: expected null or a string")
    asset_config = object_value(config.get("assets"), "assets")
    require_keys(asset_config, REQUIRED_ASSETS, "assets")
    assets = {role: repo_path(value, f"assets.{role}") for role, value in asset_config.items()}
    token_config = object_value(config.get("tokens"), "tokens")
    source = repo_path(token_config.get("source"), "tokens.source")
    foundations = repo_path(token_config.get("foundations"), "tokens.foundations")
    css_output = repo_path(token_config.get("css"), "tokens.css", must_exist=False)
    preview = object_value(config.get("preview"), "preview")
    entry = repo_path(preview.get("entry"), "preview.entry")
    js_output = repo_path(preview.get("browserConfig"), "preview.browserConfig", must_exist=False)
    # Documentation is not a generation input, but every declared file must exist locally.
    documentation = object_value(config.get("documentation", {}), "documentation")
    docs = [repo_path(value, f"documentation.{role}", must_exist=True)
            for role, value in documentation.items()]
    inputs = {CONFIG, Path(__file__).resolve(), source, foundations, entry, *assets.values(), *docs}
    require(css_output != js_output, "CSS and browser config outputs must be distinct")
    require(css_output not in inputs and js_output not in inputs,
            "generated outputs must not overwrite an input or documented source")
    validate_entry_links(entry, css_output, js_output)

    data = read_json(source)
    require(data.get("schemaVersion") == "couli.tokens.v1", "unsupported token schema")
    metadata = object_value(data.get("metadata"), "metadata")
    require(metadata.get("theme") == "light", "this baseline only supports metadata.theme=light")
    require(metadata.get("name") == identity["name"], "identity.name and metadata.name disagree")
    font_base = number(metadata.get("cssFontBase"), "metadata.cssFontBase", positive=True)
    tokens, variables = flatten_tokens(data.get("tokens"), font_base)

    semantics = {}
    aliases = object_value(config.get("semantics"), "semantics")
    require_keys(aliases, REQUIRED_SEMANTICS, "semantics")
    for role, path in aliases.items():
        require(isinstance(path, str) and path in tokens,
                f"semantics.{role}: unknown token alias: {path!r}")
        token, variable = tokens[path]
        require(token["type"] == "color", f"semantics.{role}: alias must target a color token")
        semantics[role] = {"token": path, "cssVariable": variable, "value": token["value"]}

    foundation_text = foundations.read_text(encoding="utf-8")
    require(bool(foundation_text.strip()), "foundations template is empty")
    used_variables = set(re.findall(r"var\(\s*(--[A-Za-z0-9_-]+)", foundation_text))
    require(used_variables <= variables.keys(),
            "foundations references unknown variables: " + ", ".join(sorted(used_variables - variables.keys())))
    declarations = "\n".join(f"  {key}: {value};" for key, value in variables.items())
    css = ("/* AUTO-GENERATED by scripts/sync-brand.py; do not edit.\n"
           " * Sources: brand.config.json, canonical tokens JSON, foundations.css. */\n"
           ":root {\n  color-scheme: only light;\n" + declarations + "\n}\n\n" + foundation_text)
    if not css.endswith("\n"):
        css += "\n"
    browser = {
        "schemaVersion": config["schemaVersion"],
        "identity": identity,
        "metadata": metadata,
        "assets": {role: relative_url(path, entry) for role, path in assets.items()},
        "tokens": {"source": relative_url(source, entry), "css": relative_url(css_output, entry)},
        "semantics": semantics,
    }
    payload = json.dumps(browser, ensure_ascii=False, indent=2, allow_nan=False)
    payload = payload.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    js = ("/* AUTO-GENERATED by scripts/sync-brand.py; do not edit. */\n"
          "window.COULI_BRAND = Object.freeze(" + payload + ");\n")
    return {css_output: css, js_output: js}, len(tokens), len(assets), len(semantics)


def write_outputs(outputs):
    # Stage every already-validated output before replacing any destination.
    staged = []
    try:
        for path, content in outputs.items():
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=path.parent, prefix=".sync-brand-", delete=False) as handle:
                temporary = Path(handle.name)
                staged.append((temporary, path))
                handle.write(content)
            temporary.chmod(path.stat().st_mode & 0o777 if path.exists() else 0o644)
        for temporary, path in staged:
            temporary.replace(path)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def main():
    if sys.version_info < (3, 9):
        print("ERROR: scripts/sync-brand.py requires Python >= 3.9.", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="read-only generated-output drift check")
    args = parser.parse_args()
    try:
        outputs, count, asset_count, alias_count = build_outputs()
        if args.check:
            drift = [path for path, content in outputs.items()
                     if not path.is_file() or path.read_bytes() != content.encode("utf-8")]
            if drift:
                for path in drift:
                    print(f"DRIFT {path.relative_to(ROOT)}", file=sys.stderr)
                print("Run python3 scripts/sync-brand.py to regenerate.", file=sys.stderr)
                return 1
            print(f"PASS: {count} tokens, {asset_count} assets, {alias_count} aliases; 2 generated files match.")
        else:
            write_outputs(outputs)
            print(f"Generated 2 files from {count} tokens, {asset_count} assets, {alias_count} aliases.")
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

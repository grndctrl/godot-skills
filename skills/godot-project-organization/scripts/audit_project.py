#!/usr/bin/env python3
"""Audit a Godot 4 project against the Function First conventions.

Read-only: reports problems, never changes files.

Usage:
    python3 audit_project.py [path-to-godot-project]

Checks:
    1. Names on disk are snake_case (folders and files), with no spaces.
    2. No file-type folders at the top level (scripts/, scenes/, textures/, ...).
    3. common/ purity: no references to game code (res:// paths outside
       common/ and addons/, game class_names, or game autoloads).

Exit code: 0 if no errors, 1 if errors were found, 2 on bad usage.
"""

import re
import sys
from pathlib import Path

SKIP_DIRS = {".godot", ".git", ".import", ".vscode", ".idea", "addons", "android", "build", "export", "exports"}
SKIP_FILE_SUFFIXES = {".import", ".uid", ".tmp"}
# Root-level files that conventionally aren't snake_case.
ROOT_FILE_ALLOWLIST = re.compile(r"^(README|LICENSE|LICENCE|CHANGELOG|CONTRIBUTING|AUTHORS|NOTICE)(\..*)?$", re.I)

EXPECTED_TOP_LEVEL = {"addons", "assets", "common", "config", "entities", "localization", "stages", "ui", "utilities"}
FILE_TYPE_FOLDERS = {
    "scripts", "script", "scenes", "scene", "textures", "texture", "sprites", "images", "img",
    "sounds", "sfx", "music", "materials", "shaders", "models", "meshes", "prefabs",
    "resources", "src", "art", "animations", "fonts", "audio",
}

SNAKE_DIR = re.compile(r"^[a-z0-9_]+$")
SNAKE_FILE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")
CLASS_NAME = re.compile(r"^\s*class_name\s+([A-Za-z_]\w*)", re.M)
RES_PATH = re.compile(r"[\"'](res://[^\"'\n]+)[\"']")
AUTOLOAD_LINE = re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*"\*?(res://[^"]+)"')


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_skipped(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(p in SKIP_DIRS or p.startswith(".") for p in parts)


def check_names(root: Path):
    errors, warnings = [], []
    for path in sorted(root.rglob("*")):
        if is_skipped(path, root):
            continue
        name = path.name
        where = rel(path, root)
        if path.is_file():
            if path.suffix in SKIP_FILE_SUFFIXES or path.suffix == ".cs":
                continue  # sidecars follow their source; C# uses PascalCase by convention
            if path.parent == root and ROOT_FILE_ALLOWLIST.match(name):
                continue
        if " " in name:
            errors.append(f"space in name: {where}")
        elif not (SNAKE_DIR if path.is_dir() else SNAKE_FILE).match(name):
            warnings.append(f"not snake_case: {where}")
    return errors, warnings


def check_top_level(root: Path):
    warnings, info = [], []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        key = d.name.lower()
        if key in FILE_TYPE_FOLDERS:
            warnings.append(f"file-type folder at top level: {d.name}/ (group by in-game function instead)")
        elif key not in EXPECTED_TOP_LEVEL:
            info.append(f"non-standard top-level folder: {d.name}/")
    return warnings, info


def find_dir(root: Path, name: str):
    for p in root.iterdir():
        if p.is_dir() and p.name.lower() == name:
            return p
    return None


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def check_common_purity(root: Path):
    common = find_dir(root, "common")
    if common is None:
        return [], ["no common/ folder found; purity check skipped"]
    addons = find_dir(root, "addons")
    allowed_prefixes = [f"res://{common.name}/"] + ([f"res://{addons.name}/"] if addons else [])

    def inside_allowed(path: Path) -> bool:
        return common in path.parents or (addons is not None and addons in path.parents)

    # Game class names: class_name declared outside common/ and addons/.
    game_classes = set()
    for gd in root.rglob("*.gd"):
        if is_skipped(gd, root) or inside_allowed(gd):
            continue
        game_classes.update(CLASS_NAME.findall(read(gd)))

    # Game autoloads: autoloads whose script/scene lives outside common/ and addons/.
    game_autoloads = set()
    project_file = root / "project.godot"
    in_autoload = False
    for line in read(project_file).splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            in_autoload = stripped == "[autoload]"
            continue
        if in_autoload:
            m = AUTOLOAD_LINE.match(line)
            if m and not any(m.group(2).startswith(p) for p in allowed_prefixes):
                game_autoloads.add(m.group(1))

    game_names = game_classes | game_autoloads
    name_pattern = re.compile(r"\b(" + "|".join(sorted(map(re.escape, game_names))) + r")\b") if game_names else None

    errors = []
    for path in sorted(common.rglob("*")):
        if not path.is_file() or path.suffix not in {".gd", ".tscn", ".tres", ".gdshader", ".gdshaderinc"}:
            continue
        text = read(path)
        where = rel(path, root)
        for res in sorted(set(RES_PATH.findall(text))):
            if not any(res.startswith(p) for p in allowed_prefixes):
                errors.append(f"{where}: references {res}")
        if path.suffix == ".gd" and name_pattern:
            code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
            for name in sorted(set(name_pattern.findall(code))):
                kind = "autoload" if name in game_autoloads else "game class"
                errors.append(f"{where}: uses {kind} {name}")
    return errors, []


def main() -> int:
    if len(sys.argv) > 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1] if len(sys.argv) == 2 else ".").resolve()
    if not (root / "project.godot").is_file():
        print(f"error: no project.godot in {root}")
        return 2

    name_err, name_warn = check_names(root)
    top_warn, top_info = check_top_level(root)
    pure_err, pure_info = check_common_purity(root)

    sections = [
        ("ERRORS: common/ purity (move to utilities/ or pass data in)", pure_err),
        ("ERRORS: spaces in names", name_err),
        ("WARNINGS: top-level structure", top_warn),
        ("WARNINGS: naming (should be snake_case)", name_warn),
        ("INFO", top_info + pure_info),
    ]
    print(f"Function First audit: {root}\n")
    for title, items in sections:
        if items:
            print(f"{title} ({len(items)})")
            for item in items:
                print(f"  - {item}")
            print()

    n_err = len(pure_err) + len(name_err)
    n_warn = len(top_warn) + len(name_warn)
    print(f"Summary: {n_err} error(s), {n_warn} warning(s).")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())

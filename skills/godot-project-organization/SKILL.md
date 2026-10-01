---
name: godot-project-organization
description: Organizes Godot 4 projects with the "Function First" structure. Folders are grouped by in-game function (entities, stages, ui) rather than by file type, and all names follow Godot's official snake_case conventions. Use this skill whenever working in a Godot project (a folder with project.godot, or .gd/.tscn/.tres files) and deciding where a new scene, script, resource or asset should go, or what to name it. Also use it when setting up the folder structure of a new Godot project, auditing or reorganizing an existing one, renaming files to Godot conventions, or when the user asks "where should I put this?" in Godot, even if they don't mention organization explicitly.
---

# Godot Project Organization: Function First

A folder structure for Godot 4 projects that groups files by in-game function, with naming that follows Godot's official conventions.

**Never move or rename existing files, and never run the audit script, unless the user explicitly asks.** Otherwise, apply these rules only to new files. If the skill is invoked without a specific task, say in one line what it can help with (placing or naming a file, setting up folders, auditing, reorganizing) and ask what the user wants. Don't start an audit on your own.

## The two core rules

1. **Group by in-game function first, by file type last.** Top-level folders say what things *are in the game* (`entities/`, `stages/`, `ui/`), never what kind of file they are (no `scripts/`, `scenes/`, `textures/`). File-type folders (`art/`, `sound/`, `data/`) only exist at the bottom, inside the folder of the one thing that uses them. This way every change to a thing, and every bug in it, has exactly one place to look.
2. **Keep the number of top-level folders small.** Don't add a new top-level folder when an existing bucket fits. Push large groups of siblings at least one level down.

## Top-level layout

```
res://
├── addons/          # Third-party plugins and asset packs
├── assets/          # Only assets used across the whole game (music, fonts, credits)
├── common/          # Game-agnostic, reusable systems (strict purity rule)
├── config/          # Player-facing settings: volume, resolution, gameplay options
├── entities/        # Anything in the game world the player sees or interacts with
├── localization/    # Translated text
├── stages/          # Areas/maps the player is inside of, plus shared TileSets
├── ui/              # The game's own interfaces: HUD, menus, crafting screens
├── utilities/       # Game-specific helpers, tools and autoloads
└── (Godot's own root files: project.godot, icon.png, default_bus_layout.tres, …)
```

For what belongs in each folder, with example trees, read `references/folders.md`.

## Where does a new file go?

Ask these questions in order and stop at the first "yes":

1. Third-party plugin or asset pack? → `addons/`
2. Reusable in another game unchanged, with no references to game code? → `common/`
   - Reusable idea, but it depends on game code? → `utilities/`
3. An area/map the player is inside of, or a TileSet for one? → `stages/`
4. One of the game's interfaces (HUD, menu, screen)? → `ui/<screen_name>/`
5. Exists in the game world, or the player interacts with it? → `entities/<domain>/…`
   - Subtype of an existing type? → a folder under its base type, class named with the parent as suffix.
   - New concrete thing? → its own leaf folder: `entities/<domain>/<category>/<thing_name>/`.
6. Background system, autoload, or game-specific tool? → `utilities/`
7. Player-facing setting? → `config/`
8. Translated text? → `localization/`
9. An asset used across the entire game? → `assets/`
10. An asset used by one thing? → that thing's `art/`, `sound/` or `data/` subfolder. Never `assets/`.

If nothing fits, tell the user and suggest the closest existing bucket before proposing a new top-level folder.

**Entities vs. stages:** entities are usually *siblings* of the player in the scene tree; stages are the *parent* the player lives in. An island is a stage; the palm tree on it is an entity.

## The two structural patterns

**Leaf folder: one thing = one folder.** The scene and its script share a name and sit next to optional `art/`, `data/` and `sound/` subfolders:

```
entities/organisms/invertebrates/sand_crab/
├── art/
├── data/
├── sound/
├── sand_crab_organism.gd     # class_name SandCrabOrganism
└── sand_crab_organism.tscn
```

**Inheritance mirrors the folder tree.** The base type's script sits at the top of its folder; each subtype gets a sibling folder with its own base script; subclasses carry the parent's name as a suffix (`Item` → `ToolItem` → `ForagingToolItem`). The path reads like the type chain: `entities/items/tools/foraging/`.

For full examples, including the data/scene split (`ToolItem` resource vs. `Tool` scene) and typed flag exports, read `references/patterns.md`.

## Naming (Godot official conventions)

Rule of thumb: **anything on disk is snake_case; anything in code or the scene tree is PascalCase.**

| Thing | Convention | Example |
|---|---|---|
| Folders | snake_case, no spaces | `sand_crab/`, `time_manager/` |
| Scripts | snake_case of the class name | `tool_item.gd` → `class_name ToolItem` |
| Scenes | snake_case, same name as its script | `tool_item.gd` + `tool_item.tscn` |
| Resources | snake_case | `organism_list.tres` |
| `class_name` | PascalCase, parent name as suffix for subclasses | `ForagingToolItem` |
| Node names | PascalCase, no spaces | `MapSurface`, `PalmTree2` |
| Autoloads | file snake_case, registered name PascalCase, `Manager` suffix for services | `game_manager.gd` → `GameManager` |
| Variables, functions | snake_case | `max_stack_size`, `save_to_dict()` |
| Enums | PascalCase name, CONSTANT_CASE members | `ItemType.EQUIPMENT` |
| Exported enums/flags | typed: `@export var x: MyEnum` or `@export_flags(...)` | never `int` plus a comment |

The reason for snake_case on disk: Windows and macOS ignore case, but exported `.pck` files don't, so a path with the wrong case works in the editor and breaks in the exported game. C# files are the exception: Godot's C# convention is PascalCase file names matching the class.

## The common/ purity rule

Nothing in `common/` may reference game-specific code:
- no `class_name` types defined outside `common/` and `addons/`
- no `res://` paths outside `common/` and `addons/`
- no game autoloads (`GameManager`, `GlobalSignals`, …)

Dependencies go one way: game code may use `common/`, never the reverse. If a common system needs game data, pass it in through exports, function parameters or signals. When code fails this rule, move it to `utilities/` (or wherever its in-game function belongs). `common/ui/` may hold generic widgets like tooltips; the game's actual screens go in the top-level `ui/`.

## Workflows

### Adding files to a project
Use the decision guide above, name the file by the naming table, and create the leaf folder if the thing doesn't have one yet. Mention the chosen location in one line so the user can object.

### Setting up a new project
Create the top-level folders from the layout above (skip ones the project clearly won't need yet, such as `localization/`). Git doesn't track empty folders, so if the user wants the empty structure committed, add an empty `.gitkeep` file in each.

### Auditing an existing project
Only when the user asks for an audit. Run the bundled audit script from the project root (the folder with `project.godot`):

```bash
python3 <skill-dir>/scripts/audit_project.py <path-to-godot-project>
```

It reports names that aren't snake_case, spaces in names, file-type folders at the top level, and `common/` purity violations. It doesn't change anything. Summarize the findings for the user, grouped by severity, before proposing changes.

### Reorganizing an existing project
Reorganizing touches references across the whole project, so:

1. **Don't restructure unasked.** If the project uses a different structure, propose the move and wait for approval. Present it as a table of old path → new path.
2. **Recommend a commit first**, so the move can be undone.
3. **Prefer moving files in Godot's FileSystem dock.** The editor updates references in scenes and resources. When the user can do this, give them the move list.
4. **If you must move files from the command line:** move sidecar files with their source (`foo.png.import`, `foo.gd.uid`), then update every `res://old/path` string in `.tscn`, `.tres`, `.gd`, `.cfg` and `project.godot` (including autoload paths). Afterwards, tell the user to open the project in the editor and check the Output panel for broken dependencies.
5. **Search scripts for hard-coded paths** (`load()`, `preload()`, exported path strings). The editor doesn't update these even when moving in the FileSystem dock.
6. Move in small batches (one top-level folder at a time) and re-run the audit script after each batch.

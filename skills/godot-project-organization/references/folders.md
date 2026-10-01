# Folder reference

What belongs in each top-level folder. The examples show the shape; a project only needs the subfolders it actually uses.

## Contents

- addons/
- assets/
- common/
- config/
- entities/
- localization/
- stages/
- ui/
- utilities/

---

## addons/

Third-party plugins and asset packs, following Godot's own convention. Leave plugin folder names as the plugin ships them, since plugins often reference their own paths.

## assets/

**Only assets used across the whole game.** Most art and sound does _not_ go here; it lives in the `art/` and `sound/` folders of the thing that uses it.

```
assets/
├── audio/     # soundtrack
├── credits/   # e.g. list of supporters
└── fonts/     # fonts used across the UI
```

If an asset in `assets/` turns out to be used by only one thing, move it to that thing's leaf folder.

## common/

Reusable systems that are **not specific to this game**. Every folder in here should be droppable into another Godot project with zero edits.

```
common/
├── animations/
├── collisions/
├── lights/
├── loot/
├── projectiles/
├── resolution_management/
│   └── interface_scaler/
│       ├── interface_scaler.gd     # class_name InterfaceScaler
│       └── interface_scaler.tscn
├── shaders/
├── shadows/
├── state_management/
│   └── states/
│       ├── chase/  fear/  idle/  ready/  wander/
├── time_manager/
│   ├── time_manager.gd             # class_name TimeManager
│   └── time_manager.tscn
├── tooltips/
├── transitions/
├── ui/                             # generic widgets only
└── visual_effects/
```

Typical residents: a state machine, a resolution/interface scaler, general-purpose shaders, an in-game time system, screen transitions.

**Purity rule:** no references to game-specific `class_name` types, no `res://` paths outside `common/` and `addons/`, no game autoloads. Game code may depend on `common/`; `common/` never depends on game code. Pass game data in through exports, parameters or signals.

Good fit: a generic `StateMachine` whose states are passed in. Bad fit: a state that calls `GameManager.save()`, which belongs in `utilities/` or with the entity that uses it.

Having `common/` also acts as a nudge: when building a system, ask whether it could be made generic enough to live here.

## config/

Small. Holds what appears in the player's options menu: audio bus volumes, resolution, gameplay tweaks.

## entities/

The largest folder. **Anything in the game world**, especially anything the player can interact with: the player, NPCs, creatures, items, weather, building systems, gathering nodes, crafting stations, ships, spawners, terrain features.

```
entities/
├── crafting/
├── environment/
├── fish/
├── foraging/
├── items/
├── npcs/
├── organisms/
├── player/
├── ships/
├── spawner/
├── terrain/
└── weather/
```

Inside a domain, go **domain → category → individual thing → asset types**:

```
entities/organisms/
├── fish/
├── fungi/
├── invertebrates/
│   ├── coral_head/
│   ├── jellyfish/
│   ├── sand_crab/
│   │   ├── art/
│   │   ├── data/
│   │   ├── sound/
│   │   ├── sand_crab_organism.gd
│   │   └── sand_crab_organism.tscn
│   └── tube_coral/
├── mammals/
├── plants/
├── reptiles/
├── organism.gd            # base class
├── organism.tscn          # base scene
├── organism_data.gd       # data resource definition
├── organism_list.gd
└── organism_list.tres
```

A big `entities/` is expected in a content-heavy game; that's fine as long as each subfolder has a clear in-game meaning.

## localization/

Translation files (`.csv`, `.po`, `.translation`). Give it a place early, even if empty, so localization stays easy to add.

## stages/

**Areas the player is inside of:** islands, caves, dungeons, levels, the open world, building interiors, vehicle interiors. Mostly tile map scenes, handmade or procedural.

Shared **TileSet resources** live in `stages/tile_sets/`, since stages are their main users (e.g. water tiles reused across several area types).

A stage scene is the parent; entities are placed under it:

```
CoralIsland (stages/islands/coral_island/coral_island.tscn)
├── Camera
├── TileMap
├── MapSurface
└── Entities
    ├── ResearchVessel
    ├── FishermansHutExterior
    ├── Workbench
    └── PalmTree …
```

## ui/

**The game's own interfaces:** player HUD, inventory, crafting and fishing screens, journals, main menu, pause menu. Each screen is a leaf folder:

```
ui/
├── hud/
├── inventory/
├── crafting_menu/
├── field_notes/
└── main_menu/
```

Generic, reusable widgets (tooltip, fade transition) go in `common/` instead and must pass the purity rule.

## utilities/

A deliberate grab bag for **game-specific** behind-the-scenes code and tools, including anything that would be in `common/` except that it depends on game code.

- `game_manager.gd` (`GameManager`): saving and loading
- `global_signals.gd` (`GlobalSignals`): global signal bus
- `scene_manager.gd` (`SceneManager`): scene transitions and caching

Many of these are autoload singletons. Files are snake_case; the name registered under Project Settings → Autoload is PascalCase, usually with a `Manager` suffix for services.

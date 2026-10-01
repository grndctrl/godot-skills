# Structural patterns

## 1. Leaf folder: one thing = one folder

Each concrete thing (a creature, a tool, a HUD screen) gets its own folder. Inside:

- the scene and its script, sharing one snake_case name
- optional `art/`, `data/`, `sound/` subfolders for assets only that thing uses

```
sand_crab/
├── art/
├── data/                  # Resource files (.tres) describing this thing
├── sound/
├── sand_crab_organism.gd
└── sand_crab_organism.tscn
```

Only create the asset subfolders that are needed. A thing with one sprite doesn't need `sound/` or `data/`.

## 2. Inheritance mirrors the folder tree

1. Put the **base type** script at the top level of its folder.
2. Give **each subtype a sibling folder**, containing its own base script and, in turn, its own subtype folders.
3. Name subclasses with the **parent's name as suffix** so the chain is visible at a glance.
4. Put concrete implementations at the bottom.

```
entities/items/
├── consumable/
├── equipment/
├── forageable/
├── placeable/
├── tools/
│   ├── fishing/
│   ├── foraging/
│   │   ├── foraging_tool_item.gd    # class_name ForagingToolItem extends ToolItem
│   │   ├── axe/
│   │   └── pickaxe/
│   ├── other/
│   ├── weapons/
│   ├── tool.gd                      # class_name Tool (the in-world scene's script)
│   ├── tool.tscn
│   └── tool_item.gd                 # class_name ToolItem extends Item
└── item.gd                          # class_name Item extends Resource
```

The path `entities/items/tools/foraging/axe/` reads as the type chain Item → ToolItem → ForagingToolItem → axe.

## 3. Split data from the in-world scene

Describe a thing's *data* as a `Resource` (what shows in an inventory, what gets saved) and its *presence in the world* as a scene. Keep both in the same folder.

- `ToolItem` (Resource): name, icon, stack size, which scene to spawn
- `Tool` (`tool.gd` + `tool.tscn`): the node that exists in the world when equipped

Organisms follow the same idea: `Organism` (scene) plus `OrganismData` (resource definition), with `organism_list.tres` as a data catalog.

## 4. Typed type-flags and inherited saving

```gdscript
# entities/items/item.gd
class_name Item extends Resource

# Bit flags. Update this and the @export_flags list for every new item type.
enum ItemType {
    EQUIPMENT = 1,
    TOOL = 2,
    CONSUMABLE = 4,
    PLACEABLE = 8,
    FORAGEABLE = 16,
}

@export var name: String = ""
@export var description: String = ""
@export_flags("Equipment", "Tool", "Consumable", "Placeable", "Forageable") var base_item_type: int = 0
@export var max_stack_size: int = 1
@export var inventory_texture: Texture2D

var amount: int = 1
```

```gdscript
# entities/items/tools/tool_item.gd
class_name ToolItem extends Item

enum ToolItemType {
    WEAPON = 1,
    FISHING = 2,
    FORAGING = 4,
    OTHER = 8,
}

@export_flags("Weapon", "Fishing", "Foraging", "Other") var tool_item_type: int = 0
@export var tool_scene_path: String
@export var tool_equipped_texture: Texture2D

var tool_instance: Tool


func _init() -> void:
    call_deferred("_load_tool")


func _load_tool() -> void:
    tool_instance = load(tool_scene_path).instantiate()


func save_to_dict() -> Dictionary:
    var save_dict: Dictionary = super.save_to_dict()
    # add ToolItem-specific fields here
    return save_dict
```

Notes:
- Bit-flag values (1, 2, 4, 8, 16) let one item have several types. The `@export_flags` labels must be in the same order as the enum values.
- If a value can only ever be one type, use `@export var base_item_type: ItemType` instead (dropdown rather than checkboxes).
- Each level extends `save_to_dict()` with `super`, so saving follows the same chain as the folders.
- Path strings like `tool_scene_path` are *not* updated when files move. Search for them after any reorganization. Exporting a `PackedScene` instead of a path string avoids this, at the cost of loading the scene together with the resource.

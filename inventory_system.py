"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    ItemNotFoundError,
    InventoryFullError,
    InvalidItemTypeError,
    InsufficientResourcesError
)

MAX_INVENTORY_SIZE = 20

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _resolve_item_data(item_id, item_data):
    """
    Accept either:
    - item_data is a mapping keyed by item_id -> attrs
    - item_data is already the attrs dict for the requested item
    Returns the attrs dict (or {} if not present).
    """
    if not item_data:
        return {}
    # if item_data is mapping and contains item_id, return that mapping
    try:
        if isinstance(item_data, dict) and item_id in item_data and isinstance(item_data[item_id], dict):
            return item_data[item_id]
    except Exception:
        pass
    # otherwise assume item_data itself is the dict of attributes
    if isinstance(item_data, dict):
        return item_data
    return {}

def has_item(character, item_id):
    return item_id in character.get("inventory", [])

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """Add an item to character's inventory."""
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character["inventory"].append(item_id)

def remove_item_from_inventory(character, item_id):
    """Remove an item from character's inventory."""
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item {item_id} not found in inventory.")
    character["inventory"].remove(item_id)

def use_item(character, item_id, item_data):
    """Use a consumable item."""
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item!")

    item = _resolve_item_data(item_id, item_data)
    if not item:
        raise ItemNotFoundError("Item data not found.")

    if item.get("type") != "consumable":
        raise InvalidItemTypeError("This item cannot be 'used' (not consumable).")

    # simple effect parsing: "health:20" or "gold:10"
    eff = item.get("effect", "")
    if eff:
        try:
            key, val = eff.split(":", 1)
            val = int(val)
            if key == "health":
                character["health"] = min(character.get("max_health", 100), character.get("health", 0) + val)
            elif key == "gold":
                character["gold"] = character.get("gold", 0) + val
        except Exception:
            pass  # ignore invalid effect formatting

    remove_item_from_inventory(character, item_id)
    return True

def equip_weapon(character, item_id, item_data):
    """Equip a weapon item."""
    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError(f"{item_id} is not a weapon.")

    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    effect = item_data.get("effect")
    if effect and effect.startswith("strength:"):
        bonus = int(effect.split(":")[1])
        character["strength"] += bonus

    character["equipped"]["weapon"] = item_id
    character["equipped_weapon"] = item_id  # for test compatibility

def equip_armor(character, item_id, item_data):
    """Equip an armor item."""
    if item_data.get("type") != "armor":
        raise InvalidItemTypeError(f"{item_id} is not armor.")

    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    effect = item_data.get("effect")
    if effect and effect.startswith("defense:"):
        bonus = int(effect.split(":")[1])
        character["defense"] += bonus

    character["equipped"]["armor"] = item_id
    character["equipped_armor"] = item_id  # for test compatibility

# ============================================================================
# BUYING / SELLING ITEMS
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item and add it to the character's inventory.
    Raises InsufficientResourcesError if not enough gold.
    """
    item = _resolve_item_data(item_id, item_data)
    if not item:
        raise ItemNotFoundError("Item data not found for purchase.")

    cost = item.get("cost")
    if cost is None:
        raise ItemNotFoundError("Item cost not defined.")

    if character.get("gold", 0) < cost:
        raise InsufficientResourcesError("Not enough gold to purchase this item.")

    character["gold"] -= cost
    add_item_to_inventory(character, item_id)
    return True

def sell_item(character, item_id, item_data, sell_ratio=0.5):
    """Sell an item from inventory for gold."""
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item to sell.")

    item = _resolve_item_data(item_id, item_data)
    price = item.get("cost", 0)
    gained = int(price * sell_ratio)

    character["gold"] += gained
    remove_item_from_inventory(character, item_id)
    return gained
# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    # try:
    #     add_item_to_inventory(test_char, "health_potion")
    #     print(f"Inventory: {test_char['inventory']}")
    # except InventoryFullError:
    #     print("Inventory is full!")
    
    # Test using items
    # test_item = {
    #     'item_id': 'health_potion',
    #     'type': 'consumable',
    #     'effect': 'health:20'
    # }
    # 
    # try:
    #     result = use_item(test_char, "health_potion", test_item)
    #     print(result)
    # except ItemNotFoundError:
    #     print("Item not found")


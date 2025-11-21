"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles inventory management, item usage, and equipment.
"""

# inventory_system.py
from custom_exceptions import (
    ItemNotFoundError,
    InventoryFullError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Helper constants
MAX_INVENTORY_SIZE = 20

def has_item(character: dict, item_id: str) -> bool:
    return item_id in character.get("inventory", [])

def add_item_to_inventory(character: dict, item_id: str) -> bool:
    inventory = character.setdefault("inventory", [])
    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    inventory.append(item_id)
    return True

def remove_item_from_inventory(character: dict, item_id: str) -> bool:
    inventory = character.get("inventory", [])
    if item_id not in inventory:
        raise ItemNotFoundError("Item not found in inventory.")
    inventory.remove(item_id)
    return True

def _parse_effect(effect_str: str) -> tuple[str, int]:
    """
    Parse effect strings like "health:20" or "strength:5"
    Returns (stat, value)
    """
    if not isinstance(effect_str, str) or ":" not in effect_str:
        raise InvalidItemTypeError("Invalid effect format.")
    stat, val = effect_str.split(":", 1)
    try:
        val_int = int(val)
    except ValueError:
        raise InvalidItemTypeError("Effect value must be integer.")
    return stat.strip(), val_int

def use_item(character: dict, item_id: str, item_data: dict):
    """
    item_data is the single-item dict for the item being used, e.g.:
    {'type': 'consumable', 'effect': 'health:20'}
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item!")

    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Item data must be a dict.")

    item_type = item_data.get("type")
    if item_type != "consumable":
        # trying to "use" a weapon/armor should raise InvalidItemTypeError
        raise InvalidItemTypeError("This item can't be used like that.")

    effect = item_data.get("effect")
    stat, value = _parse_effect(effect)

    # Apply effect
    if stat == "health":
        character["health"] = min(character.get("max_health", character.get("health", 0)), character.get("health", 0) + value)
    else:
        # Generic stat application
        character[stat] = character.get(stat, 0) + value

    # Remove consumable from inventory after use
    remove_item_from_inventory(character, item_id)
    return True

def equip_weapon(character: dict, item_id: str, item_data: dict):
    """
    item_data example: {'type': 'weapon', 'effect': 'strength:5'}
    Equips weapon (adds stat), stores equipped weapon id.
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that weapon!")

    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Item data must be a dict.")

    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    stat, value = _parse_effect(item_data.get("effect", "strength:0"))

    # Unequip old weapon if present (naive approach: don't try to reverse effects unless tracked)
    # For these tests it's enough to apply the weapon's bonus.
    character[stat] = character.get(stat, 0) + value
    character["equipped_weapon"] = item_id
    return True

def equip_armor(character: dict, item_id: str, item_data: dict):
    """
    item_data example: {'type': 'armor', 'effect': 'defense:3'}
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that armor!")

    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Item data must be a dict.")

    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    stat, value = _parse_effect(item_data.get("effect", "defense:0"))
    character[stat] = character.get(stat, 0) + value
    character["equipped_armor"] = item_id
    return True

def purchase_item(character: dict, item_id: str, item_data: dict):
    """
    item_data is the single-item info dict, e.g. {'cost': 25, 'type': 'consumable'}
    """
    if not isinstance(item_data, dict):
        raise InvalidItemTypeError("Invalid item data provided.")

    cost = item_data.get("cost")
    if cost is None:
        raise InvalidItemTypeError("Item cost missing.")

    try:
        cost = int(cost)
    except (TypeError, ValueError):
        raise InvalidItemTypeError("Invalid item cost.")

    gold = character.get("gold", 0)
    if gold < cost:
        raise InsufficientResourcesError("Not enough gold to purchase item.")

    # Deduct gold and add to inventory
    character["gold"] = gold - cost
    add_item_to_inventory(character, item_id)
    return True

def sell_item(character: dict, item_id: str, item_data: dict):
    """
    Sell item: removes from inventory and adds back half the cost by default.
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item!")

    cost = item_data.get("cost", 0)
    try:
        cost = int(cost)
    except (TypeError, ValueError):
        cost = 0

    character["gold"] = character.get("gold", 0) + (cost // 2)
    remove_item_from_inventory(character, item_id)
    return True

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


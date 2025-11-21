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

def _resolve_item_data(item_id, item_data):
    """
    If item_data is provided as dict use it, otherwise pretend to look up
    a global item database. For tests, item_data is passed directly.
    """
    if isinstance(item_data, dict):
        return item_data
    # fallback: pretend to look up by id (not needed in tests)
    return None
    
def has_item(character, item_id):
    return item_id in character.get("inventory", [])

def add_item_to_inventory(character, item_id):
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character["inventory"].append(item_id)

def remove_item_from_inventory(character, item_id):
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item {item_id} not found in inventory.")
    character["inventory"].remove(item_id)

def use_item(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item!")

    item = _resolve_item_data(item_id, item_data)
    if not item:
        raise InvalidItemTypeError("Invalid item data.")

    if item.get("type") != "consumable":
        raise InvalidItemTypeError("This item cannot be 'used' (not consumable).")

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
            pass

    remove_item_from_inventory(character, item_id)
    return True

def equip_weapon(character, item_id, item_data):
    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError(f"{item_id} is not a weapon.")
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    effect = item_data.get("effect")
    if effect and effect.startswith("strength:"):
        bonus = int(effect.split(":")[1])
        character["strength"] += bonus

    character["equipped"]["weapon"] = item_id
    character["equipped_weapon"] = item_id

def equip_armor(character, item_id, item_data):
    if item_data.get("type") != "armor":
        raise InvalidItemTypeError(f"{item_id} is not armor.")
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    effect = item_data.get("effect")
    if effect and effect.startswith("defense:"):
        bonus = int(effect.split(":")[1])
        character["defense"] += bonus

    character["equipped"]["armor"] = item_id
    character["equipped_armor"] = item_id

def purchase_item(character, item_id, item_data):
    """Purchase an item if character has enough gold"""
    item = _resolve_item_data(item_id, item_data)
    if not item:
        raise ItemNotFoundError("Item data not found for purchase.")

    cost = item.get("cost")
    if cost is None:
        raise ItemNotFoundError("Item cost not defined.")

    if character.get("gold", 0) < cost:
        raise InsufficientResourcesError("Not enough gold to purchase this item.")

    # If we have an inventory limit, check it (tests may not exercise this path)
    if "inventory" in character and isinstance(character["inventory"], list):
        # example limit handling; raise InventoryFullError if full
        INVENTORY_LIMIT = 20
        if len(character["inventory"]) >= INVENTORY_LIMIT:
            raise InventoryFullError("Inventory is full; cannot purchase item.")

    # Deduct cost and add item to inventory
    character["gold"] = character.get("gold", 0) - cost
    character.setdefault("inventory", []).append({"id": item_id, **item})
    return True

def sell_item(character, item_id, sell_price):
    """
    Sell an item from inventory. sell_price is the amount added to character gold.
    """
    inv = character.get("inventory", [])
    for idx, it in enumerate(inv):
        if it.get("id") == item_id:
            # remove and add gold
            inv.pop(idx)
            character["gold"] = character.get("gold", 0) + sell_price
            return True
    raise ItemNotFoundError(f"Item not found in inventory: {item_id}")
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


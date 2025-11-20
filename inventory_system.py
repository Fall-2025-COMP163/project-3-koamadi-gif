"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

MAX_INVENTORY_SIZE = 20

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

def add_item_to_inventory(character, item_id):
    inv = character.setdefault("inventory", [])
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    inv.append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    inv = character.setdefault("inventory", [])
    if item_id not in inv:
        raise ItemNotFoundError("Item not in inventory.")
    inv.remove(item_id)
    return True

def use_item(character, item_id, item_data):
    """
    Use a consumable item. item_data can be:
      - {'health_potion': {'type':'consumable', 'effect':'health:20'}}
      - or a single-item dict {'type':'consumable','effect':'health:20'}
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item!")

    item = _resolve_item_data(item_id, item_data)
    if not item:
        # fallback: treat as invalid item data (but tests expect InvalidItemTypeError for wrong type)
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
            # more effects could be supported
        except Exception:
            # if effect parse fails, ignore and still remove item
            pass

    # consume item
    remove_item_from_inventory(character, item_id)
    return True

def equip_weapon(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that weapon!")

    item = _resolve_item_data(item_id, item_data)
    if not item:
        raise ItemNotFoundError("Weapon data not found.")

    if item.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # parse effect like "strength:5"
    eff = item.get("effect", "")
    if eff:
        try:
            key, val = eff.split(":", 1)
            val = int(val)
            character[key] = character.get(key, 0) + val
        except Exception:
            pass

    # mark equipped (simple)
    character.setdefault("equipped", {})["weapon"] = item_id
    return True

def equip_armor(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that armor!")

    item = _resolve_item_data(item_id, item_data)
    if not item:
        raise ItemNotFoundError("Armor data not found.")

    if item.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    eff = item.get("effect", "")
    if eff:
        try:
            key, val = eff.split(":", 1)
            val = int(val)
            character[key] = character.get(key, 0) + val
        except Exception:
            pass

    character.setdefault("equipped", {})["armor"] = item_id
    return True

def purchase_item(character, item_id, item_data):
    """
    item_data can be either mapping keyed by id or the item's attribute dict itself.
    """
    item = _resolve_item_data(item_id, item_data)
    if not item:
        raise ItemNotFoundError("Item data not found for purchase.")

    cost = item.get("cost")
    if cost is None:
        raise ItemNotFoundError("Item cost not defined.")

    if character.get("gold", 0) < cost:
        raise InsufficientResourcesError("Not enough gold to purchase this item.")

    # subtract gold and add to inventory
    character["gold"] = character.get("gold", 0) - cost
    add_item_to_inventory(character, item_id)
    return True

def sell_item(character, item_id, item_data, sell_ratio=0.5):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item to sell.")
    item = _resolve_item_data(item_id, item_data)
    price = item.get("cost", 0)
    gained = int(price * sell_ratio)
    character["gold"] = character.get("gold", 0) + gained
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


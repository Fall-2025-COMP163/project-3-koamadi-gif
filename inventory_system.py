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

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    inventory = character.get("inventory", [])

    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    inventory.append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    inventory = character.get("inventory", [])

    if item_id not in inventory:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    inventory.remove(item_id)
    return True

def has_item(character, item_id):
    """
    Check if character has a specific item
    
    Returns: True if item in inventory, False otherwise
    """
    return item_id in character.get("inventory", [])

def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    return character.get("inventory", []).count(item_id)

def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    return MAX_INVENTORY_SIZE - len(character.get("inventory", []))
    # TODO: Implement space calculation

def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    removed_items = character.get("inventory", []).copy()
    character["inventory"] = []
    return removed_items

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found in inventory.")

    if item_data["type"] != "consumable":
        raise InvalidItemTypeError(f"{item_id} is not a consumable.")

    stat, value = parse_item_effect(item_data["effect"])

    apply_stat_effect(character, stat, value)

    remove_item_from_inventory(character, item_id)

    item_name = item_data.get("name", item_id)
    return f"Used {item_name} and gained {value} {stat}."

def equip_weapon(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found.")

    if item_data["type"] != "weapon":
        raise InvalidItemTypeError(f"{item_id} is not a weapon.")

    if character.get("equipped_weapon"):
        old_weapon_id = character["equipped_weapon"]
        old_weapon_data = character["item_data"][old_weapon_id]

        stat, value = parse_item_effect(old_weapon_data["effect"])
        apply_stat_effect(character, stat, -value)

        add_item_to_inventory(character, old_weapon_id)

    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)

    character["equipped_weapon"] = item_id
    remove_item_from_inventory(character, item_id)

    weapon_name = item_data.get("name", item_id)
    return f"Equipped weapon: {weapon_name}"

def equip_armor(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found.")

    if item_data["type"] != "armor":
        raise InvalidItemTypeError(f"{item_id} is not armor.")

    # Unequip current armor
    if character.get("equipped_armor"):
        old_armor_id = character["equipped_armor"]
        old_armor_data = character["item_data"][old_armor_id]

        stat, value = parse_item_effect(old_armor_data["effect"])
        apply_stat_effect(character, stat, -value)

        add_item_to_inventory(character, old_armor_id)

        # Equip new armor
    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)

    character["equipped_armor"] = item_id
    remove_item_from_inventory(character, item_id)

    armor_name = item_data.get("name", item_id)
    return f"Equipped armor: {armor_name}"

def unequip_weapon(character):
    if not character.get("equipped_weapon"):
        return None

    weapon_id = character["equipped_weapon"]
    weapon_data = character["item_data"][weapon_id]

    stat, value = parse_item_effect(weapon_data["effect"])
    apply_stat_effect(character, stat, -value)

    if get_inventory_space_remaining(character) == 0:
        raise InventoryFullError("No space to unequip weapon.")

    add_item_to_inventory(character, weapon_id)
    character["equipped_weapon"] = None

    return weapon_id

def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no armor equipped
    Raises: InventoryFullError if inventory is full
    """
    if not character.get("equipped_armor"):
        return None

    armor_id = character["equipped_armor"]
    armor_data = character["item_data"][armor_id]

    stat, value = parse_item_effect(armor_data["effect"])
    apply_stat_effect(character, stat, -value)

    if get_inventory_space_remaining(character) == 0:
        raise InventoryFullError("No space to unequip armor.")

    add_item_to_inventory(character, armor_id)
    character["equipped_armor"] = None

    return armor_id
    # TODO: Implement armor unequipping

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    cost = item_data["cost"]

    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold.")

    if get_inventory_space_remaining(character) == 0:
        raise InventoryFullError("Inventory full.")

    character["gold"] -= cost
    add_item_to_inventory(character, item_id)

    return True

def sell_item(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found.")

    price = item_data["cost"] // 2

    remove_item_from_inventory(character, item_id)
    character["gold"] += price

    return price

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    try:
        stat, value = effect_string.split(":")
        return stat, int(value)
    except:
        raise InvalidItemTypeError("Invalid effect format.")

def apply_stat_effect(character, stat_name, value):
    if stat_name not in character:
        character[stat_name] = 0

    character[stat_name] += value

    # Cap health at max_health
    if stat_name == "health":
        character["health"] = min(character["health"], character.get("max_health", 9999))

def display_inventory(character, item_data_dict):
    inventory = character.get("inventory", [])
    
    print("\n=== INVENTORY ===")
    if not inventory:
        print("Inventory is empty.")
        return
    
    counted = {}
    for item in inventory:
        counted[item] = counted.get(item, 0) + 1

    for item_id, qty in counted.items():
        item_name = item_data_dict[item_id]["name"]
        item_type = item_data_dict[item_id]["type"]
        print(f"{item_name} ({item_type}) x{qty}")

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


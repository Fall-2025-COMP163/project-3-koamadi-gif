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

# ============================================================================
# BASIC INVENTORY
# ============================================================================

def add_item_to_inventory(character, item_id):
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character['inventory'].append(item_id)


def remove_item_from_inventory(character, item_id):
    if item_id not in character['inventory']:
        raise ItemNotFoundError("Item not found.")
    character['inventory'].remove(item_id)


def has_item(character, item_id):
    return item_id in character['inventory']


def count_item(character, item_id):
    return character['inventory'].count(item_id)


def get_inventory_space_remaining(character):
    return MAX_INVENTORY_SIZE - len(character['inventory'])


def clear_inventory(character):
    removed = character['inventory'][:]
    character['inventory'].clear()
    return removed

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item!")

    item = item_data[item_id]
    if item['type'] != "consumable":
        raise InvalidItemTypeError("That item cannot be used.")

    stat, value = item['effect'].split(":")
    value = int(value)

    character[stat] = min(character['max_health'], character[stat] + value)

    remove_item_from_inventory(character, item_id)
    return f"You used {item['name']}!"

# ============================================================================
# EQUIPMENT
# ============================================================================

def equip_weapon(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that weapon!")

    item = item_data[item_id]
    if item['type'] != "weapon":
        raise InvalidItemTypeError("That is not a weapon!")

    if character.get("equipped_weapon"):
        return "You already have a weapon equipped!"

    stat, value = item['effect'].split(":")
    character[stat] += int(value)

    character["equipped_weapon"] = item_id
    remove_item_from_inventory(character, item_id)
    return f"You equipped {item['name']}!"

def equip_armor(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that armor!")

    item = item_data[item_id]
    if item['type'] != "armor":
        raise InvalidItemTypeError("That is not armor!")

    if character.get("equipped_armor"):
        return "You already have armor equipped!"

    stat, value = item['effect'].split(":")
    character[stat] += int(value)

    character["equipped_armor"] = item_id
    remove_item_from_inventory(character, item_id)
    return f"You equipped {item['name']}!"

# ============================================================================
# SHOP
# ============================================================================

def purchase_item(character, item_id, item_data):
    cost = item_data[item_id]['cost']
    if character['gold'] < cost:
        raise InsufficientResourcesError("Not enough gold!")
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError()
    
    character['gold'] -= cost
    add_item_to_inventory(character, item_id)
    return True


def sell_item(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You can't sell what you don't own!")

    sell_price = item_data[item_id]['cost'] // 2
    remove_item_from_inventory(character, item_id)
    character['gold'] += sell_price
    return sell_price

# ============================================================================
# UI / DISPLAY
# ============================================================================

def display_inventory(character, item_data_dict):
    if not character['inventory']:
        print("\nInventory is empty.")
        return

    print("\n=== Inventory ===")
    counted = {}
    for item_id in character['inventory']:
        counted[item_id] = counted.get(item_id, 0) + 1

    for item_id, qty in counted.items():
        item = item_data_dict[item_id]
        print(f"{item['name']} x{qty} ({item['type']})")
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


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


# Helper check
def has_item(character, item_id):
    return item_id in character.get("inventory", [])


def add_item_to_inventory(character, item_id, max_size=10):
    if len(character.get("inventory", [])) >= max_size:
        raise InventoryFullError("Inventory is full!")

    character.setdefault("inventory", []).append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    if not has_item(character, item_id):
        raise ItemNotFoundError("Item not found in inventory")

    character["inventory"].remove(item_id)
    return True


def use_item(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that item!")

    item_type = item_data.get("type")

    if item_type != "consumable":
        raise InvalidItemTypeError("This item cannot be used!")

    # Apply effect: "health:20" style
    effect = item_data.get("effect")
    if effect:
        stat, amount = effect.split(":")
        amount = int(amount)

        character[stat] = min(
            character.get(stat, 0) + amount,
            character.get(f"max_{stat}", character.get(stat, 0))
        )

    remove_item_from_inventory(character, item_id)
    return True


def equip_weapon(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don't have that weapon!")

    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("This item is not a weapon!")

    effect = item_data.get("effect")
    if effect:
        stat, amount = effect.split(":")
        character[stat] += int(amount)

    remove_item_from_inventory(character, item_id)
    character["equipped_weapon"] = item_id
    return True


def equip_armor(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("You don’t have that armor!")

    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("This item is not armor!")

    effect = item_data.get("effect")
    if effect:
        stat, amount = effect.split(":")
        character[stat] += int(amount)

    remove_item_from_inventory(character, item_id)
    character["equipped_armor"] = item_id
    return True


def purchase_item(character, item_id, item_data):
    cost = item_data.get("cost", 0)

    if character.get("gold", 0) < cost:
        raise InsufficientResourcesError("Not enough gold!")

    character["gold"] -= cost
    add_item_to_inventory(character, item_id)
    return True


def sell_item(character, item_id, item_data):
    if not has_item(character, item_id):
        raise ItemNotFoundError("Cannot sell item you don't own!")

    character["gold"] += item_data.get("cost", 0)
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


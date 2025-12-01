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

# Maximum number of items a character can carry at once
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to the character's inventory.

    Raises:
        InventoryFullError: If the character already has MAX_INVENTORY_SIZE items.
    Returns:
        True when item was successfully added.
    """
    # Retrieve inventory list or default to empty if missing.
    inventory = character.get("inventory", [])

    # Check if adding another item exceeds the allowed max size.
    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    # Append the item ID into inventory.
    inventory.append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove a specific item from the character's inventory.

    Raises:
        ItemNotFoundError: If item is not currently in inventory.
    Returns:
        True when removed successfully.
    """
    inventory = character.get("inventory", [])

    # Ensure item exists before removal.
    if item_id not in inventory:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    # Remove the first occurrence of the item.
    inventory.remove(item_id)
    return True


def has_item(character, item_id):
    """
    Check if character has a specific item in their inventory.

    Returns:
        True if found, otherwise False.
    """
    return item_id in character.get("inventory", [])


def count_item(character, item_id):
    """
    Count how many of a specific item the character owns.

    Returns:
        Integer count.
    """
    return character.get("inventory", []).count(item_id)


def get_inventory_space_remaining(character):
    """
    Determine how many inventory slots are left.

    Returns:
        Integer representing remaining capacity.
    """
    # Subtract current item count from the max capacity.
    return MAX_INVENTORY_SIZE - len(character.get("inventory", []))


def clear_inventory(character):
    """
    Remove all items from the inventory.

    Returns:
        List of items that were removed.
    """
    # Copy the list so we can return what was removed.
    removed_items = character.get("inventory", []).copy()

    # Reset inventory to empty list.
    character["inventory"] = []
    return removed_items

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item, applying its effect to the character.

    Raises:
        ItemNotFoundError: If item is not in inventory.
        InvalidItemTypeError: If the item is not consumable.
    Returns:
        A string describing the effect applied.
    """
    # Ensure player has the item.
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found in inventory.")

    # Ensure item is actually a consumable.
    if item_data["type"] != "consumable":
        raise InvalidItemTypeError(f"{item_id} is not a consumable.")

    # Parse effect such as "health:20" into ("health", 20).
    stat, value = parse_item_effect(item_data["effect"])

    # Apply stat change to the character.
    apply_stat_effect(character, stat, value)

    # Remove item after use.
    remove_item_from_inventory(character, item_id)

    item_name = item_data.get("name", item_id)
    return f"Used {item_name} and gained {value} {stat}."


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon item, applying its stat bonus and unequipping any previously equipped weapon.

    Raises:
        ItemNotFoundError: If weapon is not owned.
        InvalidItemTypeError: If item is not of type 'weapon'.
    Returns:
        String describing the newly equipped weapon.
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found.")

    if item_data["type"] != "weapon":
        raise InvalidItemTypeError(f"{item_id} is not a weapon.")

    # If a weapon is already equipped, remove its effects.
    if character.get("equipped_weapon"):
        old_weapon_id = character["equipped_weapon"]
        old_weapon_data = character["item_data"][old_weapon_id]

        # Reverse the old weapon's stat bonus.
        stat, value = parse_item_effect(old_weapon_data["effect"])
        apply_stat_effect(character, stat, -value)

        # Return old weapon back to inventory.
        add_item_to_inventory(character, old_weapon_id)

    # Apply new weapon bonuses.
    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)

    # Set new weapon as equipped.
    character["equipped_weapon"] = item_id

    # Remove weapon from inventory when equipped.
    remove_item_from_inventory(character, item_id)

    weapon_name = item_data.get("name", item_id)
    return f"Equipped weapon: {weapon_name}"


def equip_armor(character, item_id, item_data):
    """
    Equip an armor item, applying its stat bonus and unequipping prior armor.

    Raises:
        ItemNotFoundError: If armor not in inventory.
        InvalidItemTypeError: If item is not armor.
    Returns:
        String describing equipped armor.
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found.")

    if item_data["type"] != "armor":
        raise InvalidItemTypeError(f"{item_id} is not armor.")

    # Remove currently equipped armor first.
    if character.get("equipped_armor"):
        old_armor_id = character["equipped_armor"]
        old_armor_data = character["item_data"][old_armor_id]

        # Reverse old armor's bonus.
        stat, value = parse_item_effect(old_armor_data["effect"])
        apply_stat_effect(character, stat, -value)

        # Add old armor back to inventory.
        add_item_to_inventory(character, old_armor_id)

    # Apply new armor bonus.
    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)

    # Equip the new armor.
    character["equipped_armor"] = item_id

    # Remove it from inventory once worn.
    remove_item_from_inventory(character, item_id)

    armor_name = item_data.get("name", item_id)
    return f"Equipped armor: {armor_name}"


def unequip_weapon(character):
    """
    Unequip currently equipped weapon, reversing its stat bonus.

    Raises:
        InventoryFullError: if inventory has no space to store unequipped weapon.
    Returns:
        Weapon ID that was unequipped, or None if no weapon was equipped.
    """
    # No equipped weapon → nothing to do.
    if not character.get("equipped_weapon"):
        return None

    weapon_id = character["equipped_weapon"]
    weapon_data = character["item_data"][weapon_id]

    # Reverse stat change applied when equipped.
    stat, value = parse_item_effect(weapon_data["effect"])
    apply_stat_effect(character, stat, -value)

    # Check inventory capacity before unequipping.
    if get_inventory_space_remaining(character) == 0:
        raise InventoryFullError("No space to unequip weapon.")

    add_item_to_inventory(character, weapon_id)
    character["equipped_weapon"] = None

    return weapon_id


def unequip_armor(character):
    """
    Unequip currently equipped armor and return it to inventory.

    Raises:
        InventoryFullError: If no inventory space available.
    Returns:
        Item ID of unequipped armor or None.
    """
    if not character.get("equipped_armor"):
        return None

    armor_id = character["equipped_armor"]
    armor_data = character["item_data"][armor_id]

    # Reverse armor stat bonus.
    stat, value = parse_item_effect(armor_data["effect"])
    apply_stat_effect(character, stat, -value)

    if get_inventory_space_remaining(character) == 0:
        raise InventoryFullError("No space to unequip armor.")

    add_item_to_inventory(character, armor_id)
    character["equipped_armor"] = None

    return armor_id

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Buy an item from the shop and add it to inventory.

    Raises:
        InsufficientResourcesError: Not enough gold.
        InventoryFullError: No space for purchased item.
    Returns:
        True on successful purchase.
    """
    cost = item_data["cost"]

    # Check gold requirement.
    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold.")

    # Ensure there's space before buying.
    if get_inventory_space_remaining(character) == 0:
        raise InventoryFullError("Inventory full.")

    # Deduct cost and add the item.
    character["gold"] -= cost
    add_item_to_inventory(character, item_id)

    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item from inventory for half its original cost.

    Raises:
        ItemNotFoundError: If item isn't in inventory.
    Returns:
        Gold amount received from sale.
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not found.")

    # Shop pays 50% of original cost.
    price = item_data["cost"] // 2

    remove_item_from_inventory(character, item_id)

    # Add sale profit to gold.
    character["gold"] += price

    return price

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse an effect string like 'health:20' into ('health', 20).

    Raises:
        InvalidItemTypeError: If format is invalid.
    Returns:
        (stat_name, integer_value)
    """
    try:
        stat, value = effect_string.split(":")
        return stat, int(value)
    except:
        raise InvalidItemTypeError("Invalid effect format.")


def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat change to the character.

    Automatically clamps health to max_health when affected.
    """
    # Initialize stat if missing.
    if stat_name not in character:
        character[stat_name] = 0

    # Apply the stat delta.
    character[stat_name] += value

    # Prevent health from exceeding max_health.
    if stat_name == "health":
        character["health"] = min(
            character["health"],
            character.get("max_health", 9999)
        )


def display_inventory(character, item_data_dict):
    """
    Print inventory contents grouped and counted.

    Displays item name, type, and quantity.
    """
    inventory = character.get("inventory", [])
    
    print("\n=== INVENTORY ===")
    if not inventory:
        print("Inventory is empty.")
        return
    
    # Count duplicates for display formatting.
    counted = {}
    for item in inventory:
        counted[item] = counted.get(item, 0) + 1

    # Output each item with its name and type.
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


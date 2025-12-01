"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Missing file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        raise CorruptedDataError("Error reading quests file")

    if not content:
        raise CorruptedDataError("Quest file is empty or corrupted")

    quests = {}
    blocks = content.split("\n\n")

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        quest = parse_quest_block(lines)
        validate_quest_data(quest)
        quests[quest["quest_id"]] = quest

    return quests

def load_items(filename="data/items.txt"):
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Missing file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        raise CorruptedDataError("Error reading items file")

    if not content:
        raise CorruptedDataError("Item file is empty or corrupted")

    items = {}
    blocks = content.split("\n\n")

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        item = parse_item_block(lines)
        validate_item_data(item)
        items[item["item_id"]] = item

    return items

def validate_quest_data(quest_dict):
    required = [
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    ]

    for key in required:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Missing quest field: {key}")

    # Check numeric fields
    try:
        int(quest_dict["reward_xp"])
        int(quest_dict["reward_gold"])
        int(quest_dict["required_level"])
    except ValueError:
        raise InvalidDataFormatError("Quest numeric fields must be integers")

    return True

def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields
    
    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or invalid type
    """
    required = ["item_id", "name", "type", "effect", "cost", "description"]

    for key in required:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Missing item field: {key}")

    if item_dict["type"] not in ["weapon", "armor", "consumable"]:
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")

    try:
        int(item_dict["cost"])
    except ValueError:
        raise InvalidDataFormatError("Item cost must be an integer")

    return True

def create_default_data_files():
    """
    Create default data files if they don't exist
    This helps with initial setup and testing
    """
    os.makedirs("data", exist_ok=True)

    if not os.path.exists("data/quests.txt"):
        with open("data/quests.txt", "w", encoding="utf-8") as f:
            f.write(
                "QUEST_ID: first_steps\n"
                "TITLE: First Steps\n"
                "DESCRIPTION: Begin your journey.\n"
                "REWARD_XP: 25\n"
                "REWARD_GOLD: 10\n"
                "REQUIRED_LEVEL: 1\n"
                "PREREQUISITE: NONE\n\n"

                "QUEST_ID: goblin_hunter\n"
                "TITLE: Goblin Hunter\n"
                "DESCRIPTION: Clear out goblins.\n"
                "REWARD_XP: 150\n"
                "REWARD_GOLD: 50\n"
                "REQUIRED_LEVEL: 2\n"
                "PREREQUISITE: first_steps\n\n"

                "QUEST_ID: dragon_slayer\n"
                "TITLE: Dragon Slayer\n"
                "DESCRIPTION: Defeat the dragon.\n"
                "REWARD_XP: 500\n"
                "REWARD_GOLD: 300\n"
                "REQUIRED_LEVEL: 3\n"
                "PREREQUISITE: goblin_hunter\n"
            )

    if not os.path.exists("data/items.txt"):
        with open("data/items.txt", "w", encoding="utf-8") as f:
            f.write(
                "ITEM_ID: health_potion\n"
                "NAME: Health Potion\n"
                "TYPE: consumable\n"
                "EFFECT: health:20\n"
                "COST: 25\n"
                "DESCRIPTION: Restores 20 HP.\n\n"

                "ITEM_ID: iron_sword\n"
                "NAME: Iron Sword\n"
                "TYPE: weapon\n"
                "EFFECT: strength:5\n"
                "COST: 100\n"
                "DESCRIPTION: A sturdy iron blade.\n\n"

                "ITEM_ID: leather_armor\n"
                "NAME: Leather Armor\n"
                "TYPE: armor\n"
                "EFFECT: max_health:10\n"
                "COST: 80\n"
                "DESCRIPTION: Light protective armor.\n"
            )
    # TODO: Implement this function
    # Create data/ directory if it doesn't exist
    # Create default quests.txt and items.txt files
    # Handle any file permission errors appropriately

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary
    
    Args:
        lines: List of strings representing one quest
    
    Returns: Dictionary with quest data
    Raises: InvalidDataFormatError if parsing fails
    """
    quest = {}

    for line in lines:
        if ": " not in line:
            raise InvalidDataFormatError(f"Invalid quest line: {line}")

        key, value = line.split(": ", 1)
        key = key.lower().strip()
        value = value.strip()

        if key in ["reward_xp", "reward_gold", "required_level"]:
            value = int(value)

        if key == "prerequisite":
            value = "NONE" if value.upper() == "NONE" else value

        quest[key] = value

    return quest

def parse_item_block(lines):

    item = {}

    for line in lines:
        if ": " not in line:
            raise InvalidDataFormatError(f"Invalid item line: {line}")

        key, value = line.split(": ", 1)
        key = key.lower().strip()
        value = value.strip()

        if key == "cost":
            value = int(value)

        item[key] = value

    return item
    # TODO: Implement parsing logic


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    # try:
    #     quests = load_quests()
    #     print(f"Loaded {len(quests)} quests")
    # except MissingDataFileError:
    #     print("Quest file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid quest format: {e}")
    
    # Test loading items
    # try:
    #     items = load_items()
    #     print(f"Loaded {len(items)} items")
    # except MissingDataFileError:
    #     print("Item file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid item format: {e}")


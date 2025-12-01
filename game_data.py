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
    """
    Load and parse quest data from a text file.

    Each quest is stored in a block separated by blank lines.
    The function validates existence of the file, parses each block,
    performs structural validation, and returns a dictionary of quests.
    """

    # Ensure file exists before opening
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Missing file: {filename}")

    try:
        # Read entire file content as a string
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        # Any I/O issue is considered corruption
        raise CorruptedDataError("Error reading quests file")

    # Empty file = invalid
    if not content:
        raise CorruptedDataError("Quest file is empty or corrupted")

    quests = {}

    # Quests are separated by double newlines; split into blocks
    blocks = content.split("\n\n")

    # Parse each individual quest block
    for block in blocks:
        # Remove blank lines and strip whitespace
        lines = [line.strip() for line in block.split("\n") if line.strip()]

        # Convert the block into a quest dictionary
        quest = parse_quest_block(lines)

        # Validate required fields and types
        validate_quest_data(quest)

        # Store parsed quest using its ID as the key
        quests[quest["quest_id"]] = quest

    return quests


def load_items(filename="data/items.txt"):
    """
    Load and parse item data from a text file.

    Items are stored in blocks separated by blank lines.
    Validates structure and returns dictionary keyed by item_id.
    """

    # Ensure item data file exists
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Missing file: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        raise CorruptedDataError("Error reading items file")

    # File missing or empty = corruption
    if not content:
        raise CorruptedDataError("Item file is empty or corrupted")

    items = {}

    # Items separated into blocks via blank lines
    blocks = content.split("\n\n")

    for block in blocks:
        # Clean lines and ignore empty ones
        lines = [line.strip() for line in block.split("\n") if line.strip()]

        # Convert block into a structured dictionary
        item = parse_item_block(lines)

        # Ensure required keys and valid formats
        validate_item_data(item)

        # Store item using its ID as dictionary key
        items[item["item_id"]] = item

    return items


def validate_quest_data(quest_dict):
    """
    Ensure that a parsed quest dictionary contains all required fields
    and that numeric fields contain valid integer values.

    Raises InvalidDataFormatError for missing or invalid data.
    """

    # Required keys a quest must include
    required = [
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    ]

    # Check presence of each required field
    for key in required:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Missing quest field: {key}")

    # Validate numeric data types
    try:
        int(quest_dict["reward_xp"])
        int(quest_dict["reward_gold"])
        int(quest_dict["required_level"])
    except ValueError:
        raise InvalidDataFormatError("Quest numeric fields must be integers")

    return True


def validate_item_data(item_dict):
    """
    Validate item dictionary structure and values.

    Required fields include:
        item_id, name, type, effect, cost, description
    
    Valid item types:
        weapon, armor, consumable

    Ensures cost is a valid integer.

    Raises InvalidDataFormatError on validation failure.
    """

    required = ["item_id", "name", "type", "effect", "cost", "description"]

    # Check for missing required fields
    for key in required:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Missing item field: {key}")

    # Ensure item type is one of the allowed types
    if item_dict["type"] not in ["weapon", "armor", "consumable"]:
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")

    # Validate numeric cost
    try:
        int(item_dict["cost"])
    except ValueError:
        raise InvalidDataFormatError("Item cost must be an integer")

    return True


def create_default_data_files():
    """
    Create the 'data' directory and default quests/items files if they do not exist.
    Helps with first-time setup or automated testing environments.
    """

    # Create directory if missing
    os.makedirs("data", exist_ok=True)

    # Write default quest data only if file does not exist
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

    # Write default item data only if file does not exist
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

    # NOTE: Additional error handling (permission errors, filesystem failures)
    # could be added here if desired.


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Convert a list of text lines representing a single quest block
    into a structured quest dictionary.

    Converts numeric fields and normalizes prerequisite field.
    Raises InvalidDataFormatError for incorrectly formatted lines.
    """

    quest = {}

    for line in lines:
        # Ensure the line contains a valid key-value separator
        if ": " not in line:
            raise InvalidDataFormatError(f"Invalid quest line: {line}")

        # Split only at the first ": " to allow colons in descriptions
        key, value = line.split(": ", 1)

        key = key.lower().strip()
        value = value.strip()

        # Convert specific keys to integers
        if key in ["reward_xp", "reward_gold", "required_level"]:
            value = int(value)

        # Normalize prerequisite (accept "NONE" but keep uppercase)
        if key == "prerequisite":
            value = "NONE" if value.upper() == "NONE" else value

        # Store parsed value
        quest[key] = value

    return quest


def parse_item_block(lines):
    """
    Convert a list of text lines representing a single item
    into a structured item dictionary.

    Converts cost to integer. Ensures formatting correctness.
    """

    item = {}

    for line in lines:
        if ": " not in line:
            raise InvalidDataFormatError(f"Invalid item line: {line}")

        key, value = line.split(": ", 1)

        key = key.lower().strip()
        value = value.strip()

        # Convert cost field to integer
        if key == "cost":
            value = int(value)

        item[key] = value

    return item


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


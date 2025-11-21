"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import MissingDataFileError, InvalidDataFormatError

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quests from a file.
    Returns a dictionary: quest_id -> quest_data dict
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"File not found: {filename}")

    quests = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Expecting format: id|name|description|required_level|reward_gold
                parts = line.split("|")
                if len(parts) != 5:
                    raise InvalidDataFormatError(f"Invalid quest format: {line}")
                quest_id = parts[0].strip()
                quests[quest_id] = {
                    "name": parts[1].strip(),
                    "description": parts[2].strip(),
                    "required_level": int(parts[3].strip()),
                    "reward_gold": int(parts[4].strip()),
                }
    except ValueError as ve:
        raise InvalidDataFormatError(f"Invalid data type in file {filename}: {ve}")
    return quests

# ============================================================================
# ITEM DATA
# ============================================================================

def load_items(filename="data/items.txt"):
    """
    Load items from a file.
    Returns a dictionary: item_id -> item_data dict
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"File not found: {filename}")

    items = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Expecting format: id|name|type|value
                parts = line.split("|")
                if len(parts) != 4:
                    raise InvalidDataFormatError(f"Invalid item format: {line}")
                item_id = parts[0].strip()
                items[item_id] = {
                    "name": parts[1].strip(),
                    "type": parts[2].strip(),
                    "value": int(parts[3].strip()),
                }
    except ValueError as ve:
        raise InvalidDataFormatError(f"Invalid data type in file {filename}: {ve}")
    return items

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_data(quest_dict):
    required = ["quest_id", "title", "description",
                "reward_xp", "reward_gold",
                "required_level", "prerequisite"]

    for key in required:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Quest missing required field: {key}")

    if not isinstance(quest_dict["quest_id"], (int, str)):
        raise InvalidDataFormatError("quest_id must be string or integer")

    for key in ("reward_xp", "reward_gold", "required_level"):
        if not isinstance(quest_dict[key], int):
            raise InvalidDataFormatError(f"{key} must be integer")

    prereq = quest_dict.get("prerequisite")
    if prereq is not None and not isinstance(prereq, (int, str)):
        raise InvalidDataFormatError("prerequisite must be int, string, or None")

    return True



def validate_item_data(item_dict):
    required = ["item_id", "name", "type", "effect", "cost", "description"]

    for key in required:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Item missing required field: {key}")

    if not isinstance(item_dict["item_id"], (int, str)):
        raise InvalidDataFormatError("item_id must be string or integer")

    if not isinstance(item_dict["type"], str):
        raise InvalidDataFormatError("type must be string")

    effect = item_dict["effect"]
    if not isinstance(effect, str) or ":" not in effect:
        raise InvalidDataFormatError("effect must be in 'stat:value' format")

    if not isinstance(item_dict["cost"], int):
        raise InvalidDataFormatError("cost must be integer")

    return True


# ============================================================================
# HELPER PARSERS
# ============================================================================

def parse_quest_block(lines):
    if isinstance(lines, str):
        raw_lines = [ln.strip() for ln in lines.splitlines() if ln.strip()]
    else:
        raw_lines = [ln.strip() for ln in lines if ln and ln.strip()]

    data = {}
    for line in raw_lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid quest line: {line}")

        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        if key == "QUEST_ID":
            data["quest_id"] = int(val) if val.isdigit() else val
        elif key == "PREREQUISITE":
            if val.upper() == "NONE":
                data["prerequisite"] = None
            else:
                data["prerequisite"] = int(val) if val.isdigit() else val
        elif key in ("REWARD_XP", "REWARD_GOLD", "REQUIRED_LEVEL"):
            try:
                data[key.lower()] = int(val)
            except:
                raise InvalidDataFormatError(f"{key} must be integer")
        else:
            data[key.lower()] = val

    validate_quest_data(data)
    return data


def parse_item_block(lines):
    if isinstance(lines, str):
        raw_lines = [ln.strip() for ln in lines.splitlines() if ln.strip()]
    else:
        raw_lines = [ln.strip() for ln in lines if ln and ln.strip()]

    data = {}
    for line in raw_lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid item line: {line}")

        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        if key == "ITEM_ID":
            data["item_id"] = int(val) if val.isdigit() else val
        elif key == "TYPE":
            data["type"] = val.lower()
        elif key == "EFFECT":
            data["effect"] = val
        elif key == "COST":
            try:
                data["cost"] = int(val)
            except:
                raise InvalidDataFormatError("Cost must be integer")
        else:
            data[key.lower()] = val

    validate_item_data(data)
    return data

def _split_into_blocks(raw):
    return [b for b in raw.split("\n\n") if b.strip()]



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


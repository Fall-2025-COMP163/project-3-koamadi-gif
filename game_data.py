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
    Format per line:
    quest_id|title|description|reward_xp|reward_gold|required_level|prerequisite
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest data file '{filename}' not found")

    quests = {}

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) != 7:
                raise InvalidDataFormatError("Quest data format invalid")

            quest_id, title, desc, reward_xp, reward_gold, req_lvl, prereq = parts

            try:
                quests[quest_id] = {
                    "quest_id": quest_id,
                    "title": title,
                    "description": desc,
                    "reward_xp": int(reward_xp),
                    "reward_gold": int(reward_gold),
                    "required_level": int(req_lvl),
                    "prerequisite": prereq,
                }
            except ValueError:
                raise InvalidDataFormatError("Numeric field invalid in quest data")

    return quests

# ============================================================================
# ITEM DATA
# ============================================================================

def load_items(filename="data/items.txt"):
    """
    Load items from a file.
    Format per line:
    item_id|type|cost|effect
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item data file '{filename}' not found")

    items = {}

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) != 4:
                raise InvalidDataFormatError("Item data format invalid")

            item_id, type_, cost, effect = parts

            try:
                items[item_id] = {
                    "item_id": item_id,
                    "type": type_,
                    "cost": int(cost),
                    "effect": effect,
                }
            except ValueError:
                raise InvalidDataFormatError("Numeric field invalid in item data")

    return items

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_data(data):
    required_keys = [
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite",
    ]

    for key in required_keys:
        if key not in data:
            return False

    # All fields present & assumed valid
    return True



def validate_item_data(data):
    required_keys = ["item_id", "type", "cost", "effect"]

    for key in required_keys:
        if key not in data:
            return False

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


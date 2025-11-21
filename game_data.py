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
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quests file '{filename}' not found.")

    quests = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) != 7:
                    raise InvalidDataFormatError("Quest line does not have 7 fields.")
                quest_id, title, description, reward_xp, reward_gold, required_level, prerequisite = parts
                try:
                    reward_xp = int(reward_xp)
                    reward_gold = int(reward_gold)
                    required_level = int(required_level)
                except ValueError:
                    raise InvalidDataFormatError("Numeric field has invalid format in quest.")
                quest = {
                    "quest_id": quest_id,
                    "title": title,
                    "description": description,
                    "reward_xp": reward_xp,
                    "reward_gold": reward_gold,
                    "required_level": required_level,
                    "prerequisite": prerequisite
                }
                quests[quest_id] = quest
        return quests
    except UnicodeDecodeError:
        raise InvalidDataFormatError("File encoding unreadable.")
    except InvalidDataFormatError:
        raise
    except Exception as e:
        # Any other I/O error treat as missing/unreadable for tests
        raise InvalidDataFormatError(f"Unable to load quests: {e}")

def load_items(filename="data/items.txt"):
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Items file '{filename}' not found.")

    items = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) < 3:
                    raise InvalidDataFormatError("Item line does not have enough fields.")
                # Allow optional cost
                item_id = parts[0]
                item_type = parts[1]
                effect = parts[2] if len(parts) >= 3 else ""
                cost = None
                if len(parts) >= 4 and parts[3] != "":
                    try:
                        cost = int(parts[3])
                    except ValueError:
                        raise InvalidDataFormatError("Item cost must be integer.")
                items[item_id] = {"type": item_type, "effect": effect, "cost": cost}
        return items
    except UnicodeDecodeError:
        raise InvalidDataFormatError("File encoding unreadable.")
    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise InvalidDataFormatError(f"Unable to load items: {e}")

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



def validate_quest_data(quest: dict) -> bool:
    required_keys = {"quest_id", "title", "description", "reward_xp", "reward_gold", "required_level", "prerequisite"}
    if not isinstance(quest, dict):
        raise InvalidDataFormatError("Quest must be a dict.")
    if not required_keys.issubset(set(quest.keys())):
        raise InvalidDataFormatError("Quest missing required fields.")
    # numeric checks
    try:
        int(quest["reward_xp"])
        int(quest["reward_gold"])
        int(quest["required_level"])
    except (TypeError, ValueError):
        raise InvalidDataFormatError("Quest numeric fields invalid.")
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


"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles loading and validating game data from text files.
"""

import os
import errno

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
        raise MissingDataFileError(f"Quest data file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise MissingDataFileError(f"Quest data file not found: {filename}")
    except PermissionError as pe:
        raise CorruptedDataError(f"Permission denied reading quests file: {pe}")
    except Exception as e:
        raise CorruptedDataError(f"Failed to read quests file: {e}")

    try:
        blocks = _split_into_blocks(raw)
        quests = []
        for block in blocks:
            if not block.strip():
                continue
            q = parse_quest_block(block)
            quests.append(q)
        return quests  # changed: return LIST not dict
    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise InvalidDataFormatError(f"Failed to parse quests file: {e}")  # changed error type


def load_items(filename="data/items.txt"):
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item data file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise MissingDataFileError(f"Item data file not found: {filename}")
    except PermissionError as pe:
        raise CorruptedDataError(f"Permission denied reading items file: {pe}")
    except Exception as e:
        raise CorruptedDataError(f"Failed to read items file: {e}")

    try:
        blocks = _split_into_blocks(raw)
        items = {}
        for block in blocks:
            if not block.strip():
                continue
            it = parse_item_block(block)
            items[it["item_id"]] = it
        return items
    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise InvalidDataFormatError(f"Failed to parse items file: {e}")  # consistent behavior


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

    # allow quest_id as string OR int
    if not isinstance(quest_dict["quest_id"], (int, str)):
        raise InvalidDataFormatError("quest_id must be string or integer")

    # numeric fields still must be ints
    for key in ("reward_xp", "reward_gold", "required_level"):
        if not isinstance(quest_dict[key], int):
            raise InvalidDataFormatError(f"{key} must be integer")

    # prerequisite may be None, int, or string ID
    prereq = quest_dict.get("prerequisite")
    if prereq is not None and not isinstance(prereq, (int, str)):
        raise InvalidDataFormatError("prerequisite must be int, string, or None")

    return True


# ============================================================================
# HELPER FUNCTIONS (PARSERS)
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
            # allow string OR integer
            if val.isdigit():
                data["quest_id"] = int(val)
            else:
                data["quest_id"] = val

        elif key == "PREREQUISITE":
            if val.upper() == "NONE":
                data["prerequisite"] = None
            else:
                # string prereqs allowed
                if val.isdigit():
                    data["prerequisite"] = int(val)
                else:
                    data["prerequisite"] = val

        elif key in ("REWARD_XP", "REWARD_GOLD", "REQUIRED_LEVEL"):
            try:
                data[key.lower()] = int(val)
            except ValueError:
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
            try:
                data["item_id"] = int(val)
            except ValueError:
                raise InvalidDataFormatError("ITEM_ID must be integer")

        elif key == "TYPE":
            data["type"] = val.lower()

        elif key == "EFFECT":
            if ":" not in val:
                raise InvalidDataFormatError("Effect format invalid")
            stat, sval = val.split(":", 1)
            try:
                data["effect"] = {stat: int(sval)}
            except:
                raise InvalidDataFormatError("Effect value must be integer")

        elif key == "COST":
            try:
                data["cost"] = int(val)
            except:
                raise InvalidDataFormatError("Cost must be integer")

        else:
            data[key.lower()] = val

    validate_item_data(data)
    return data


# internal helper
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


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
    """
    Load quest data from file and return dict keyed by integer quest_id:
        { quest_id_int: { 'quest_id': quest_id_int, 'title': ..., ... } }

    Raises:
        MissingDataFileError: file doesn't exist
        InvalidDataFormatError: content doesn't match expected format
        CorruptedDataError: other IO errors (permissions, read errors)
    """
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
        # Split into blocks separated by one or more blank lines
        blocks = _split_into_blocks(raw)
        quests = {}
        for block in blocks:
            if not block:
                continue
            q = parse_quest_block(block)
            qid = q["quest_id"]
            if qid in quests:
                raise InvalidDataFormatError(f"Duplicate quest_id found: {qid}")
            quests[qid] = q
        return quests
    except InvalidDataFormatError:
        # re-raise format errors directly
        raise
    except Exception as e:
        # Any other unexpected parsing errors
        raise CorruptedDataError(f"Failed to parse quests file: {e}")


def load_items(filename="data/items.txt"):
    """
    Load item data from file and return dict keyed by integer item_id:
        { item_id_int: { 'item_id': item_id_int, 'name': ..., ... } }

    Raises:
        MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
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
            if not block:
                continue
            it = parse_item_block(block)
            iid = it["item_id"]
            if iid in items:
                raise InvalidDataFormatError(f"Duplicate item_id found: {iid}")
            items[iid] = it
        return items
    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise CorruptedDataError(f"Failed to parse items file: {e}")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_data(quest_dict):
    """
    Validate a single quest dict (as returned by parse_quest_block)
    Required fields: quest_id, title, description, reward_xp, reward_gold, required_level, prerequisite
    """
    required = ["quest_id", "title", "description", "reward_xp", "reward_gold", "required_level", "prerequisite"]
    for key in required:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Quest missing required field: {key}")

    # check types
    if not isinstance(quest_dict["quest_id"], int):
        raise InvalidDataFormatError("quest_id must be an integer")

    for num_key in ("reward_xp", "reward_gold", "required_level"):
        val = quest_dict.get(num_key)
        if not isinstance(val, int):
            raise InvalidDataFormatError(f"{num_key} must be an integer for quest {quest_dict.get('quest_id')}")

    # prerequisite can be None or int
    prereq = quest_dict.get("prerequisite")
    if prereq is not None and not isinstance(prereq, int):
        raise InvalidDataFormatError("prerequisite must be integer quest id or None")

    return True


def validate_item_data(item_dict):
    """
    Validate a single item dict
    Required fields: item_id, name, type, effect (dict), cost, description
    Valid types: weapon, armor, consumable
    """
    required = ["item_id", "name", "type", "effect", "cost", "description"]
    for key in required:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Item missing required field: {key}")

    if not isinstance(item_dict["item_id"], int):
        raise InvalidDataFormatError("item_id must be an integer")

    if item_dict["type"] not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError(f"Invalid item type '{item_dict['type']}' for item {item_dict['item_id']}")

    # effect should be a dict of {stat_name: int}
    if not isinstance(item_dict["effect"], dict):
        raise InvalidDataFormatError(f"Item effect must be a dict for item {item_dict['item_id']}")
    for k, v in item_dict["effect"].items():
        if not isinstance(v, int):
            raise InvalidDataFormatError(f"Item effect values must be integers (item {item_dict['item_id']}, effect {k})")

    if not isinstance(item_dict["cost"], int):
        raise InvalidDataFormatError(f"Item cost must be an integer for item {item_dict['item_id']}")

    return True


# ============================================================================
# DEFAULT FILE CREATION
# ============================================================================

def create_default_data_files():
    """
    Create default data directory and sample files if they don't exist.
    Returns: None
    Raises: CorruptedDataError on write/permission errors
    """
    data_dir = "data"
    try:
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir, exist_ok=True)
    except PermissionError as pe:
        raise CorruptedDataError(f"Cannot create data directory '{data_dir}': {pe}")
    except Exception as e:
        raise CorruptedDataError(f"Failed to create data directory '{data_dir}': {e}")

    # default quests
    quests_path = os.path.join(data_dir, "quests.txt")
    if not os.path.exists(quests_path):
        try:
            with open(quests_path, "w", encoding="utf-8") as f:
                f.write(
"""QUEST_ID: 1
TITLE: The Beginning
DESCRIPTION: Speak to the village elder to begin your journey.
REWARD_XP: 50
REWARD_GOLD: 20
REQUIRED_LEVEL: 1
PREREQUISITE: NONE

QUEST_ID: 2
TITLE: Goblin Trouble
DESCRIPTION: Clear out the goblin camp to the east.
REWARD_XP: 100
REWARD_GOLD: 40
REQUIRED_LEVEL: 2
PREREQUISITE: 1
""")
        except PermissionError as pe:
            raise CorruptedDataError(f"Cannot write default quests file: {pe}")
        except Exception as e:
            raise CorruptedDataError(f"Failed to write default quests file: {e}")

    # default items
    items_path = os.path.join(data_dir, "items.txt")
    if not os.path.exists(items_path):
        try:
            with open(items_path, "w", encoding="utf-8") as f:
                f.write(
"""ITEM_ID: 1
NAME: Rusty Sword
TYPE: weapon
EFFECT: strength:5
COST: 15
DESCRIPTION: An old sword with a bit of bite.

ITEM_ID: 2
NAME: Small Potion
TYPE: consumable
EFFECT: health:30
COST: 10
DESCRIPTION: Restores a small amount of health.

ITEM_ID: 3
NAME: Leather Armor
TYPE: armor
EFFECT: strength:1
COST: 25
DESCRIPTION: Basic protection for new adventurers.
""")
        except PermissionError as pe:
            raise CorruptedDataError(f"Cannot write default items file: {pe}")
        except Exception as e:
            raise CorruptedDataError(f"Failed to write default items file: {e}")


# ============================================================================
# HELPER FUNCTIONS (PARSERS)
# ============================================================================

def parse_quest_block(lines):
    """
    Parse a block (string or list-of-lines) into a quest dictionary.
    Accepts both a single multi-line string or a list of stripped lines.
    Returns validated quest dict with integer quest_id and numeric fields as ints.
    """
    if isinstance(lines, str):
        raw_lines = [ln.strip() for ln in lines.splitlines() if ln.strip() != ""]
    else:
        raw_lines = [ln.strip() for ln in lines if ln and ln.strip() != ""]

    data = {}
    for line in raw_lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid line in quest block (no ':'): '{line}'")
        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()
        if key == "QUEST_ID":
            # convert to int (user chose option B)
            try:
                data["quest_id"] = int(val)
            except ValueError:
                raise InvalidDataFormatError(f"QUEST_ID must be integer, got '{val}'")
        elif key == "TITLE":
            data["title"] = val
        elif key == "DESCRIPTION":
            data["description"] = val
        elif key == "REWARD_XP":
            try:
                data["reward_xp"] = int(val)
            except ValueError:
                raise InvalidDataFormatError(f"REWARD_XP must be integer, got '{val}'")
        elif key == "REWARD_GOLD":
            try:
                data["reward_gold"] = int(val)
            except ValueError:
                raise InvalidDataFormatError(f"REWARD_GOLD must be integer, got '{val}'")
        elif key == "REQUIRED_LEVEL":
            try:
                data["required_level"] = int(val)
            except ValueError:
                raise InvalidDataFormatError(f"REQUIRED_LEVEL must be integer, got '{val}'")
        elif key == "PREREQUISITE":
            # "NONE" -> None, otherwise integer (user chose integer IDs)
            if val.upper() == "NONE":
                data["prerequisite"] = None
            else:
                try:
                    data["prerequisite"] = int(val)
                except ValueError:
                    raise InvalidDataFormatError(f"PREREQUISITE must be integer quest id or NONE, got '{val}'")
        else:
            # unknown keys can be stored but not required
            data[key.lower()] = val

    # Validate required fields
    try:
        validate_quest_data(data)
    except InvalidDataFormatError:
        # re-raise with context
        raise
    return data


def parse_item_block(lines):
    """
    Parse a block (string or list-of-lines) into an item dictionary.
    Returns validated item dict with integer item_id and numeric fields as ints.
    EFFECT is parsed to a dict preserving original stat case (user chose B).
    """
    if isinstance(lines, str):
        raw_lines = [ln.strip() for ln in lines.splitlines() if ln.strip() != ""]
    else:
        raw_lines = [ln.strip() for ln in lines if ln and ln.strip() != ""]

    data = {}
    for line in raw_lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Invalid line in item block (no ':'): '{line}'")
        key, val = line.split(":", 1)
        key = key.strip().upper()
        val = val.strip()
        if key == "ITEM_ID":
            try:
                data["item_id"] = int(val)
            except ValueError:
                raise InvalidDataFormatError(f"ITEM_ID must be integer, got '{val}'")
        elif key == "NAME":
            data["name"] = val
        elif key == "TYPE":
            data["type"] = val.lower()
        elif key == "EFFECT":
            # Expect format stat:value (single effect). Preserve case of stat name.
            if ":" not in val:
                raise InvalidDataFormatError(f"EFFECT must be in 'stat:value' format, got '{val}'")
            stat, sval = val.split(":", 1)
            stat = stat.strip()  # preserve case per user choice
            sval = sval.strip()
            try:
                ival = int(sval)
            except ValueError:
                raise InvalidDataFormatError(f"EFFECT value must be integer, got '{sval}' for stat '{stat}'")
            data["effect"] = {stat: ival}
        elif key == "COST":
            try:
                data["cost"] = int(val)
            except ValueError:
                raise InvalidDataFormatError(f"COST must be integer, got '{val}'")
        elif key == "DESCRIPTION":
            data["description"] = val
        else:
            # unknown keys stored under lowercase
            data[key.lower()] = val

    # Validate required fields
    try:
        validate_item_data(data)
    except InvalidDataFormatError:
        raise
    return data


# ============================================================================
# UTILITY: split text into blocks separated by blank lines
# ============================================================================

def _split_into_blocks(text):
    """
    Splits a text blob into blocks separated by blank lines.
    Returns a list of strings (each block).
    """
    lines = text.splitlines()
    blocks = []
    current = []
    for ln in lines:
        if ln.strip() == "":
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(ln)
    if current:
        blocks.append("\n".join(current))
    return blocks


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


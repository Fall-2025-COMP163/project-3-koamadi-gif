"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles character creation, loading, and saving.
"""
import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    # TODO: Implement character creation
    classes = {
        "Warrior": {"health": 120, "strength": 20, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15}
    }

    if character_class not in valid_classes:
        raise InvalidCharacterClassError(
            f"'{character_class}' is not a valid class. "
            f"Valid classes: {', '.join(classes.keys())}"
        )

    stats = classes[character_class]

    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }


def save_character(character, save_directory="data/save_games"):
    os.makedirs(save_directory, exist_ok=True)
    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            for key, value in character.items():
                key_str = key.upper()  # required by tests
                f.write(f"{key_str}: {value}\n")
        return True
    except Exception as e:
        raise SaveFileCorruptedError(str(e))
    
    except Exception as e:
        raise SaveFileCorruptedError(str(e))
    
    # TODO: Implement save functionality
    # Create save_directory if it doesn't exist
    # Handle any file I/O errors appropriately
    # Lists should be saved as comma-separated values

def load_character(character_name, save_directory="data/save_games"):
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save found for {character_name}.")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        raise SaveFileCorruptedError(str(e))

    data = {}

    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if ": " not in line:
                raise InvalidSaveDataError("Invalid line in save file.")

            key, value = line.split(": ", 1)
            key = key.strip().lower()
            data[key] = value.strip()
    except InvalidSaveDataError:
        raise
    except Exception as e:
        raise SaveFileCorruptedError(str(e))

    # Convert lists saved as strings
    def parse_list(value):
        return [] if value == "" else [x for x in value.split(",")]

    character = {
        "name": data["name"],
        "class": data["class"],
        "level": int(data["level"]),
        "health": int(data["health"]),
        "max_health": int(data["max_health"]),
        "strength": int(data["strength"]),
        "magic": int(data["magic"]),
        "experience": int(data["experience"]),
        "gold": int(data["gold"]),
        "inventory": parse_list(data.get("inventory", "")),
        "active_quests": parse_list(data.get("active_quests", "")),
        "completed_quests": parse_list(data.get("completed_quests", ""))
    }

    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    
    Returns: List of character names (without _save.txt extension)
    """
    # TODO: Implement this function
    if not os.path.exists(save_directory):
        return []

    entries = []
    try:
        for fn in os.listdir(save_directory):
            if fn.endswith("_save.txt"):
                entries.append(fn[:-9])  # remove "_save.txt"
    except Exception:
        # If directory can't be read, return empty list rather than crashing
        return []

    return entries
    # Return empty list if directory doesn't exist
    # Extract character names from filenames

def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    
    Returns: True if deleted successfully
    Raises: CharacterNotFoundError if character doesn't exist
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"{character_name} does not exist.")

    os.remove(filename)
    return True

    # TODO: Implement character deletion
    # Verify file exists before attempting deletion

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot gain XP while dead.")

    character["experience"] += xp_amount

    leveled_up = False

    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]
        leveled_up = True

    return leveled_up
    # TODO: Implement experience gain and leveling
    # Check if character is dead first
    # Add experience
    # Check for level up (can level up multiple times)
    # Update stats on level up

def add_gold(character, amount):
    """
    Add gold to character's inventory
    
    Args:
        character: Character dictionary
        amount: Amount of gold to add (can be negative for spending)
    
    Returns: New gold total
    Raises: ValueError if result would be negative
    """
    new_total = character["gold"] + amount

    if new_total < 0:
        raise ValueError("Gold cannot go negative.")

    character["gold"] = new_total
    return character["gold"]

    # TODO: Implement gold management
    # Check that result won't be negative
    # Update character's gold

def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot heal a dead character.")

    original = character["health"]
    character["health"] = min(character["health"] + amount, character["max_health"])
    return character["health"] - original

    # TODO: Implement healing
    # Calculate actual healing (don't exceed max_health)
    # Update character health

def is_character_dead(character):
    """
    Check if character's health is 0 or below
    
    Returns: True if dead, False if alive
    """
    return character["health"] <= 0

    # TODO: Implement death check

def revive_character(character):
    """
    Revive a dead character with 50% health
    
    Returns: True if revived
    """
    if character["health"] > 0:
        return False
    
    character["health"] = character["max_health"] // 2

    return True
    # TODO: Implement revival
    # Restore health to half of max_health

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for key in required:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    for field in ["level", "health", "max_health", "strength", "magic", "experience", "gold"]:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field {field} must be an integer.")

    for field in ["inventory", "active_quests", "completed_quests"]:
        if not isinstance(character[field], list):
            raise InvalidSaveDataError(f"Field {field} must be a list.")

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
    #     print("Save file corrupted")


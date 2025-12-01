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
    """Create a new character with stats based on chosen class."""
    
    # Dictionary of allowed classes and their starting stats
    classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15}
    }

    # Validate that player-selected class exists
    if character_class not in classes:
        raise InvalidCharacterClassError(
            f"'{character_class}' is not a valid class. "
            f"Valid classes: {', '.join(classes.keys())}"
        )

    # Retrieve stat block for chosen class
    stats = classes[character_class]

    # Return fully constructed character dictionary
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
    """Save character data to a text file."""
    
    # Ensure save directory exists
    os.makedirs(save_directory, exist_ok=True)

    # Build full file path: e.g. /data/save_games/Bob_save.txt
    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    try:
        # Open save file in write mode
        with open(filename, "w", encoding="utf-8") as f:
            # Write each key-value pair on its own line
            for key, value in character.items():
                key_str = key.upper()  # required uppercase format for tests
                f.write(f"{key_str}: {value}\n")
        return True

    except Exception as e:
        # If anything goes wrong during saving, wrap error
        raise SaveFileCorruptedError(str(e))

    # NOTE: second except block below is redundant and unreachable
    except Exception as e:
        raise SaveFileCorruptedError(str(e))


def load_character(character_name, save_directory="data/save_games"):
    """Load character data from a save file."""
    
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    # Ensure save file exists
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save found for {character_name}.")

    # Attempt to read file contents
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        raise SaveFileCorruptedError(str(e))

    data = {}

    # Parse each line of save file
    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue  # skip blank lines

            if ": " not in line:
                raise InvalidSaveDataError("Invalid line in save file.")

            key, value = line.split(": ", 1)
            key = key.strip().lower()  # convert keys back to lowercase
            data[key] = value.strip()

    except InvalidSaveDataError:
        raise
    except Exception as e:
        raise SaveFileCorruptedError(str(e))

    # Convert comma-separated string to Python list
    def parse_list(value):
        return [] if value == "" else [x for x in value.split(",")]

    # Construct character dictionary with correct data types restored
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
    Return list of all saved characters (filenames without _save.txt).
    """
    
    # Return empty list if directory doesn't exist
    if not os.path.exists(save_directory):
        return []

    entries = []
    try:
        # Loop through all files in directory
        for fn in os.listdir(save_directory):
            if fn.endswith("_save.txt"):
                entries.append(fn[:-9])  # Remove "_save.txt" suffix

    except Exception:
        # If directory can't be read, prevent crash by returning empty list
        return []

    return entries


def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file.
    Raises error if file doesn't exist.
    """
    
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    # Ensure file exists before attempting deletion
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"{character_name} does not exist.")

    os.remove(filename)
    return True


# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """Add experience to character and handle leveling up."""
    
    # Cannot gain XP when dead
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot gain XP while dead.")

    # Add XP
    character["experience"] += xp_amount
    leveled_up = False

    # Level-up loop (can level multiple times)
    while character["experience"] >= character["level"] * 100:
        # Deduct XP required for this level
        character["experience"] -= character["level"] * 100
        
        # Increase level
        character["level"] += 1

        # Increase stats on level up
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2

        # Restore full health
        character["health"] = character["max_health"]

        leveled_up = True

    return leveled_up


def add_gold(character, amount):
    """
    Add or subtract gold from character.
    Raises ValueError if result would be negative.
    """
    
    new_total = character["gold"] + amount

    if new_total < 0:
        raise ValueError("Gold cannot go negative.")

    character["gold"] = new_total
    return character["gold"]


def heal_character(character, amount):
    """
    Heal character up to max health.
    Returns actual healed amount.
    """
    
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot heal a dead character.")

    original = character["health"]

    # Apply healing but do not exceed max health
    character["health"] = min(character["health"] + amount, character["max_health"])

    return character["health"] - original


def is_character_dead(character):
    """Return True if health is 0 or less."""
    return character["health"] <= 0


def revive_character(character):
    """
    Revive a dead character to 50% max health.
    Returns False if character was already alive.
    """
    
    if character["health"] > 0:
        return False  # already alive
    
    # Set health to half max
    character["health"] = character["max_health"] // 2
    return True


# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """Verify that loaded character data contains required fields and correct types."""
    
    # Required keys in a save file
    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    # Ensure all required fields exist
    for key in required:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    # Ensure numerical fields contain integers
    for field in ["level", "health", "max_health", "strength", "magic", "experience", "gold"]:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field {field} must be an integer.")

    # Ensure list fields contain lists
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


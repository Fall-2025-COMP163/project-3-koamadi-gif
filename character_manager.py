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
    valid_classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15}
    }

    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"{character_class} is not a valid class")

    stats = valid_classes[character_class]

    character = {
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

    return character


def save_character(character, save_directory="data/save_games"):
    os.makedirs(save_directory, exist_ok=True)
    file_path = os.path.join(save_directory, f"{character['name']}_save.txt")

    try:
        with open(file_path, "w") as file:
            for key, value in character.items():
                if isinstance(value, list):
                    value = ",".join(value)
                file.write(f"{key.upper()}: {value}\n")
        return True

    except (PermissionError, IOError):
        raise  # propagate as instructed


def load_character(character_name, save_directory="data/save_games"):
    file_path = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Save file for {character_name} does not exist.")

    try:
        character = {}
        with open(file_path, "r") as file:
            for line in file:
                if ": " not in line:
                    raise InvalidSaveDataError("Invalid save format")

                key, value = line.strip().split(": ", 1)
                key = key.lower()

                # convert lists
                if key in ["inventory", "active_quests", "completed_quests"]:
                    character[key] = value.split(",") if value else []
                # convert numbers
                elif key in ["level", "health", "max_health",
                             "strength", "magic", "experience", "gold"]:
                    character[key] = int(value)
                else:
                    character[key] = value

        validate_character_data(character)
        return character

    except UnicodeDecodeError:
        raise SaveFileCorruptedError("Save file unreadable")

    except ValueError:
        raise InvalidSaveDataError("Numeric field is invalid")


def list_saved_characters(save_directory="data/save_games"):
    if not os.path.exists(save_directory):
        return []
    
    names = []
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            name = filename.replace("_save.txt", "")
            names.append(name)
    return names


def delete_character(character_name, save_directory="data/save_games"):
    file_path = os.path.join(save_directory, f"{character_name}_save.txt")
    
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"No save found for {character_name}")

    os.remove(file_path)
    return True


# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    if is_character_dead(character):
        raise CharacterDeadError("Cannot gain XP while dead")

    character["experience"] += xp_amount

    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]
        print(f"🎉 {character['name']} leveled up! Now level {character['level']}")

    return character["experience"]


def add_gold(character, amount):
    new_gold = character["gold"] + amount
    if new_gold < 0:
        raise ValueError("Not enough gold!")
    character["gold"] = new_gold
    return new_gold


def heal_character(character, amount):
    old_hp = character["health"]
    character["health"] = min(character["max_health"], character["health"] + amount)
    return character["health"] - old_hp


def is_character_dead(character):
    return character["health"] <= 0


def revive_character(character):
    if not is_character_dead(character):
        return False
    character["health"] = character["max_health"] // 2
    return True


# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for field in required_fields:
        if field not in character:
            raise InvalidSaveDataError(f"Missing field: {field}")

    if not isinstance(character["inventory"], list):
        raise InvalidSaveDataError("Inventory must be a list")

    if not isinstance(character["active_quests"], list):
        raise InvalidSaveDataError("Active quests must be a list")

    if not isinstance(character["completed_quests"], list):
        raise InvalidSaveDataError("Completed quests must be a list")

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


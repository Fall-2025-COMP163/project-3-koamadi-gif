"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles character creation, loading, and saving.
"""
import os
from typing import Dict, Any
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================ #
# CONFIG / CONSTANTS
# ============================================================================ #

CHARACTER_CLASSES = {
    "Warrior": {"strength": 10, "defense": 8, "health": 120, "gold": 50},
    "Mage": {"strength": 4, "defense": 3, "health": 80, "gold": 10, "magic": 20, "mana": 30},
    "Rogue": {"strength": 7, "defense": 5, "health": 100, "gold": 40},
    "Cleric": {"strength": 6, "defense": 7, "health": 90, "gold": 20, "magic": 10, "mana": 20}
}

SAVE_DIR = "data/save_games"
os.makedirs(SAVE_DIR, exist_ok=True)


# ============================================================================ #
# CHARACTER CREATION / SAVE / LOAD
# ============================================================================ #

def create_character(name: str, char_class: str) -> Dict[str, Any]:
    if char_class not in CHARACTER_CLASSES:
        raise InvalidCharacterClassError(f"Invalid class: {char_class}")

    stats = CHARACTER_CLASSES[char_class].copy()
    character = {
        "name": name,
        "class": char_class,
        "level": 1,
        "experience": 0,
        "xp": 0,
        "gold": stats.get("gold", 0),
        "strength": stats.get("strength", 5),
        "defense": stats.get("defense", 5),
        "health": stats["health"],
        "max_health": stats["health"],
        "magic": stats.get("magic", 0),
        "mana": stats.get("mana", 0),
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    return character


def save_character(character: Dict[str, Any], filename: str):
    if character.get("health", 0) <= 0:
        raise CharacterDeadError("Cannot save a dead character")

    try:
        with open(filename, "w") as f:
            for key, value in character.items():
                if isinstance(value, list):
                    if value:
                        f.write(f"{key}: {','.join(value)}\n")
                    else:
                        f.write(f"{key}: NONE\n")
                else:
                    f.write(f"{key}: {value}\n")
    except Exception:
        raise InvalidSaveDataError("Failed to save character")


def load_character(filename: str) -> Dict[str, Any]:
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"Character file '{filename}' not found")

    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except Exception:
        raise InvalidSaveDataError("Unable to read character file")

    character = {}
    for line in lines:
        if ": " not in line:
            raise InvalidSaveDataError("Saved data incorrectly formatted")
        key, value = line.strip().split(": ", 1)

        if value == "NONE":
            character[key] = []
        elif "," in value:
            character[key] = value.split(",")
        else:
            try:
                character[key] = int(value)
            except ValueError:
                character[key] = value

    validate_character_data(character)

    if character.get("health", 0) <= 0:
        raise CharacterDeadError("Character is dead upon loading")

    return character


def list_saved_characters(save_directory: str = SAVE_DIR) -> list:
    if not os.path.exists(save_directory):
        return []
    return [f.replace("_save.txt", "") for f in os.listdir(save_directory) if f.endswith("_save.txt")]


def delete_character(character_name: str, save_directory: str = SAVE_DIR) -> bool:
    filename = f"{character_name}_save.txt"
    file_path = os.path.join(save_directory, filename)
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"No save found for {character_name}")
    os.remove(file_path)
    return True


# ============================================================================ #
# CHARACTER OPERATIONS
# ============================================================================ #

def is_character_dead(character: Dict[str, Any]) -> bool:
    return character.get("health", 0) <= 0


def gain_experience(character: Dict[str, Any], xp_amount: int) -> int:
    if is_character_dead(character):
        raise CharacterDeadError("Cannot gain XP while dead")

    character["xp"] = character.get("xp", character.get("experience", 0)) + xp_amount
    character["experience"] = character["xp"]

    while character["xp"] >= character["level"] * 100:
        character["xp"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2

        if character.get("magic", 0) or character.get("mana", 0):
            character["magic"] = character.get("magic", 0) + 5
            character["mana"] = character.get("mana", 0) + 5

        character["health"] = character["max_health"]

    character["experience"] = character["xp"]
    return character["xp"]


def add_gold(character: Dict[str, Any], amount: int) -> int:
    new_total = character.get("gold", 0) + amount
    if new_total < 0:
        raise ValueError("Not enough gold!")
    character["gold"] = new_total
    return new_total


def heal_character(character: Dict[str, Any], amount: int) -> int:
    if is_character_dead(character):
        return character.get("health", 0)

    character["health"] = min(character["max_health"], character["health"] + amount)
    return character["health"]


def revive_character(character: Dict[str, Any]) -> bool:
    if not is_character_dead(character):
        return False
    character["health"] = character["max_health"]
    return True


# ============================================================================ #
# VALIDATION
# ============================================================================ #

def validate_character_data(character: Dict[str, Any]) -> bool:
    required = [
        "name", "class", "level",
        "health", "max_health",
        "strength", "defense",
        "magic", "mana",
        "experience", "xp",
        "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for field in required:
        if field not in character:
            raise InvalidSaveDataError(f"Missing field: {field}")

    if not all(isinstance(character[field], list) for field in ["inventory", "active_quests", "completed_quests"]):
        raise InvalidSaveDataError("Inventory and quest fields must be lists")

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


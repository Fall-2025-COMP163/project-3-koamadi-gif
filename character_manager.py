"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles character creation, loading, and saving.
"""
import os
import json
from custom_exceptions import (
    CharacterNotFoundError,
    InvalidSaveDataError,
    InvalidCharacterClassError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER CLASSES
# ============================================================================

CHARACTER_CLASSES = {
    "Warrior": {"strength": 10, "defense": 8, "health": 100},
    "Mage": {"strength": 4, "defense": 5, "health": 70, "mana": 100},
    "Rogue": {"strength": 7, "defense": 6, "health": 80},
    "Cleric": {"strength": 5, "defense": 6, "health": 80, "mana": 80}  # Added for integration tests
}

SAVE_DIR = "data/save_games"
os.makedirs(SAVE_DIR, exist_ok=True)

# ============================================================================
# CHARACTER MANAGEMENT
# ============================================================================

def create_character(name, char_class):
    if char_class not in CHARACTER_CLASSES:
        raise InvalidCharacterClassError(f"{char_class} is not a valid class.")

    base_stats = CHARACTER_CLASSES[char_class]
    character = {
        "name": name,
        "class": char_class,
        "level": 1,
        "experience": 0,
        "gold": 0,
        "strength": base_stats["strength"],
        "defense": base_stats["defense"],
        "health": base_stats["health"],
        "max_health": base_stats["health"],
        "magic": base_stats.get("mana", 0),
        "inventory": [],
        "equipped": {},
        "active_quests": [],
        "completed_quests": []
    }
    return character

def save_character(character, save_directory=SAVE_DIR):
    file_path = os.path.join(save_directory, f"{character['name']}_save.txt")
    try:
        with open(file_path, "w") as file:
            json.dump(character, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving character: {e}")
        return False

def load_character(character_name, save_directory=SAVE_DIR):
    file_path = os.path.join(save_directory, f"{character_name}_save.txt")
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Save file for {character_name} does not exist.")
    try:
        with open(file_path, "r") as file:
            character = json.load(file)
        return character
    except json.JSONDecodeError:
        raise InvalidSaveDataError("Invalid save format")

def list_saved_characters(save_directory=SAVE_DIR):
    if not os.path.exists(save_directory):
        return []
    return [f.replace("_save.txt", "") for f in os.listdir(save_directory) if f.endswith("_save.txt")]

def delete_character(character_name, save_directory=SAVE_DIR):
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


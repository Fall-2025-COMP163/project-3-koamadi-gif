"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: Kobby Amadi

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    while True:
        print("\n=== MAIN MENU ===")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice in {"1", "2", "3"}:
            return int(choice)
        else:
            print("Invalid choice. Enter a number 1-3.")


def new_game():
    global current_character

    print("\n--- NEW GAME ---")
    name = input("Enter character name: ")
    char_class = input("Choose class (Warrior/Mage/Rogue): ")

    try:
        current_character = character_manager.create_character(name, char_class)
        print(f"Character created: {name} the {char_class}")
        game_loop()
    except InvalidCharacterClassError as e:
        print(f"Error: {e}")


def load_game():
    global current_character

    print("\n--- LOAD GAME ---")
    saved_characters = character_manager.list_saved_characters()

    if not saved_characters:
        print("No saved characters found.")
        return

    for i, char_name in enumerate(saved_characters, 1):
        print(f"{i}. {char_name}")

    try:
        index = int(input("Select a character: ")) - 1
        current_character = character_manager.load_character(saved_characters[index])
        print(f"Loaded {current_character.name}")
        game_loop()
    except (CharacterNotFoundError, SaveFileCorruptedError, ValueError, IndexError) as e:
        print(f"Error: {e}")


# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    global game_running
    game_running = True

    print(f"\nWelcome, {current_character.name}!")
    
    while game_running:
        try:
            choice = game_menu()
            if choice == 1: view_character_stats()
            elif choice == 2: view_inventory()
            elif choice == 3: quest_menu()
            elif choice == 4: explore()
            elif choice == 5: shop()
            elif choice == 6:
                save_game()
                print("Game saved. Goodbye!")
                game_running = False
        except Exception as e:
            print(f"Unexpected error: {e}")


def game_menu():
    while True:
        print("\n=== GAME MENU ===")
        print("1. View Stats")
        print("2. Inventory")
        print("3. Quests")
        print("4. Explore")
        print("5. Shop")
        print("6. Save & Quit")

        choice = input("Choose action: ")
        if choice in {"1","2","3","4","5","6"}:
            return int(choice)
        print("Invalid choice. Enter 1-6.")


# ============================================================================
# GAME ACTIONS (simple versions)
# ============================================================================

def view_character_stats():
    print("\n--- CHARACTER STATS ---")
    character_manager.display_stats(current_character)
    quest_handler.display_quest_progress(current_character)


def view_inventory():
    print("\n--- INVENTORY ---")
    inventory_system.display_inventory(current_character)


def quest_menu():
    print("\n--- QUESTS (WIP) ---")
    quest_handler.show_quests(current_character)


def explore():
    print("\nExploring the wilderness...")
    try:
        enemy = combat_system.generate_enemy(current_character.level)
        combat = combat_system.SimpleBattle(current_character, enemy)
        combat.start()
    except Exception as e:
        print(f"Combat error: {e}")


def shop():
    print("\nThe shop is currently under construction!")


# ============================================================================
# SAVE / LOAD DATA
# ============================================================================

def save_game():
    try:
        character_manager.save_character(current_character)
    except Exception as e:
        print(f"Save failed: {e}")


def load_game_data():
    global all_quests, all_items
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except (MissingDataFileError, InvalidDataFormatError):
        print("Data missing or corrupted. Creating defaults...")
        game_data.create_default_data_files()
        load_game_data()


def handle_character_death():
    global game_running
    print("\nYou died!")
    game_running = False

def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main game execution function"""
    
    # Display welcome message
    display_welcome()
    
    # Load game data
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()


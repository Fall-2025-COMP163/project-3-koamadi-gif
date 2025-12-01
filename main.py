"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

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

current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display main menu and get player choice.
    """
    print("\n=== MAIN MENU ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")

    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice in {"1", "2", "3"}:
            return int(choice)
        print("Invalid input. Choose 1-3.")

def new_game():
    """
    Start a new game.
    """
    global current_character

    print("\n=== NEW GAME ===")
    name = input("Enter character name: ").strip()

    print("\nChoose a class:")
    for c in character_manager.CHARACTER_CLASSES:
        print(f"- {c}")

    char_class = input("Enter class: ").strip()

    try:
        current_character = character_manager.create_character(name, char_class)
        character_manager.save_character(current_character)
        print(f"\nCharacter '{name}' created!")
        game_loop()

    except InvalidCharacterClassError:
        print("Invalid class! Returning to main menu.")

def load_game():
    """
    Load an existing character.
    """
    global current_character

    print("\n=== LOAD GAME ===")

    saved = character_manager.list_saved_characters()
    if not saved:
        print("No saved characters found.")
        return

    print("\nSaved Characters:")
    for i, c in enumerate(saved, start=1):
        print(f"{i}. {c}")

    while True:
        choice = input("Select character number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(saved):
            chosen_name = saved[int(choice) - 1]
            break
        print("Invalid selection.")

    try:
        current_character = character_manager.load_character(chosen_name)
        print(f"\nLoaded '{chosen_name}'!")
        game_loop()

    except (CharacterNotFoundError, InvalidSaveDataError) as e:
        print(f"Failed to load game: {e}")

# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """
    Main gameplay loop.
    """
    global game_running, current_character

    game_running = True

    while game_running:
        choice = game_menu()

        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            save_game()
            print("Game saved. Exiting to main menu.")
            game_running = False

        # Auto-save after each action
        character_manager.save_character(current_character)

def game_menu():
    """
    Display game menu.
    """
    print("\n=== GAME MENU ===")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore")
    print("5. Shop")
    print("6. Save & Quit")

    while True:
        choice = input("Choose (1-6): ").strip()
        if choice in {"1", "2", "3", "4", "5", "6"}:
            return int(choice)
        print("Invalid choice.")

# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    global current_character

    print("\n=== CHARACTER STATS ===")

    stats = character_manager.get_character_stats(current_character)

    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\nQuests:")
    active = quest_handler.get_active_quests(current_character)
    completed = quest_handler.get_completed_quests(current_character)

    print(f"- Active: {active}")
    print(f"- Completed: {completed}")

def view_inventory():
    global current_character

    print("\n=== INVENTORY ===")
    inv = current_character.inventory

    if not inv:
        print("Inventory is empty.")
        return

    for i, item in enumerate(inv, start=1):
        print(f"{i}. {item}")

    print("\nOptions:")
    print("1. Use Item")
    print("2. Drop Item")
    print("3. Back")

    choice = input("Choose (1-3): ").strip()

    if choice == "1":
        idx = input("Enter item number to use: ").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(inv):
            item_name = inv[int(idx)-1]
            try:
                inventory_system.use_item(current_character, item_name)
                print(f"Used {item_name}.")
            except (InvalidItemError, CharacterDeadError) as e:
                print(f"Error: {e}")
    elif choice == "2":
        idx = input("Enter item number to drop: ").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(inv):
            item_name = inv[int(idx)-1]
            inventory_system.remove_item(current_character, item_name)
            print(f"Dropped {item_name}.")
    else:
        return

def quest_menu():
    global current_character

    print("\n=== QUEST MENU ===")
    print("1. View Active Quests")
    print("2. View Available Quests")
    print("3. View Completed Quests")
    print("4. Accept Quest")
    print("5. Abandon Quest")
    print("6. Complete Quest (Testing)")
    print("7. Back")

    choice = input("Choose (1-7): ").strip()

    if choice == "1":
        print(quest_handler.get_active_quests(current_character))
    elif choice == "2":
        print(list(all_quests.keys()))
    elif choice == "3":
        print(quest_handler.get_completed_quests(current_character))
    elif choice == "4":
        q = input("Enter quest name: ").strip()
        try:
            quest_handler.accept_quest(current_character, q, all_quests)
        except QuestError as e:
            print(e)
    elif choice == "5":
        q = input("Enter quest name: ").strip()
        quest_handler.abandon_quest(current_character, q)
    elif choice == "6":
        q = input("Enter quest name: ").strip()
        quest_handler.complete_quest(current_character, q)
    elif choice == "7":
        return

def explore():
    global current_character

    print("\n=== EXPLORING... ===")

    try:
        enemy = combat_system.generate_enemy(current_character.level)
        print(f"Encountered: {enemy['name']}")

        battle = combat_system.SimpleBattle(current_character, enemy)
        result = battle.start()

        if result == "victory":
            print("Victory!")
        elif result == "defeat":
            handle_character_death()

    except CharacterDeadError:
        handle_character_death()

def shop():
    global current_character, all_items

    print("\n=== SHOP ===")
    print("Your Gold:", current_character.gold)

    print("\nItems for sale:")
    for i, item in enumerate(all_items, start=1):
        price = all_items[item].get("price", 10)
        print(f"{i}. {item} - {price} gold")

    print("\nOptions:")
    print("1. Buy Item")
    print("2. Sell Item")
    print("3. Back")

    choice = input("Choose [1-3]: ").strip()

    if choice == "1":
        idx = input("Item number: ").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(all_items):
            item = list(all_items)[int(idx)-1]
            try:
                inventory_system.buy_item(current_character, item, all_items)
                print(f"Bought {item}.")
            except InventoryError as e:
                print(e)

    elif choice == "2":
        inv = current_character.inventory
        if not inv:
            print("No items to sell.")
            return

        idx = input("Item number to sell: ").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(inv):
            item = inv[int(idx)-1]
            inventory_system.sell_item(current_character, item, all_items)
            print(f"Sold {item}.")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    """Save character."""
    try:
        character_manager.save_character(current_character)
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game_data():
    """Load quest & item data."""
    global all_quests, all_items

    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except MissingDataFileError:
        raise
    except InvalidDataFormatError:
        raise

def handle_character_death():
    global current_character, game_running

    print("\n=== YOU DIED ===")
    print("1. Revive (cost 10 gold)")
    print("2. Quit to menu")

    choice = input("Choose: ").strip()

    if choice == "1":
        try:
            character_manager.revive_character(current_character, cost=10)
            print("Revived!")
        except CharacterDeadError:
            print("Not enough gold.")
            game_running = False
    else:
        print("Returning to main menu.")
        game_running = False

def display_welcome():
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    display_welcome()

    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        return

    while True:
        choice = main_menu()

        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break

if __name__ == "__main__":
    main()

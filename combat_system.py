"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

Handles combat mechanics
"""

import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    
    Example enemy types and stats:
    - goblin: health=50, strength=8, magic=2, xp_reward=25, gold_reward=10
    - orc: health=80, strength=12, magic=5, xp_reward=50, gold_reward=25
    - dragon: health=200, strength=25, magic=15, xp_reward=200, gold_reward=100
    
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemy_type = enemy_type.lower()
    enemies = {
        "goblin": {
            "name": "Goblin",
            "health": 50,
            "max_health": 50,
            "strength": 8,
            "magic": 2,
            "xp_reward": 25,
            "gold_reward": 10
        },
        "orc": {
            "name": "Orc",
            "health": 80,
            "max_health": 80,
            "strength": 12,
            "magic": 5,
            "xp_reward": 50,
            "gold_reward": 25
        },
        "dragon": {
            "name": "Dragon",
            "health": 200,
            "max_health": 200,
            "strength": 25,
            "magic": 15,
            "xp_reward": 200,
            "gold_reward": 100
        }
    }
    if enemy_type not in enemies:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")

    return enemies[enemy_type].copy()

    # TODO: Implement enemy creation
    # Return dictionary with: name, health, max_health, strength, magic, xp_reward, gold_reward


def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    
    Returns: Enemy dictionary
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")
    
    # TODO: Implement level-appropriate enemy selection
    # Use if/elif/else to select enemy type
    # Call create_enemy with appropriate type

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    
    Manages combat between character and enemy
    """
    
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_counter = 1
        # TODO: Implement initialization
        # Store character and enemy
        # Set combat_active flag
        # Initialize turn counter
    
    def start_battle(self):
        """
        Start the combat loop
        
        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}
        
        Raises: CharacterDeadError if character is already dead
        """
        if self.character["health"] <= 0:
            raise CharacterDeadError("Character is dead before battle starts.")

        display_battle_log("Battle begins!")

        while self.combat_active:
            display_combat_stats(self.character, self.enemy)

            self.player_turn()
            result = self.check_battle_end()
            if result:
                break

            self.enemy_turn()
            result = self.check_battle_end()
            if result:
                break

            self.turn_counter += 1

        if result == "player":
            rewards = get_victory_rewards(self.enemy)
            display_battle_log("You won the battle!")
            return {
                "winner": "player",
                "xp_gained": rewards["xp"],
                "gold_gained": rewards["gold"]
            }

        display_battle_log("You were defeated...")
        return {
            "winner": "enemy",
            "xp_gained": 0,
            "gold_gained": 0
        }
    
        # TODO: Implement battle loop
        # Check character isn't dead
        # Loop until someone dies
        # Award XP and gold if player wins
    
    def player_turn(self):
        """
        Handle player's turn
        
        Displays options:
        1. Basic Attack
        2. Special Ability (if available)
        3. Try to Run
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Battle is not active.")

        print("\n--- PLAYER TURN ---")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Run")

        choice = input("Choose action: ").strip()

        if choice == "1":
            dmg = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, dmg)
            display_battle_log(f"You deal {dmg} damage!")
        
        elif choice == "2":
            try:
                message = use_special_ability(self.character, self.enemy)
                display_battle_log(message)
            except AbilityOnCooldownError:
                display_battle_log("Ability is on cooldown!")

        elif choice == "3":
            escaped = self.attempt_escape()
            if escaped:
                display_battle_log("You escaped successfully!")
                return
            else:
                display_battle_log("Escape failed!")

        else:
            display_battle_log("Invalid choice. You lose your turn!")

        # TODO: Implement player turn
        # Check combat is active
        # Display options
        # Get player choice
        # Execute chosen action
    
    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        
        Enemy always attacks
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Battle is not active.")

        print("\n--- ENEMY TURN ---")
        dmg = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, dmg)
        display_battle_log(f"{self.enemy['name']} attacks for {dmg} damage!")

        # TODO: Implement enemy turn
        # Check combat is active
        # Calculate damage
        # Apply to character
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        
        Returns: Integer damage amount
        """
        dmg = attacker["strength"] - (defender["strength"] // 4)
        return max(1, dmg)
        # TODO: Implement damage calculation
    
    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        
        Reduces health, prevents negative health
        """
        target["health"] -= damage
        if target["health"] < 0:
            target["health"] = 0
        # TODO: Implement damage application
    
    def check_battle_end(self):
        """
        Check if battle is over
        
        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy["health"] <= 0:
            self.combat_active = False
            return "player"
        if self.character["health"] <= 0:
            self.combat_active = False
            return "enemy"
        return None
        # TODO: Implement battle end check
    
    def attempt_escape(self):
        """
        Try to escape from battle
        
        50% success chance
        
        Returns: True if escaped, False if failed
        """
        success = random.random() < 0.5
        if success:
            self.combat_active = False
        return success
        # TODO: Implement escape attempt
        # Use random number or simple calculation
        # If successful, set combat_active to False

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability
    
    Example abilities by class:
    - Warrior: Power Strike (2x strength damage)
    - Mage: Fireball (2x magic damage)
    - Rogue: Critical Strike (3x strength damage, 50% chance)
    - Cleric: Heal (restore 30 health)
    
    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently
    """
    char_class = character["class"].lower()

    if char_class == "warrior":
        return warrior_power_strike(character, enemy)

    elif char_class == "mage":
        return mage_fireball(character, enemy)

    elif char_class == "rogue":
        return rogue_critical_strike(character, enemy)

    elif char_class == "cleric":
        return cleric_heal(character)

    else:
        return "No special ability available."
    # TODO: Implement special abilities
    # Check character class
    # Execute appropriate ability
    # Track cooldowns (optional advanced feature)

def warrior_power_strike(character, enemy):
    """Warrior special ability"""
    dmg = character["strength"] * 2
    enemy["health"] -= dmg
    return f"Power Strike! You deal {dmg} damage."
    # TODO: Implement power strike
    # Double strength damage

def mage_fireball(character, enemy):
    """Mage special ability"""
    dmg = character["magic"] * 2
    enemy["health"] -= dmg
    return f"Fireball hits for {dmg} damage!"
    # TODO: Implement fireball
    # Double magic damage

def rogue_critical_strike(character, enemy):
    """Rogue special ability"""
    if random.random() < 0.5:
        dmg = character["strength"] * 3
        enemy["health"] -= dmg
        return f"Critical Strike! Massive {dmg} damage!"
    else:
        return "Critical Strike missed!"
    # TODO: Implement critical strike
    # 50% chance for triple damage

def cleric_heal(character):
    """Cleric special ability"""
    character["health"] = min(character["health"] + 30, character["max_health"])
    return "You heal 30 HP."
    # TODO: Implement healing
    # Restore 30 HP (not exceeding max_health)

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    
    Returns: True if health > 0 and not in battle
    """
    return character["health"] > 0
    # TODO: Implement fight check

def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    
    Returns: Dictionary with 'xp' and 'gold'
    """
    return {"xp": enemy["xp_reward"], "gold": enemy["gold_reward"]}

    # TODO: Implement reward calculation

def display_combat_stats(character, enemy):
    """
    Display current combat status
    
    Shows both character and enemy health/stats
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")
    # TODO: Implement status display

def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")
    # TODO: Implement battle log display
# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    # Test enemy creation
    # try:
    #     goblin = create_enemy("goblin")
    #     print(f"Created {goblin['name']}")
    # except InvalidTargetError as e:
    #     print(f"Invalid enemy: {e}")
    
    # Test battle
    # test_char = {
    #     'name': 'Hero',
    #     'class': 'Warrior',
    #     'health': 120,
    #     'max_health': 120,
    #     'strength': 15,
    #     'magic': 5
    # }
    #
    # battle = SimpleBattle(test_char, goblin)
    # try:
    #     result = battle.start_battle()
    #     print(f"Battle result: {result}")
    # except CharacterDeadError:
    #     print("Character is dead!")


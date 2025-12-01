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
    Create and return a dictionary representing an enemy of the given type.

    Args:
        enemy_type (str): Name of the enemy type ("goblin", "orc", "dragon")

    Returns:
        dict: A copy of the enemy template containing stats, rewards, and name.

    Raises:
        InvalidTargetError: If the provided enemy type does not exist.

    Notes:
        - The function lowercases enemy_type for consistency.
        - Returns a COPY so the original template isn't mutated during combat.
    """
    enemy_type = enemy_type.lower()

    # Predefined enemy templates with stats and reward values
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

    # Validate enemy type
    if enemy_type not in enemies:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")

    # Return a fresh copy so changes do not affect the template
    return enemies[enemy_type].copy()


def get_random_enemy_for_level(character_level):
    """
    Select an enemy appropriate for the player's level.

    Args:
        character_level (int): Level of the character.

    Returns:
        dict: Enemy instance appropriate for level range.

    Notes:
        - Levels 1–2 → Goblin
        - Levels 3–5 → Orc
        - Level 6+ → Dragon
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    A simple turn-based combat manager.

    Handles:
    - Player actions
    - Enemy AI actions
    - Combat loop control
    - Victory/defeat detection
    """
    
    def __init__(self, character, enemy):
        """
        Initialize a battle instance.

        Args:
            character (dict): Player stats and info.
            enemy (dict): Enemy stats and info.

        Attributes:
            combat_active (bool): True while battle is ongoing.
            turn_counter (int): Tracks which turn number it is.

        Notes:
            - Character health must be checked later in start_battle().
            - No deep copying is done here; caller should manage character safety.
        """
        self.character = character
        self.enemy = enemy
        self.combat_active = True   # Flag that controls the combat loop
        self.turn_counter = 1       # Useful for cooldowns, logs, etc.
        # TODO: Additional initialization (timers, cooldown tracking, logs if needed)
    
    def start_battle(self):
        """
        Start the full combat loop.

        Returns:
            dict: Battle result summary:
                  {
                      'winner': 'player' or 'enemy',
                      'xp_gained': int,
                      'gold_gained': int
                  }

        Raises:
            CharacterDeadError: If the player starts the fight already dead.
        """
        # Ensure combat is valid
        if self.character["health"] <= 0:
            raise CharacterDeadError("Character is dead before battle starts.")

        display_battle_log("Battle begins!")

        # Main battle loop — ends when combat_active becomes False
        while self.combat_active:

            # Show current HP values before each round
            display_combat_stats(self.character, self.enemy)

            # Player acts first
            self.player_turn()
            result = self.check_battle_end()
            if result:
                break

            # Enemy acts second
            self.enemy_turn()
            result = self.check_battle_end()
            if result:
                break

            # Increase turn count after both take actions
            self.turn_counter += 1

        # Combat resolution — player victory
        if result == "player":
            rewards = get_victory_rewards(self.enemy)
            display_battle_log("You won the battle!")
            return {
                "winner": "player",
                "xp_gained": rewards["xp"],
                "gold_gained": rewards["gold"]
            }

        # Enemy victory
        display_battle_log("You were defeated...")
        return {
            "winner": "enemy",
            "xp_gained": 0,
            "gold_gained": 0
        }
    
    def player_turn(self):
        """
        Handle the player's turn.

        Options:
        1. Basic Attack
        2. Special Ability (may raise AbilityOnCooldownError)
        3. Attempt to run (50% chance)

        Raises:
            CombatNotActiveError: If called after battle has ended.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Battle is not active.")

        print("\n--- PLAYER TURN ---")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Run")

        choice = input("Choose action: ").strip()

        if choice == "1":
            # Standard damage calculation
            dmg = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, dmg)
            display_battle_log(f"You deal {dmg} damage!")
        
        elif choice == "2":
            # Attempt to use special ability
            try:
                message = use_special_ability(self.character, self.enemy)
                display_battle_log(message)
            except AbilityOnCooldownError:
                # If ability is on cooldown, simply warn but do not end combat
                display_battle_log("Ability is on cooldown!")

        elif choice == "3":
            # Attempt escape
            escaped = self.attempt_escape()
            if escaped:
                display_battle_log("You escaped successfully!")
                return
            else:
                display_battle_log("Escape failed!")

        else:
            # Punish invalid input
            display_battle_log("Invalid choice. You lose your turn!")
    
    def enemy_turn(self):
        """
        Handle simple enemy AI turn.

        Notes:
            - Enemy always attacks; no abilities.
            - Damage formula identical to player attack.

        Raises:
            CombatNotActiveError: If battle already ended.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Battle is not active.")

        print("\n--- ENEMY TURN ---")
        dmg = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, dmg)
        display_battle_log(f"{self.enemy['name']} attacks for {dmg} damage!")
    
    def calculate_damage(self, attacker, defender):
        """
        Compute damage for a basic attack.

        Formula:
            damage = attacker.strength - (defender.strength // 4)

        Ensures:
            - Minimum of 1 damage per attack.

        Returns:
            int: Final damage dealt.
        """
        dmg = attacker["strength"] - (defender["strength"] // 4)
        return max(1, dmg)
    
    def apply_damage(self, target, damage):
        """
        Apply damage to the target, guaranteeing HP does not drop below zero.

        Args:
            target (dict): Character or enemy being damaged.
            damage (int): Amount to subtract from target health.
        """
        target["health"] -= damage
        if target["health"] < 0:
            target["health"] = 0  # Prevent negative HP values
    
    def check_battle_end(self):
        """
        Determine whether the battle has ended.

        Returns:
            str:
                "player" → Enemy defeated
                "enemy" → Player defeated
                None → Battle continues

        Notes:
            - This function also sets combat_active = False once battle ends.
        """
        if self.enemy["health"] <= 0:
            self.combat_active = False
            return "player"

        if self.character["health"] <= 0:
            self.combat_active = False
            return "enemy"

        return None
    
    def attempt_escape(self):
        """
        Attempt to flee from battle.

        Returns:
            bool: True if escape successful, False otherwise.

        Notes:
            - 50% chance using random.random() < 0.5
            - Ends combat if successful.
        """
        success = random.random() < 0.5
        if success:
            self.combat_active = False
        return success

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Activate the special ability associated with the character's class.

    Args:
        character (dict): Player stats.
        enemy (dict): Target enemy.

    Returns:
        str: Description of ability result.

    Raises:
        AbilityOnCooldownError: If ability cannot be used yet.

    Notes:
        - Assumes cooldown management handled externally (not shown in code).
        - Supports Warrior, Mage, Rogue, Cleric.
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


def warrior_power_strike(character, enemy):
    """Warrior ability — deals double strength damage."""
    dmg = character["strength"] * 2
    enemy["health"] -= dmg
    return f"Power Strike! You deal {dmg} damage."
    
def mage_fireball(character, enemy):
    """Mage ability — deals double magic damage."""
    dmg = character["magic"] * 2
    enemy["health"] -= dmg
    return f"Fireball hits for {dmg} damage!"

def rogue_critical_strike(character, enemy):
    """
    Rogue ability — 50% chance of landing a triple-damage critical hit.
    
    Returns:
        Success message if hit lands, miss message if it fails.
    """
    if random.random() < 0.5:
        dmg = character["strength"] * 3
        enemy["health"] -= dmg
        return f"Critical Strike! Massive {dmg} damage!"
    else:
        return "Critical Strike missed!"

def cleric_heal(character):
    """
    Cleric ability — heals 30 HP without exceeding max health.
    """
    character["health"] = min(character["health"] + 30, character["max_health"])
    return "You heal 30 HP."

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Determine whether the character is able to enter combat.

    Returns:
        bool: True if character has >0 HP; False otherwise.
    """
    return character["health"] > 0

def get_victory_rewards(enemy):
    """
    Retrieve XP and gold rewards after defeating an enemy.

    Returns:
        dict: {'xp': int, 'gold': int}
    """
    return {"xp": enemy["xp_reward"], "gold": enemy["gold_reward"]}

def display_combat_stats(character, enemy):
    """
    Print the current health/maximum health of both combatants.
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")

def display_battle_log(message):
    """
    Print combat messages with a unified format prefix.
    """
    print(f">>> {message}")
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


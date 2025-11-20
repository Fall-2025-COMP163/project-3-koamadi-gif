"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

Handles combat mechanics
"""

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)
import random

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    Returns enemy dict with keys: name, health, max_health, strength, magic, xp_reward, gold_reward
    """
    et = enemy_type.lower()
    if et == "goblin":
        hp = 50
        return {
            "name": "Goblin",
            "type": "goblin",
            "health": hp,
            "max_health": hp,
            "strength": 8,
            "magic": 2,
            "xp_reward": 25,
            "gold_reward": 10
        }
    elif et == "orc":
        hp = 80
        return {
            "name": "Orc",
            "type": "orc",
            "health": hp,
            "max_health": hp,
            "strength": 12,
            "magic": 5,
            "xp_reward": 50,
            "gold_reward": 25
        }
    elif et == "dragon":
        hp = 200
        return {
            "name": "Dragon",
            "type": "dragon",
            "health": hp,
            "max_health": hp,
            "strength": 25,
            "magic": 15,
            "xp_reward": 200,
            "gold_reward": 100
        }
    else:
        raise InvalidTargetError(f"Unknown enemy type '{enemy_type}'")


def get_random_enemy_for_level(character_level):
    """
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif 3 <= character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    
    Non-interactive: player actions are automatically chosen (basic attack or special when available).
    start_battle returns a summary of the result; it does not mutate XP/gold itself.
    """

    # class-specific cooldown durations (in turns)
    CLASS_COOLDOWNS = {
        "Warrior": 3,
        "Mage": 3,
        "Rogue": 4,
        "Cleric": 3
    }

    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        # shallow copies are fine; we mutate health values
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_counter = 1
        # cooldowns remaining (0 means ability ready)
        self.cooldowns = {"remaining": 0}
        # store per-character cooldown state keyed by class name
        char_class = character.get("class", None)
        self.char_class = char_class
        # initialize remaining cooldowns to 0
        self.cooldown_remaining = 0
        # friendly flag to mark character in battle (optional integration)
        self.character["in_battle"] = True

    def start_battle(self):
        """
        Run the battle loop until someone dies or escape succeeds.
        Returns: {'winner': 'player'|'enemy'|'escaped', 'xp_gained': int, 'gold_gained': int}
        Raises: CharacterDeadError if character already dead
        """
        if self.character.get("health", 0) <= 0:
            raise CharacterDeadError("Character is already dead and cannot fight.")

        # reset any initial cooldown
        self.cooldown_remaining = 0
        # loop until end
        while self.combat_active:
            # Player turn
            self.player_turn()
            result = self.check_battle_end()
            if result:
                winner = result
                break

            # Enemy turn
            self.enemy_turn()
            result = self.check_battle_end()
            if result:
                winner = result
                break

            # decrement cooldown(s) at end of full round (after both turns)
            if self.cooldown_remaining > 0:
                self.cooldown_remaining = max(0, self.cooldown_remaining - 1)

            self.turn_counter += 1

        # leave battle
        self.combat_active = False
        self.character["in_battle"] = False

        if winner == "player":
            rewards = get_victory_rewards(self.enemy)
            display_battle_log(f"{self.character.get('name','Player')} defeated {self.enemy['name']}!")
            return {"winner": "player", "xp_gained": rewards["xp"], "gold_gained": rewards["gold"]}
        elif winner == "enemy":
            display_battle_log(f"{self.character.get('name','Player')} was defeated by {self.enemy['name']}...")
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}
        elif winner == "escaped":
            display_battle_log(f"{self.character.get('name','Player')} escaped from battle.")
            return {"winner": "escaped", "xp_gained": 0, "gold_gained": 0}
        else:
            # defensive fallback
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}

    def player_turn(self):
        """
        Auto-decides and executes player action.
        Options: Basic attack, Use special ability (if ready), Try to run (rarely)
        """
        if not self.combat_active:
            raise CombatNotActiveError("Cannot take player turn when combat is not active.")

        # update display
        display_combat_stats(self.character, self.enemy)

        # If character health is very low, try to escape with some chance
        if self.character.get("health", 0) <= max(1, self.character.get("max_health", 1) * 0.2):
            # small chance to attempt escape
            if random.random() < 0.25:
                escaped = self.attempt_escape()
                if escaped:
                    # set winner to escaped by deactivating combat
                    self.combat_active = False
                    self._battle_end_state = "escaped"
                    return

        # if ability ready, use it; otherwise basic attack
        if self.cooldown_remaining == 0:
            # attempt special ability
            try:
                msg = use_special_ability(self.character, self.enemy)
                # using special ability typically applies damage or heals
                display_battle_log(msg)
                # set cooldown according to class only if ability actually used
                if self.char_class in self.CLASS_COOLDOWNS:
                    self.cooldown_remaining = self.CLASS_COOLDOWNS[self.char_class]
            except AbilityOnCooldownError:
                # fallback to basic attack
                damage = self.calculate_damage(self.character, self.enemy)
                self.apply_damage(self.enemy, damage)
                display_battle_log(f"{self.character.get('name','Player')} attacks for {damage} damage.")
        else:
            # ability on cooldown -> basic attack
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"{self.character.get('name','Player')} attacks for {damage} damage.")

    def enemy_turn(self):
        """
        Enemy attacks the player every enemy turn.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Cannot take enemy turn when combat is not active.")
        # Simple AI: always attack
        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} attacks {self.character.get('name','Player')} for {damage} damage.")

    def calculate_damage(self, attacker, defender):
        """
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        If attacker uses magic (mage Fireball), their ability uses 'magic' stat directly.
        """
        atk = attacker.get("strength", 0)
        # If attacker contains a temporary 'use_magic' flag, use magic stat instead
        if attacker is self.character and attacker.get("_last_ability") == "mage_fireball":
            atk = attacker.get("magic", 0)
            # clear the flag so next attack uses normal strength
            attacker.pop("_last_ability", None)

        mitigation = defender.get("strength", 0) // 4
        dmg = atk - mitigation
        return max(1, int(dmg))

    def apply_damage(self, target, damage):
        """
        Reduce health but do not go below zero. If character dies, mark battle inactive.
        """
        target["health"] = max(0, target.get("health", 0) - int(damage))
        display_battle_log(f"{target.get('name', 'Target')} takes {damage} damage (HP now {target['health']}/{target.get('max_health', '?')}).")

    def check_battle_end(self):
        """
        Returns: 'player' if enemy dead, 'enemy' if character dead, 'escaped' if escaped, None if ongoing
        """
        if self.enemy.get("health", 0) <= 0:
            # enemy dead -> player wins
            self.combat_active = False
            return "player"
        if self.character.get("health", 0) <= 0:
            # player dead -> enemy wins
            self.combat_active = False
            return "enemy"
        # check if escape flag set earlier
        if getattr(self, "_battle_end_state", None) == "escaped":
            return "escaped"
        return None

    def attempt_escape(self):
        """
        50% success chance to escape.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Cannot attempt escape when combat is not active.")

        success = random.random() < 0.5
        if success:
            self.combat_active = False
            self._battle_end_state = "escaped"
            display_battle_log(f"{self.character.get('name','Player')} successfully escaped!")
            return True
        else:
            display_battle_log(f"{self.character.get('name','Player')} failed to escape!")
            return False


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use class-specific special ability. Raises AbilityOnCooldownError if not available.
    Abilities:
      Warrior -> warrior_power_strike
      Mage -> mage_fireball
      Rogue -> rogue_critical_strike
      Cleric -> cleric_heal
    """
    cls = character.get("class", None)
    if cls is None:
        raise AbilityOnCooldownError("Unknown class or no class assigned.")

    cls = cls.title()
    # Note: cooldown enforcement is handled in SimpleBattle.start_battle via cooldown_remaining
    if cls == "Warrior":
        return warrior_power_strike(character, enemy)
    elif cls == "Mage":
        return mage_fireball(character, enemy)
    elif cls == "Rogue":
        return rogue_critical_strike(character, enemy)
    elif cls == "Cleric":
        return cleric_heal(character)
    else:
        raise AbilityOnCooldownError(f"No special ability defined for class '{cls}'.")


def warrior_power_strike(character, enemy):
    """Warrior: 2x strength damage"""
    dmg = max(1, character.get("strength", 0) * 2 - (enemy.get("strength", 0) // 4))
    # apply damage
    enemy["health"] = max(0, enemy.get("health", 0) - int(dmg))
    return f"{character.get('name','Warrior')} uses Power Strike for {dmg} damage!"

def mage_fireball(character, enemy):
    """Mage: 2x magic damage. Use a flag so calculate_damage can use magic if needed."""
    # Use magic stat directly; calculate mitigation from enemy strength // 4
    dmg = max(1, character.get("magic", 0) * 2 - (enemy.get("strength", 0) // 4))
    enemy["health"] = max(0, enemy.get("health", 0) - int(dmg))
    # Mark last ability so any next calculate_damage logic that depends on it can handle (not strictly necessary)
    character["_last_ability"] = "mage_fireball"
    return f"{character.get('name','Mage')} casts Fireball for {dmg} magic damage!"

def rogue_critical_strike(character, enemy):
    """Rogue: 50% chance for 3x damage, else normal attack"""
    if random.random() < 0.5:
        dmg = max(1, character.get("strength", 0) * 3 - (enemy.get("strength", 0) // 4))
        enemy["health"] = max(0, enemy.get("health", 0) - int(dmg))
        return f"{character.get('name','Rogue')} lands a CRITICAL STRIKE for {dmg} damage!"
    else:
        # normal attack
        dmg = max(1, character.get("strength", 0) - (enemy.get("strength", 0) // 4))
        enemy["health"] = max(0, enemy.get("health", 0) - int(dmg))
        return f"{character.get('name','Rogue')} attacks and deals {dmg} damage."

def cleric_heal(character):
    """Cleric: restore 30 HP (cap at max_health)"""
    heal_amt = 30
    old_hp = character.get("health", 0)
    max_hp = character.get("max_health", old_hp)
    new_hp = min(max_hp, old_hp + heal_amt)
    character["health"] = new_hp
    actual_heal = new_hp - old_hp
    return f"{character.get('name','Cleric')} casts Heal and restores {actual_heal} HP."


# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    True if health > 0 and not currently marked as in battle
    """
    return character.get("health", 0) > 0 and not character.get("in_battle", False)

def get_victory_rewards(enemy):
    """
    Returns {'xp': <int>, 'gold': <int>}
    """
    return {"xp": int(enemy.get("xp_reward", 0)), "gold": int(enemy.get("gold_reward", 0))}

def display_combat_stats(character, enemy):
    """
    Print combat health/stats
    """
    print(f"\n-- Combat Status --")
    print(f"{character.get('name','Player')}: HP={character.get('health',0)}/{character.get('max_health','?')}  STR={character.get('strength',0)} MAG={character.get('magic',0)}")
    print(f"{enemy.get('name','Enemy')}: HP={enemy.get('health',0)}/{enemy.get('max_health','?')}  STR={enemy.get('strength',0)} MAG={enemy.get('magic',0)}")

def display_battle_log(message):
    """
    Simple battle logger
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


"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles quest management, dependencies, and completion.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    quest = quest_data_dict[quest_id]

    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed.")

    if quest_id in character["active_quests"]:
        raise QuestRequirementsNotMetError(f"Quest '{quest_id}' already active.")

    if character.get("level", 1) < quest["required_level"]:
        raise InsufficientLevelError(
            f"Level {quest['required_level']} required to accept quest '{quest_id}'."
        )

    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        raise QuestRequirementsNotMetError(
            f"Must complete prerequisite quest '{prereq}' first."
        )

    character["active_quests"].append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Cannot complete '{quest_id}' — not active.")

    quest = quest_data_dict[quest_id]

    character["active_quests"].remove(quest_id)
    character["completed_quests"].append(quest_id)

    xp_reward = quest["reward_xp"]
    gold_reward = quest["reward_gold"]

    character["experience"] += xp_reward
    character["gold"] += gold_reward

    return {"xp": xp_reward, "gold": gold_reward}

def abandon_quest(character, quest_id):
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")

    character["active_quests"].remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    
    Returns: List of quest dictionaries for active quests
    """
    return [quest_data_dict[qid] for qid in character["active_quests"]]

def get_completed_quests(character, quest_data_dict):
    return [quest_data_dict[qid] for qid in character["completed_quests"]]

def get_available_quests(character, quest_data_dict):
    available = []

    for qid, quest in quest_data_dict.items():
        # Skip completed
        if qid in character["completed_quests"]:
            continue

        if qid in character["active_quests"]:
            continue

        if character["level"] < quest["required_level"]:
            continue

        prereq = quest["prerequisite"]
        if prereq != "NONE" and prereq not in character["completed_quests"]:
            continue

        available.append(quest)

    return available

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed
    
    Returns: True if completed, False otherwise
    """
    return quest_id in character["completed_quests"]

    # TODO: Implement completion check

def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    
    Returns: True if active, False otherwise
    """
    return quest_id in character["active_quests"]

    # TODO: Implement active check

def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]

    if quest_id in character["completed_quests"]:
        return False

    if quest_id in character["active_quests"]:
        return False

    if character["level"] < quest["required_level"]:
        return False

    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        return False

    return True

    # TODO: Implement requirement checking
    # Check all requirements without raising exceptions

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    chain = []
    current = quest_id

    while True:
        if current not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{current}' in chain does not exist.")

        chain.append(current)

        prereq = quest_data_dict[current]["prerequisite"]
        if prereq == "NONE":
            break

        current = prereq

    chain.reverse()
    return chain

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    
    Returns: Float between 0 and 100
    """
    total = len(quest_data_dict)
    if total == 0:
        return 0.0

    completed = len(character["completed_quests"])
    return (completed / total) * 100

def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0

    for qid in character["completed_quests"]:
        if qid in quest_data_dict:
            quest = quest_data_dict[qid]
            total_xp += quest["reward_xp"]
            total_gold += quest["reward_gold"]

    return {"total_xp": total_xp, "total_gold": total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    
    Returns: List of quest dictionaries
    """
    return [
        quest
        for quest in quest_data_dict.values()
        if min_level <= quest["required_level"] <= max_level
    ]

    # TODO: Implement level filtering

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    
    Shows: Title, Description, Rewards, Requirements
    """
    # TODO: Implement quest display
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    # ... etc
    print(f"Required Level: {quest_data['required_level']}")
    print(f"Prerequisite: {quest_data['prerequisite']}")
    print(f"Rewards: {quest_data['reward_xp']} XP, {quest_data['reward_gold']} Gold")

def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    
    Shows: Title, Required Level, Rewards
    """
    print("\n=== Quest List ===")
    for quest in quest_list:
        print(f"- {quest['title']} (Lvl {quest['required_level']})  "
              f"[Rewards: {quest['reward_xp']} XP, {quest['reward_gold']} Gold]")

    # TODO: Implement quest list display

def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    
    Shows:
    - Active quests count
    - Completed quests count
    - Completion percentage
    - Total rewards earned
    """
    total = len(quest_data_dict)
    completed = len(character["completed_quests"])
    active = len(character["active_quests"])
    percent = get_quest_completion_percentage(character, quest_data_dict)
    rewards = get_total_quest_rewards_earned(character, quest_data_dict)

    print("\n=== Quest Progress ===")
    print(f"Active Quests: {active}")
    print(f"Completed Quests: {completed}/{total}")
    print(f"Completion: {percent:.2f}%")
    print(f"Total Rewards Earned: {rewards['total_xp']} XP, {rewards['total_gold']} Gold")
    # TODO: Implement progress display

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    
    Checks that every prerequisite (that's not "NONE") refers to a real quest
    
    Returns: True if all valid
    Raises: QuestNotFoundError if invalid prerequisite found
    """
    for qid, quest in quest_data_dict.items():
        prereq = quest["prerequisite"]
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(
                f"Quest '{qid}' has invalid prerequisite '{prereq}'."
            )

    return True
    # TODO: Implement prerequisite validation
    # Check each quest's prerequisite
    # Ensure prerequisite exists in quest_data_dict

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    # Test data
    # test_char = {
    #     'level': 1,
    #     'active_quests': [],
    #     'completed_quests': [],
    #     'experience': 0,
    #     'gold': 100
    # }
    #
    # test_quests = {
    #     'first_quest': {
    #         'quest_id': 'first_quest',
    #         'title': 'First Steps',
    #         'description': 'Complete your first quest',
    #         'reward_xp': 50,
    #         'reward_gold': 25,
    #         'required_level': 1,
    #         'prerequisite': 'NONE'
    #     }
    # }
    #
    # try:
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")


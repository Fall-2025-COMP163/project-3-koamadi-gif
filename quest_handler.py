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

import character_manager  # Needed for gain_experience and add_gold

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")

    quest = quest_data_dict[quest_id]

    # Level requirement
    if character["level"] < quest["required_level"]:
        raise InsufficientLevelError("Level too low to accept quest")

    # Prerequisite
    prereq = quest.get("prerequisite", "NONE")
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        raise QuestRequirementsNotMetError(f"Prerequisite '{prereq}' not completed")

    # Already completed / already active
    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError("Quest already completed")
    if quest_id in character["active_quests"]:
        raise QuestAlreadyCompletedError("Quest already active")

    character["active_quests"].append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")

    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError("Quest is not active")

    quest = quest_data_dict[quest_id]

    character["active_quests"].remove(quest_id)
    character["completed_quests"].append(quest_id)

    # Grant rewards
    xp = quest.get("reward_xp", 0)
    gold = quest.get("reward_gold", 0)

    character_manager.gain_experience(character, xp)
    character_manager.add_gold(character, gold)

    return {"xp": xp, "gold": gold}


def abandon_quest(character, quest_id):
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError("Quest is not active")
    
    character["active_quests"].remove(quest_id)
    return True


# ============================================================================
# QUEST RETRIEVAL
# ============================================================================

def get_active_quests(character, quest_data_dict):
    return [quest_data_dict[qid] for qid in character["active_quests"]]


def get_completed_quests(character, quest_data_dict):
    return [quest_data_dict[qid] for qid in character["completed_quests"]]


def get_available_quests(character, quest_data_dict):
    available = []
    for qid, quest in quest_data_dict.items():
        if can_accept_quest(character, qid, quest_data_dict):
            available.append(quest)
    return available


# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    return quest_id in character["completed_quests"]


def is_quest_active(character, quest_id):
    return quest_id in character["active_quests"]


def can_accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]
    prereq = quest.get("prerequisite", "NONE")

    return (
        character["level"] >= quest["required_level"] and
        quest_id not in character["active_quests"] and
        quest_id not in character["completed_quests"] and
        (prereq == "NONE" or prereq in character["completed_quests"])
    )


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")

    chain = []
    current = quest_id

    while current != "NONE":
        if current not in quest_data_dict:
            raise QuestNotFoundError(f"Missing required quest '{current}'")
        chain.append(current)
        current = quest_data_dict[current].get("prerequisite", "NONE")

    return list(reversed(chain))


# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    done = len(character["completed_quests"])
    return (done / total * 100) if total > 0 else 0.0


def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0

    for qid in character["completed_quests"]:
        quest = quest_data_dict.get(qid, {})
        total_xp += quest.get("reward_xp", 0)
        total_gold += quest.get("reward_gold", 0)

    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    return [
        q for q in quest_data_dict.values()
        if min_level <= q.get("required_level", 0) <= max_level
    ]


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    print(f"Required Level: {quest_data['required_level']}")
    print(f"Rewards: {quest_data['reward_xp']} XP, {quest_data['reward_gold']} Gold")
    print(f"Prerequisite: {quest_data.get('prerequisite', 'NONE')}")


def display_quest_list(quest_list):
    for q in quest_list:
        print(f"- {q['title']} (Lvl {q['required_level']}): {q['reward_xp']} XP, {q['reward_gold']} Gold")


def display_character_quest_progress(character, quest_data_dict):
    percent = get_quest_completion_percentage(character, quest_data_dict)
    rewards = get_total_quest_rewards_earned(character, quest_data_dict)

    print("\n=== Quest Progress ===")
    print(f"Active: {len(character['active_quests'])}")
    print(f"Completed: {len(character['completed_quests'])}")
    print(f"Completion: {percent:.1f}%")
    print(f"Total XP Earned: {rewards['total_xp']}")
    print(f"Total Gold Earned: {rewards['total_gold']}")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    for qid, quest in quest_data_dict.items():
        prereq = quest.get("prerequisite", "NONE")
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{qid}' has invalid prerequisite '{prereq}'")
    return True


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


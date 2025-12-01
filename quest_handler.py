"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: Kobby Amadi

AI Usage: Google Gemini

This module handles quest management, dependencies, and completion.
"""

# Import specific custom exception classes from the custom_exceptions module.
# These exceptions are raised when quest-related operations fail.
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
    # Ensure the quest ID actually exists in the master quest dictionary.
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    # Retrieve the full quest data for convenience.
    quest = quest_data_dict[quest_id]

    # Prevent accepting quests the character has already finished.
    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed.")

    # Prevent accepting a quest that is currently active.
    if quest_id in character["active_quests"]:
        raise QuestRequirementsNotMetError(f"Quest '{quest_id}' already active.")

    # Check if the character's level meets the quest's required minimum.
    if character.get("level", 1) < quest["required_level"]:
        raise InsufficientLevelError(
            f"Level {quest['required_level']} required to accept quest '{quest_id}'."
        )

    # Validate prerequisite quest (if not "NONE").
    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        raise QuestRequirementsNotMetError(
            f"Must complete prerequisite quest '{prereq}' first."
        )

    # Add quest to the character's list of active quests.
    character["active_quests"].append(quest_id)

    # Return True to indicate success.
    return True


def complete_quest(character, quest_id, quest_data_dict):
    # Ensure the quest ID exists before completing it.
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    # A quest can only be completed if it's currently active.
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Cannot complete '{quest_id}' — not active.")

    # Retrieve quest details.
    quest = quest_data_dict[quest_id]

    # Remove quest from active list and mark as completed.
    character["active_quests"].remove(quest_id)
    character["completed_quests"].append(quest_id)

    # Retrieve rewards from quest data.
    xp_reward = quest["reward_xp"]
    gold_reward = quest["reward_gold"]

    # Add rewards to character stats.
    character["experience"] += xp_reward
    character["gold"] += gold_reward

    # Return rewards so the caller can display or process them.
    return {"xp": xp_reward, "gold": gold_reward}


def abandon_quest(character, quest_id):
    # Validate that the quest is currently active.
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")

    # Remove quest without marking it complete.
    character["active_quests"].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    
    Returns: List of quest dictionaries for active quests
    """
    # Return detailed data (not just quest IDs) for each active quest.
    return [quest_data_dict[qid] for qid in character["active_quests"]]


def get_completed_quests(character, quest_data_dict):
    # Return detailed quest data for each completed quest.
    return [quest_data_dict[qid] for qid in character["completed_quests"]]


def get_available_quests(character, quest_data_dict):
    # Will store quests the character can accept.
    available = []

    # Iterate over every quest in the quest database.
    for qid, quest in quest_data_dict.items():

        # Ignore quests that the character has already finished.
        if qid in character["completed_quests"]:
            continue

        # Ignore quests already active.
        if qid in character["active_quests"]:
            continue

        # Ignore quests above the character's current level.
        if character["level"] < quest["required_level"]:
            continue

        # Ignore quests whose prerequisites are incomplete.
        prereq = quest["prerequisite"]
        if prereq != "NONE" and prereq not in character["completed_quests"]:
            continue

        # If all conditions pass, add quest to available list.
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
    # Simply check membership in completed_quests list.
    return quest_id in character["completed_quests"]


def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    
    Returns: True if active, False otherwise
    """
    # Check if quest ID is in active_quests.
    return quest_id in character["active_quests"]


def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    # Quest must exist.
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]

    # Cannot accept completed quest.
    if quest_id in character["completed_quests"]:
        return False

    # Cannot accept active quest.
    if quest_id in character["active_quests"]:
        return False

    # Must meet level requirement.
    if character["level"] < quest["required_level"]:
        return False

    # Must meet prerequisite requirement.
    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        return False

    # If every check passed, it's acceptable.
    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    # Ensure the root quest ID exists.
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    # Will store chain in reverse order first.
    chain = []
    current = quest_id

    # Walk backwards through prerequisites until reaching the root.
    while True:
        # Safety check against invalid prerequisite chains.
        if current not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{current}' in chain does not exist.")

        # Add current quest to chain.
        chain.append(current)

        # Move to next prerequisite.
        prereq = quest_data_dict[current]["prerequisite"]

        # "NONE" indicates we're at the start of the chain.
        if prereq == "NONE":
            break

        # Continue walking backwards.
        current = prereq

    # Reverse so earliest quest appears first.
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
    # Handle case where no quests exist.
    total = len(quest_data_dict)
    if total == 0:
        return 0.0

    # Number of completed quests.
    completed = len(character["completed_quests"])

    # Convert to percent.
    return (completed / total) * 100


def get_total_quest_rewards_earned(character, quest_data_dict):
    # Initialize counters for xp and gold.
    total_xp = 0
    total_gold = 0

    # Loop through completed quest IDs.
    for qid in character["completed_quests"]:

        # Only count quest if it exists in the database.
        if qid in quest_data_dict:
            quest = quest_data_dict[qid]
            total_xp += quest["reward_xp"]
            total_gold += quest["reward_gold"]

    # Return cumulative totals.
    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    
    Returns: List of quest dictionaries
    """
    # Filter quests whose required_level is between the given bounds.
    return [
        quest
        for quest in quest_data_dict.values()
        if min_level <= quest["required_level"] <= max_level
    ]

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    
    Shows: Title, Description, Rewards, Requirements
    """
    # Print formatted quest details.
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    print(f"Required Level: {quest_data['required_level']}")
    print(f"Prerequisite: {quest_data['prerequisite']}")
    print(f"Rewards: {quest_data['reward_xp']} XP, {quest_data['reward_gold']} Gold")


def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    
    Shows: Title, Required Level, Rewards
    """
    print("\n=== Quest List ===")

    # Loop through each quest and show summary info.
    for quest in quest_list:
        print(f"- {quest['title']} (Lvl {quest['required_level']})  "
              f"[Rewards: {quest['reward_xp']} XP, {quest['reward_gold']} Gold]")


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

    # Print all progress stats.
    print("\n=== Quest Progress ===")
    print(f"Active Quests: {active}")
    print(f"Completed Quests: {completed}/{total}")
    print(f"Completion: {percent:.2f}%")
    print(f"Total Rewards Earned: {rewards['total_xp']} XP, {rewards['total_gold']} Gold")

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
    # Loop through all quests.
    for qid, quest in quest_data_dict.items():
        prereq = quest["prerequisite"]

        # If prerequisite isn't NONE and doesn't exist, raise an exception.
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(
                f"Quest '{qid}' has invalid prerequisite '{prereq}'."
            )

    # If no issues were found, validation succeeds.
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


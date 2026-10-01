from skills.alarm import SetAlarmSkill

SKILLS = {
    "set_alarm": SetAlarmSkill(),
    # "open_app":       OpenAppSkill(),
    # "send_email":     SendEmailSkill(),
    # "get_directions": GetDirectionsSkill(),
}


def dispatch(intent: str, parameters: dict, memory: dict = None) -> str:
    if intent == "remember_preference":
        if memory is None:
            return "I can't save that right now."
        key = parameters.get("key", "").strip()
        value = parameters.get("value", "").strip()
        if not key or not value:
            return "What would you like me to remember?"
        from memory import set_preference
        set_preference(memory, key, value)
        return f"Got it, I'll remember that {key.replace('_', ' ')} is {value}."

    skill = SKILLS.get(intent)
    if skill is None:
        return (
            f"I understood you want to {intent.replace('_', ' ')}, "
            "but I don't have that skill built yet."
        )
    return skill.execute(parameters)
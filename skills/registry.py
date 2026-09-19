from skills.alarm import SetAlarmSkill

SKILLS = {
    "set_alarm": SetAlarmSkill(),
    # "open_app":        OpenAppSkill(),
    # "send_email":      SendEmailSkill(),
    # "get_directions":  GetDirectionsSkill(),
}


def dispatch(intent: str, parameters: dict) -> str:

    skill = SKILLS.get(intent)
    if skill is None:
        return (
            f"I understood you want to {intent.replace('_', ' ')}, "
            "but I don't have that skill built yet."
        )
    return skill.execute(parameters)
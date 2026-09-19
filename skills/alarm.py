import subprocess
from datetime import datetime

from skills.base import Skill

_ALARM_SCRIPT = (
    "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
    "ContentType = WindowsRuntime] | Out-Null; "
    "$template = [Windows.UI.Notifications.ToastNotificationManager]"
    "::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
    "$template.SelectSingleNode('//text[@id=1]').InnerText = 'Voice Assistant'; "
    "$template.SelectSingleNode('//text[@id=2]').InnerText = 'Your alarm is going off!'; "
    "$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
    "[Windows.UI.Notifications.ToastNotificationManager]"
    "::CreateToastNotifier('Voice Assistant').Show($toast)"
)


class SetAlarmSkill(Skill):
    intent_name = "set_alarm"

    def execute(self, parameters: dict) -> str:
        time_str = parameters.get("time")
        if not time_str:
            return "What time should I set the alarm for?"

        alarm_time = self._parse_time(time_str)
        if alarm_time is None:
            return (
                f"I couldn't understand the time '{time_str}'. "
                "Please say something like 'set an alarm for 7 AM'."
            )

        task_name = f"VoiceAssistantAlarm_{alarm_time.strftime('%H%M%S')}"
        time_arg = alarm_time.strftime("%H:%M")

        result = subprocess.run(
            [
                "schtasks", "/create",
                "/tn", task_name,
                "/tr", f"powershell -WindowStyle Hidden -Command \"{_ALARM_SCRIPT}\"",
                "/sc", "once",
                "/st", time_arg,
                "/f",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return (
                "I had trouble setting the alarm. "
                "Make sure you're running as a normal Windows user "
                f"(error: {result.stderr.strip()})."
            )

        subprocess.run(
            [
                "schtasks", "/create",
                "/tn", f"{task_name}_cleanup",
                "/tr", f"schtasks /delete /tn \"{task_name}\" /f",
                "/sc", "once",
                "/st", time_arg,
                "/f",
            ],
            capture_output=True,
        )

        spoken_time = alarm_time.strftime("%I:%M %p").lstrip("0")
        return f"Done! Alarm set for {spoken_time}."

    @staticmethod
    def _parse_time(time_str: str) -> datetime | None:
        """Try several common time formats the AI might return."""
        formats = [
            "%H:%M",       
            "%I:%M %p",    
            "%I:%M%p",     
            "%I %p",       
            "%H",         
        ]
        for fmt in formats:
            try:
                return datetime.strptime(time_str.strip(), fmt)
            except ValueError:
                continue
        return None
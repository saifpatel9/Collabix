from django import forms

from apps.employees.forms import TailwindFormMixin

from .models import NotificationPreference


class NotificationPreferenceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = (
            "task_notifications",
            "project_notifications",
            "mention_notifications",
            "approval_notifications",
            "system_notifications",
            "realtime_enabled",
        )
        widgets = {
            name: forms.CheckboxInput(
                attrs={"class": "h-4 w-4 rounded border-slate-300 text-cyan-600"}
            )
            for name in (
                "task_notifications",
                "project_notifications",
                "mention_notifications",
                "approval_notifications",
                "system_notifications",
                "realtime_enabled",
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

from django import forms

from apps.employees.models import Department, EmployeeProfile
from apps.employees.forms import INPUT_CLASS, TailwindFormMixin

from .models import Milestone, Project, ProjectMember, Team, TeamMembership


class TeamForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Team
        fields = ("name", "description", "team_lead", "department", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 rounded border-slate-300 text-cyan-600"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team_lead"].queryset = EmployeeProfile.objects.select_related(
            "user"
        ).order_by("user__full_name")
        self.fields["department"].queryset = Department.objects.filter(
            is_active=True
        ).order_by("name")
        self._apply_base_classes()


class TeamMembershipForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TeamMembership
        fields = ("employee", "role")

    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = EmployeeProfile.objects.select_related("user").order_by(
            "user__full_name"
        )
        if team:
            queryset = queryset.exclude(team_memberships__team=team)
        self.fields["employee"].queryset = queryset
        self._apply_base_classes()


class ProjectForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "name",
            "code",
            "description",
            "owner",
            "department",
            "team",
            "start_date",
            "target_end_date",
            "actual_end_date",
            "priority",
            "status",
            "budget",
            "is_archived",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "target_end_date": forms.DateInput(attrs={"type": "date"}),
            "actual_end_date": forms.DateInput(attrs={"type": "date"}),
            "is_archived": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 rounded border-slate-300 text-cyan-600"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].queryset = EmployeeProfile.objects.select_related(
            "user"
        ).order_by("user__full_name")
        self.fields["department"].queryset = Department.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["team"].queryset = Team.objects.filter(is_active=True).order_by(
            "name"
        )
        self._apply_base_classes()


class ProjectMemberForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ("employee", "role")

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = EmployeeProfile.objects.select_related("user").order_by(
            "user__full_name"
        )
        if project:
            queryset = queryset.exclude(project_memberships__project=project)
        self.fields["employee"].queryset = queryset
        self._apply_base_classes()


class ProjectMemberRoleForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ("role",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].widget.attrs["class"] = INPUT_CLASS


class MilestoneForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ("name", "description", "due_date", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()

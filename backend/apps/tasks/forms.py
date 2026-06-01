from django import forms
from django.core.exceptions import ValidationError

from apps.employees.forms import TailwindFormMixin
from apps.employees.models import EmployeeProfile
from apps.projects.models import Milestone, Project
from apps.projects.selectors.project_selectors import ProjectSelector

from .models import (
    Task,
    TaskAssignment,
    TaskAttachment,
    TaskChecklist,
    TaskChecklistItem,
    TaskComment,
    TaskDependency,
)


class TaskForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "project",
            "milestone",
            "title",
            "description",
            "task_code",
            "status",
            "priority",
            "estimated_hours",
            "actual_hours",
            "start_date",
            "due_date",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, project=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        project_queryset = Project.objects.filter(is_archived=False).order_by("name")
        if user:
            project_queryset = ProjectSelector.visible_to(user).filter(
                is_archived=False
            )
        self.fields["project"].queryset = project_queryset
        self.fields["milestone"].queryset = (
            Milestone.objects.select_related("project")
            .filter(project__in=project_queryset)
            .order_by("project__name", "due_date")
        )
        if project:
            self.fields["project"].initial = project
            self.fields["project"].queryset = Project.objects.filter(pk=project.pk)
            self.fields["milestone"].queryset = project.milestones.order_by(
                "due_date", "name"
            )
        self._apply_base_classes()


class TaskAssignmentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = ("employee",)

    def __init__(self, *args, task=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = EmployeeProfile.objects.select_related("user").order_by(
            "user__full_name"
        )
        if task:
            queryset = queryset.filter(project_memberships__project=task.project)
        self.fields["employee"].queryset = queryset.distinct()
        self._apply_base_classes()


class TaskCommentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ("comment", "parent")
        widgets = {"comment": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, task=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].required = False
        self.fields["parent"].widget = forms.HiddenInput()
        if task:
            self.fields["parent"].queryset = task.comments.all()
        self._apply_base_classes()


class TaskAttachmentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TaskAttachment
        fields = ("file",)

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        if uploaded.size > 25 * 1024 * 1024:
            raise ValidationError("Attachments cannot exceed 25 MB.")
        return uploaded


class TaskChecklistForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TaskChecklist
        fields = ("title", "position")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()


class TaskChecklistItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TaskChecklistItem
        fields = ("title", "position")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()


class TaskDependencyForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TaskDependency
        fields = ("predecessor_task", "dependency_type")

    def __init__(self, *args, task=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Task.objects.select_related("project").filter(is_archived=False)
        if task:
            queryset = queryset.filter(project=task.project).exclude(pk=task.pk)
        self.fields["predecessor_task"].queryset = queryset.order_by("task_code")
        self._apply_base_classes()

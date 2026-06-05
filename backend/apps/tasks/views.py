from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.employees.models import EmployeeProfile
from apps.projects.models import Milestone, Project

from .forms import (
    TaskAssignmentForm,
    TaskAttachmentForm,
    TaskChecklistForm,
    TaskChecklistItemForm,
    TaskCommentForm,
    TaskDependencyForm,
    TaskForm,
)
from .models import Task, TaskChecklist, TaskChecklistItem, TaskDependency
from .permissions import TaskAccessMixin, TaskExecuteMixin, TaskManageMixin
from .selectors.task_selectors import TaskSelector
from .services.assignment_service import TaskAssignmentService
from .services.attachment_service import TaskAttachmentService
from .services.checklist_service import TaskChecklistService
from .services.comment_service import TaskCommentService
from .services.dependency_service import TaskDependencyService
from .services.task_service import TaskService


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 25

    def get_queryset(self):
        queryset = TaskSelector.active_for(self.request.user)
        return TaskSelector.filtered(
            queryset,
            search=self.request.GET.get("q"),
            status=self.request.GET.get("status"),
            priority=self.request.GET.get("priority"),
            assignee=self.request.GET.get("assignee"),
            project=self.request.GET.get("project"),
            milestone=self.request.GET.get("milestone"),
            created_by=self.request.GET.get("created_by"),
            start_date=self.request.GET.get("start_date"),
            due_date=self.request.GET.get("due_date"),
        )

    def get_template_names(self):
        if is_htmx(self.request):
            return ["tasks/partials/task_table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(task_filter_context(self.request))
        return context


class TaskDetailView(TaskAccessMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_object(self, queryset=None):
        return self.task_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "assignments": TaskSelector.assignments_for(self.object),
                "comments": TaskSelector.comments_for(self.object),
                "attachments": self.object.attachments.select_related(
                    "uploaded_by__user"
                ),
                "activities": TaskSelector.activities_for(self.object),
                "checklists": TaskSelector.checklists_for(self.object),
                "dependencies": TaskSelector.dependencies_for(self.object),
                "assignment_form": TaskAssignmentForm(task=self.object),
                "comment_form": TaskCommentForm(task=self.object),
                "attachment_form": TaskAttachmentForm(),
                "checklist_form": TaskChecklistForm(),
                "checklist_item_form": TaskChecklistItemForm(),
                "dependency_form": TaskDependencyForm(task=self.object),
            }
        )
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        project_pk = self.request.GET.get("project")
        if project_pk:
            kwargs["project"] = get_object_or_404(Project, pk=project_pk)
        return kwargs

    def form_valid(self, form):
        task = TaskService.create(
            cleaned_data=form.cleaned_data, user=self.request.user, request=self.request
        )
        messages.success(self.request, "Task created successfully.")
        return redirect("tasks:task_detail", pk=task.pk)


class TaskUpdateView(TaskManageMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_object(self, queryset=None):
        return self.task_object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("tasks:task_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            TaskService.update(
                task=self.object,
                cleaned_data=form.cleaned_data,
                user=self.request.user,
                request=self.request,
            )
            messages.success(self.request, "Task updated successfully.")
            return redirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)


class TaskDeleteView(TaskManageMixin, View):
    def post(self, request, *args, **kwargs):
        TaskService.delete(task=self.task_object, user=request.user, request=request)
        messages.success(request, "Task deleted successfully.")
        return redirect("tasks:task_list")


class TaskArchiveView(TaskManageMixin, View):
    def post(self, request, *args, **kwargs):
        TaskService.archive(task=self.task_object, user=request.user, request=request)
        messages.success(request, "Task archived successfully.")
        return redirect("tasks:task_archive")


class TaskArchiveListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_archive.html"
    context_object_name = "tasks"
    paginate_by = 25

    def get_queryset(self):
        return TaskSelector.visible_to(self.request.user).filter(is_archived=True)


class TaskStatusUpdateView(TaskExecuteMixin, View):
    def post(self, request, *args, **kwargs):
        status = request.POST.get("status")
        if status not in Task.Status.values:
            return HttpResponseBadRequest("Invalid status")
        try:
            task = TaskService.change_status(
                task=self.task_object, status=status, user=request.user, request=request
            )
            if is_htmx(request):
                return render(request, "tasks/partials/task_card.html", {"task": task})
            return redirect("tasks:task_detail", pk=task.pk)
        except ValidationError as e:
            if is_htmx(request):
                response = HttpResponseBadRequest(str(e))
                response["HX-Retarget"] = "body"
                response["HX-Reswap"] = "none"
                messages.error(request, str(e))
                return response
            else:
                messages.error(request, str(e))
                return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskPriorityUpdateView(TaskManageMixin, View):
    def post(self, request, *args, **kwargs):
        priority = request.POST.get("priority")
        if priority not in Task.Priority.values:
            return HttpResponseBadRequest("Invalid priority")
        task = TaskService.change_priority(
            task=self.task_object, priority=priority, user=request.user, request=request
        )
        if is_htmx(request):
            return render(request, "tasks/partials/priority_badge.html", {"task": task})
        return redirect("tasks:task_detail", pk=task.pk)


class TaskAssignmentView(TaskManageMixin, View):
    def post(self, request, *args, **kwargs):
        form = TaskAssignmentForm(request.POST, task=self.task_object)
        if form.is_valid():
            TaskAssignmentService.assign(
                task=self.task_object,
                employee=form.cleaned_data["employee"],
                user=request.user,
                request=request,
            )
            messages.success(request, "Task assigned.")
        else:
            messages.error(request, "Unable to assign task.")
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskCommentView(TaskAccessMixin, View):
    def post(self, request, *args, **kwargs):
        form = TaskCommentForm(request.POST, task=self.task_object)
        if form.is_valid():
            TaskCommentService.create(
                task=self.task_object,
                cleaned_data=form.cleaned_data,
                user=request.user,
                request=request,
            )
        if is_htmx(request):
            return render(
                request,
                "tasks/partials/task_comments.html",
                {
                    "comments": TaskSelector.comments_for(self.task_object),
                    "task": self.task_object,
                },
            )
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskAttachmentView(TaskAccessMixin, View):
    def post(self, request, *args, **kwargs):
        form = TaskAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            TaskAttachmentService.create(
                task=self.task_object,
                uploaded_file=form.cleaned_data["file"],
                user=request.user,
                request=request,
            )
            messages.success(request, "Attachment uploaded.")
        else:
            messages.error(request, "Unable to upload attachment.")
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskChecklistView(TaskAccessMixin, View):
    def post(self, request, *args, **kwargs):
        form = TaskChecklistForm(request.POST)
        if form.is_valid():
            TaskChecklistService.create_checklist(
                task=self.task_object,
                cleaned_data=form.cleaned_data,
                user=request.user,
                request=request,
            )
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskChecklistItemView(TaskAccessMixin, View):
    def post(self, request, *args, **kwargs):
        checklist = get_object_or_404(
            TaskChecklist, pk=kwargs["checklist_pk"], task=self.task_object
        )
        form = TaskChecklistItemForm(request.POST)
        if form.is_valid():
            TaskChecklistService.create_item(
                checklist=checklist,
                cleaned_data=form.cleaned_data,
                user=request.user,
                request=request,
            )
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskChecklistToggleView(TaskAccessMixin, View):
    def post(self, request, *args, **kwargs):
        item = get_object_or_404(
            TaskChecklistItem.objects.select_related("checklist__task"),
            pk=kwargs["item_pk"],
            checklist__task=self.task_object,
        )
        is_completed = request.POST.get("is_completed") == "on"
        TaskChecklistService.toggle_item(
            item=item, is_completed=is_completed, user=request.user, request=request
        )
        if is_htmx(request):
            checklists = TaskSelector.checklists_for(self.task_object)
            return render(
                request,
                "tasks/partials/task_checklist.html",
                {"task": self.task_object, "checklists": checklists},
            )
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskDependencyView(TaskManageMixin, View):
    def post(self, request, *args, **kwargs):
        form = TaskDependencyForm(request.POST, task=self.task_object)
        if form.is_valid():
            TaskDependencyService.create(
                successor_task=self.task_object,
                predecessor_task=form.cleaned_data["predecessor_task"],
                dependency_type=form.cleaned_data["dependency_type"],
                user=request.user,
                request=request,
            )
            messages.success(request, "Dependency added.")
        else:
            messages.error(request, "Unable to add dependency.")
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskDependencyDeleteView(TaskManageMixin, View):
    def post(self, request, *args, **kwargs):
        dependency = get_object_or_404(
            TaskDependency, pk=kwargs["dependency_pk"], successor_task=self.task_object
        )
        TaskDependencyService.delete(
            dependency=dependency, user=request.user, request=request
        )
        return redirect("tasks:task_detail", pk=self.task_object.pk)


class TaskBoardView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_board.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return TaskSelector.board_for(
            self.request.user,
            project=self.request.GET.get("project"),
            milestone=self.request.GET.get("milestone"),
        )

    def get_template_names(self):
        if is_htmx(self.request):
            return ["tasks/partials/kanban_columns.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = list(context["tasks"])
        context["columns"] = [
            (status, label, [task for task in tasks if task.status == status])
            for status, label in Task.Status.choices
            if status != Task.Status.CANCELLED
        ]
        context["projects"] = Project.objects.filter(is_archived=False).order_by("name")
        context["milestones"] = Milestone.objects.select_related("project").order_by(
            "project__name", "due_date"
        )
        context["filters"] = {
            "project": self.request.GET.get("project", ""),
            "milestone": self.request.GET.get("milestone", ""),
        }
        return context


def task_filter_context(request):
    return {
        "statuses": Task.Status.choices,
        "priorities": Task.Priority.choices,
        "projects": Project.objects.filter(is_archived=False).order_by("name"),
        "milestones": Milestone.objects.select_related("project").order_by(
            "project__name", "due_date"
        ),
        "employees": EmployeeProfile.objects.select_related("user").order_by(
            "user__full_name"
        ),
        "filters": {
            "q": request.GET.get("q", ""),
            "status": request.GET.get("status", ""),
            "priority": request.GET.get("priority", ""),
            "assignee": request.GET.get("assignee", ""),
            "project": request.GET.get("project", ""),
            "milestone": request.GET.get("milestone", ""),
            "created_by": request.GET.get("created_by", ""),
            "start_date": request.GET.get("start_date", ""),
            "due_date": request.GET.get("due_date", ""),
        },
    }

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.core.permissions import ManagerRequiredMixin, ProjectManagerRequiredMixin

from .forms import (
    MilestoneForm,
    ProjectForm,
    ProjectMemberForm,
    ProjectMemberRoleForm,
    TeamForm,
    TeamMembershipForm,
)
from .models import Milestone, Project, ProjectMember, Team, TeamMembership
from .permissions import ProjectAccessMixin, ProjectManageMixin
from .selectors.project_selectors import MilestoneSelector, ProjectSelector
from .selectors.team_selectors import TeamSelector
from .services.milestone_service import MilestoneService
from .services.project_member_service import ProjectMemberService
from .services.project_service import ProjectService
from .services.team_service import TeamMembershipService, TeamService


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


class TeamDirectoryView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "teams/directory.html"
    context_object_name = "teams"
    paginate_by = 12

    def get_queryset(self):
        queryset = TeamSelector.visible_to(self.request.user)
        return TeamSelector.search(queryset, self.request.GET.get("q"))

    def get_template_names(self):
        if is_htmx(self.request):
            return ["teams/partials/directory_grid.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "teams/detail.html"
    context_object_name = "team"

    def get_queryset(self):
        return TeamSelector.visible_to(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["memberships"] = TeamSelector.memberships_for(self.object)
        context["membership_form"] = TeamMembershipForm(team=self.object)
        return context


class TeamCreateView(ManagerRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "teams/form.html"
    success_url = reverse_lazy("projects:team_directory")

    def form_valid(self, form):
        TeamService.create(
            cleaned_data=form.cleaned_data, user=self.request.user, request=self.request
        )
        messages.success(self.request, "Team created successfully.")
        return redirect(self.success_url)


class TeamUpdateView(ManagerRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "teams/form.html"

    def get_success_url(self):
        return reverse("projects:team_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        TeamService.update(
            team=self.object,
            cleaned_data=form.cleaned_data,
            user=self.request.user,
            request=self.request,
        )
        messages.success(self.request, "Team updated successfully.")
        return redirect(self.get_success_url())


class TeamArchiveView(ManagerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, pk=kwargs["pk"])
        TeamService.archive(team=team, user=request.user, request=request)
        messages.success(request, "Team archived successfully.")
        return redirect("projects:team_directory")


class TeamMemberAddView(ManagerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, pk=kwargs["pk"])
        form = TeamMembershipForm(request.POST, team=team)
        if form.is_valid():
            TeamMembershipService.add_member(
                team=team,
                cleaned_data=form.cleaned_data,
                user=request.user,
                request=request,
            )
            messages.success(request, "Team member added.")
        else:
            messages.error(request, "Unable to add team member.")
        return redirect("projects:team_detail", pk=team.pk)


class TeamMemberRemoveView(ManagerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        membership = get_object_or_404(TeamMembership, pk=kwargs["membership_pk"])
        team = TeamMembershipService.remove_member(
            membership=membership, user=request.user, request=request
        )
        messages.success(request, "Team member removed.")
        return redirect("projects:team_detail", pk=team.pk)


class ProjectDirectoryView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/directory.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        queryset = ProjectSelector.visible_to(self.request.user).filter(
            is_archived=False
        )
        return ProjectSelector.search_and_filter(
            queryset,
            search=self.request.GET.get("q"),
            status=self.request.GET.get("status"),
            priority=self.request.GET.get("priority"),
        )

    def get_template_names(self):
        if is_htmx(self.request):
            return ["projects/partials/directory_grid.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Project.Status.choices
        context["priorities"] = Project.Priority.choices
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "status": self.request.GET.get("status", ""),
            "priority": self.request.GET.get("priority", ""),
        }
        return context


class ProjectDetailView(ProjectAccessMixin, DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_object(self, queryset=None):
        return self.project_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["memberships"] = ProjectSelector.members_for(self.object)
        context["milestones"] = ProjectSelector.milestones_for(self.object)
        context["member_form"] = ProjectMemberForm(project=self.object)
        context["milestone_form"] = MilestoneForm()
        context["progress"] = MilestoneSelector.progress_for(self.object)
        context["role_form"] = ProjectMemberRoleForm()
        return context


class ProjectCreateView(ProjectManagerRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"
    success_url = reverse_lazy("projects:project_directory")

    def form_valid(self, form):
        ProjectService.create(
            cleaned_data=form.cleaned_data, user=self.request.user, request=self.request
        )
        messages.success(self.request, "Project created successfully.")
        return redirect(self.success_url)


class ProjectUpdateView(ProjectManageMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"

    def get_object(self, queryset=None):
        return self.project_object

    def get_success_url(self):
        return reverse("projects:project_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        ProjectService.update(
            project=self.object,
            cleaned_data=form.cleaned_data,
            user=self.request.user,
            request=self.request,
        )
        messages.success(self.request, "Project updated successfully.")
        return redirect(self.get_success_url())


class ProjectArchiveView(ProjectManageMixin, View):
    def post(self, request, *args, **kwargs):
        ProjectService.archive(
            project=self.project_object, user=request.user, request=request
        )
        messages.success(request, "Project archived successfully.")
        return redirect("projects:project_directory")


class ProjectMemberAddView(ProjectManageMixin, View):
    def post(self, request, *args, **kwargs):
        form = ProjectMemberForm(request.POST, project=self.project_object)
        if form.is_valid():
            ProjectMemberService.add_member(
                project=self.project_object,
                cleaned_data=form.cleaned_data,
                user=request.user,
                request=request,
            )
            messages.success(request, "Project member added.")
        else:
            messages.error(request, "Unable to add project member.")
        return redirect("projects:project_detail", pk=self.project_object.pk)


class ProjectMemberRoleUpdateView(ProjectManageMixin, View):
    def post(self, request, *args, **kwargs):
        member = get_object_or_404(
            ProjectMember, pk=kwargs["member_pk"], project=self.project_object
        )
        form = ProjectMemberRoleForm(request.POST, instance=member)
        if form.is_valid():
            ProjectMemberService.change_role(
                member=member,
                role=form.cleaned_data["role"],
                user=request.user,
                request=request,
            )
            messages.success(request, "Project member role updated.")
        else:
            messages.error(request, "Unable to update project member role.")
        return redirect("projects:project_detail", pk=self.project_object.pk)


class ProjectMemberRemoveView(ProjectManageMixin, View):
    def post(self, request, *args, **kwargs):
        member = get_object_or_404(
            ProjectMember, pk=kwargs["member_pk"], project=self.project_object
        )
        ProjectMemberService.remove_member(
            member=member, user=request.user, request=request
        )
        messages.success(request, "Project member removed.")
        return redirect("projects:project_detail", pk=self.project_object.pk)


class MilestoneListView(LoginRequiredMixin, ListView):
    model = Milestone
    template_name = "milestones/list.html"
    context_object_name = "milestones"
    paginate_by = 20

    def get_queryset(self):
        return MilestoneSelector.visible_to(self.request.user)

    def get_template_names(self):
        if is_htmx(self.request):
            return ["milestones/partials/list.html"]
        return [self.template_name]


class MilestoneCreateView(ProjectManageMixin, View):
    def post(self, request, *args, **kwargs):
        form = MilestoneForm(request.POST)
        if form.is_valid():
            MilestoneService.create(
                project=self.project_object,
                cleaned_data=form.cleaned_data,
                user=request.user,
                request=request,
            )
            messages.success(request, "Milestone created.")
        else:
            messages.error(request, "Unable to create milestone.")
        return redirect("projects:project_detail", pk=self.project_object.pk)


class MilestoneUpdateView(ProjectManageMixin, UpdateView):
    model = Milestone
    form_class = MilestoneForm
    template_name = "milestones/form.html"
    pk_url_kwarg = "milestone_pk"

    def get_queryset(self):
        return Milestone.objects.filter(project=self.project_object)

    def get_success_url(self):
        return reverse("projects:project_detail", kwargs={"pk": self.project_object.pk})

    def form_valid(self, form):
        MilestoneService.update(
            milestone=self.object,
            cleaned_data=form.cleaned_data,
            user=self.request.user,
            request=self.request,
        )
        messages.success(self.request, "Milestone updated.")
        return redirect(self.get_success_url())


class MilestoneDeleteView(ProjectManageMixin, View):
    def post(self, request, *args, **kwargs):
        milestone = get_object_or_404(
            Milestone, pk=kwargs["milestone_pk"], project=self.project_object
        )
        MilestoneService.delete(milestone=milestone, user=request.user, request=request)
        messages.success(request, "Milestone deleted.")
        return redirect("projects:project_detail", pk=self.project_object.pk)

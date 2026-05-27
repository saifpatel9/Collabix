from django.urls import path

from .views import (
    MilestoneCreateView,
    MilestoneDeleteView,
    MilestoneListView,
    MilestoneUpdateView,
    ProjectArchiveView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectDirectoryView,
    ProjectMemberAddView,
    ProjectMemberRemoveView,
    ProjectMemberRoleUpdateView,
    ProjectUpdateView,
    TeamArchiveView,
    TeamCreateView,
    TeamDetailView,
    TeamDirectoryView,
    TeamMemberAddView,
    TeamMemberRemoveView,
    TeamUpdateView,
)

app_name = "projects"

urlpatterns = [
    path("projects/", ProjectDirectoryView.as_view(), name="project_directory"),
    path("projects/create/", ProjectCreateView.as_view(), name="project_create"),
    path("projects/<uuid:pk>/", ProjectDetailView.as_view(), name="project_detail"),
    path(
        "projects/<uuid:pk>/edit/", ProjectUpdateView.as_view(), name="project_update"
    ),
    path(
        "projects/<uuid:pk>/archive/",
        ProjectArchiveView.as_view(),
        name="project_archive",
    ),
    path(
        "projects/<uuid:project_pk>/members/add/",
        ProjectMemberAddView.as_view(),
        name="project_member_add",
    ),
    path(
        "projects/<uuid:project_pk>/members/<uuid:member_pk>/role/",
        ProjectMemberRoleUpdateView.as_view(),
        name="project_member_role",
    ),
    path(
        "projects/<uuid:project_pk>/members/<uuid:member_pk>/remove/",
        ProjectMemberRemoveView.as_view(),
        name="project_member_remove",
    ),
    path("milestones/", MilestoneListView.as_view(), name="milestone_list"),
    path(
        "projects/<uuid:project_pk>/milestones/add/",
        MilestoneCreateView.as_view(),
        name="milestone_create",
    ),
    path(
        "projects/<uuid:project_pk>/milestones/<uuid:milestone_pk>/edit/",
        MilestoneUpdateView.as_view(),
        name="milestone_update",
    ),
    path(
        "projects/<uuid:project_pk>/milestones/<uuid:milestone_pk>/delete/",
        MilestoneDeleteView.as_view(),
        name="milestone_delete",
    ),
    path("teams/", TeamDirectoryView.as_view(), name="team_directory"),
    path("teams/create/", TeamCreateView.as_view(), name="team_create"),
    path("teams/<uuid:pk>/", TeamDetailView.as_view(), name="team_detail"),
    path("teams/<uuid:pk>/edit/", TeamUpdateView.as_view(), name="team_update"),
    path("teams/<uuid:pk>/archive/", TeamArchiveView.as_view(), name="team_archive"),
    path(
        "teams/<uuid:pk>/members/add/",
        TeamMemberAddView.as_view(),
        name="team_member_add",
    ),
    path(
        "teams/members/<uuid:membership_pk>/remove/",
        TeamMemberRemoveView.as_view(),
        name="team_member_remove",
    ),
]

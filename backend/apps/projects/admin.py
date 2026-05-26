from django.contrib import admin

from .models import Milestone, Project, ProjectMember, Team, TeamMembership


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "team_lead", "is_active")
    list_filter = ("is_active", "department")
    search_fields = ("name", "description", "team_lead__user__full_name")
    inlines = [TeamMembershipInline]


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "owner", "department", "status", "priority")
    list_filter = ("status", "priority", "department", "is_archived")
    search_fields = ("code", "name", "description", "owner__user__full_name")
    inlines = [ProjectMemberInline, MilestoneInline]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ("project", "employee", "role")
    list_filter = ("role",)
    search_fields = ("project__name", "project__code", "employee__user__full_name")


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "due_date", "status")
    list_filter = ("status", "due_date")
    search_fields = ("name", "project__name", "project__code")

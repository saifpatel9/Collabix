from apps.core.rbac.permissions import (
    can_manage_projects,
    can_manage_tasks,
    can_view_employee_directory,
    is_admin,
)


def can_create_project(user):
    return can_manage_projects(user)


def can_create_team(user):
    return can_manage_projects(user)


def can_view_people(user):
    return can_view_employee_directory(user)


def can_view_admin_dashboard(user):
    return is_admin(user)


def can_view_all_activity(user):
    return is_admin(user)

def can_manage_tasks(user):
    return can_manage_tasks(user)
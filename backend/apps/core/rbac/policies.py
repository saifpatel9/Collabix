from apps.core.rbac.permissions import (
    ROLE_EMPLOYEE_LIST_ACCESS,
    ROLE_MANAGER_REQUIRED,
    ROLE_PROJECT_MANAGER_REQUIRED,
    is_admin,
    user_has_role,
)

def can_create_project(user):
    return user_has_role(user, ROLE_PROJECT_MANAGER_REQUIRED)

def can_create_team(user):
    return user_has_role(user, ROLE_MANAGER_REQUIRED)

def can_view_people(user):
    return user_has_role(user, ROLE_EMPLOYEE_LIST_ACCESS)

def can_view_admin_dashboard(user):
    return is_admin(user)

def can_view_all_activity(user):
    return is_admin(user)

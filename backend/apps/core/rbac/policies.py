from apps.core.rbac.utils import is_admin, is_manager

def can_create_project(user):
    return is_admin(user) or is_manager(user)

def can_create_team(user):
    return is_admin(user) or is_manager(user)

def can_view_people(user):
    return is_admin(user)

def can_view_admin_dashboard(user):
    return is_admin(user)

def can_view_all_activity(user):
    return is_admin(user)
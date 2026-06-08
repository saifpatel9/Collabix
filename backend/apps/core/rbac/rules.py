from apps.accounts.models import User
from apps.projects.models import ProjectMember

from .permissions import is_authenticated, user_has_role


class ProjectRole:
    OWNER = "owner"
    PROJECT_MANAGER = ProjectMember.Role.PROJECT_MANAGER
    TEAM_LEAD = ProjectMember.Role.TEAM_LEAD
    CONTRIBUTOR = ProjectMember.Role.CONTRIBUTOR
    VIEWER = ProjectMember.Role.VIEWER


def user_project_role(user, project):
    if not is_authenticated(user):
        return None
    if project.owner_id and project.owner.user_id == user.id:
        return ProjectRole.OWNER
    membership = project.memberships.filter(employee__user=user).first()
    return membership.role if membership else None


def can_manage_project(user, project) -> bool:
    if not is_authenticated(user):
        return False
    if user.is_superuser or user.role in (User.Role.ADMIN, User.Role.PROJECT_MANAGER):
        return True
    return user_project_role(user, project) in (
        ProjectRole.OWNER,
        ProjectRole.PROJECT_MANAGER,
    )


def can_view_project(user, project) -> bool:
    if can_manage_project(user, project):
        return True
    return user_project_role(user, project) in (
        ProjectRole.TEAM_LEAD,
        ProjectRole.CONTRIBUTOR,
        ProjectRole.VIEWER,
    )


def can_manage_milestone(user, project) -> bool:
    if can_manage_project(user, project):
        return True
    return user_project_role(user, project) == ProjectRole.TEAM_LEAD


def is_task_owner(user, task) -> bool:
    return is_authenticated(user) and task.created_by.user_id == user.id


def is_task_assignee(user, task) -> bool:
    return is_authenticated(user) and task.assignments.filter(employee__user=user).exists()


def is_project_team_lead(user, task) -> bool:
    return is_authenticated(user) and task.project.memberships.filter(
        employee__user=user, role=ProjectMember.Role.TEAM_LEAD
    ).exists()


def has_task_admin_role(user) -> bool:
    return user_has_role(
        user, (User.Role.ADMIN, User.Role.PROJECT_MANAGER)
    )


def can_view_task(user, task) -> bool:
    if has_task_admin_role(user) or is_task_owner(user, task) or is_task_assignee(user, task):
        return True
    project_role = user_project_role(user, task.project)
    if project_role in (
        ProjectRole.OWNER,
        ProjectRole.PROJECT_MANAGER,
        ProjectRole.TEAM_LEAD,
        ProjectRole.VIEWER,
    ):
        return True
    if project_role == ProjectRole.CONTRIBUTOR:
        return is_task_assignee(user, task) or is_task_owner(user, task)
    return False


def can_manage_task(user, task) -> bool:
    return (
        has_task_admin_role(user)
        or is_task_owner(user, task)
        or is_project_team_lead(user, task)
        or can_manage_project(user, task.project)
    )


def can_edit_task(user, task) -> bool:
    return can_manage_task(user, task)


def can_execute_task(user, task) -> bool:
    return can_manage_task(user, task) or is_task_assignee(user, task)


def can_access_employee(user, employee) -> bool:
    if not is_authenticated(user):
        return False
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True
    if user.role == User.Role.HR_MANAGER:
        return True
    if user.role == User.Role.DEPARTMENT_ADMIN:
        return employee.department and employee.department.name == user.department
    if user.role == User.Role.MANAGER:
        return (employee.manager and employee.manager.user_id == user.id) or (employee.user_id == user.id)
    if user.role == User.Role.PROJECT_MANAGER:
        return employee.user_id == user.id
    return employee.user_id == user.id

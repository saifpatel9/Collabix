import logging

from apps.accounts.models import User
from apps.projects.models import ProjectMember

from .permissions import is_authenticated, user_has_role

logger = logging.getLogger(__name__)

def log_access_denied(user, action, resource=None):
    logger.warning(
        "RBAC access denied user_id=%s role=%s action=%s resource=%s",
        getattr(user, "id", None),
        getattr(user, "role", None),
        action,
        resource,
    )

# =========================
# Project Roles
# =========================

class ProjectRole:
    OWNER = "owner"
    PROJECT_MANAGER = ProjectMember.Role.PROJECT_MANAGER
    TEAM_LEAD = ProjectMember.Role.TEAM_LEAD
    CONTRIBUTOR = ProjectMember.Role.CONTRIBUTOR
    VIEWER = ProjectMember.Role.VIEWER


# =========================
# Project Role Resolver
# =========================

def user_project_role(user, project):
    if not is_authenticated(user):
        return None

    # 1. Owner override
    if project.owner_id and project.owner.employee_id == user.id:
        return "owner"

    # 2. Membership role
    membership = project.memberships.filter(employee__user=user).first()
    if membership:
        return membership.role

    return None


# =========================
# Project Permissions
# =========================

def can_manage_project(user, project) -> bool:
    if not is_authenticated(user):
        return False

    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    role = user_project_role(user, project)

    allowed = role in (
        "owner",
        ProjectMember.Role.PROJECT_MANAGER,
    )

    if not allowed:
        log_access_denied(
            user,
            "manage_project",
            project.pk,
        )

    return allowed


def can_view_project(user, project) -> bool:
    if not is_authenticated(user):
        return False

    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    role = user_project_role(user, project)

    allowed = role in (
        "owner",
        ProjectMember.Role.PROJECT_MANAGER,
        ProjectMember.Role.TEAM_LEAD,
        ProjectMember.Role.CONTRIBUTOR,
        ProjectMember.Role.VIEWER,
    )

    if not allowed:
        log_access_denied(
            user,
            "view_project",
            project.pk,
        )

    return allowed


def can_manage_milestone(user, project) -> bool:
    if not is_authenticated(user):
        return False

    if can_manage_project(user, project):
        return True

    role = user_project_role(user, project)

    return role == ProjectMember.Role.TEAM_LEAD

# =========================
# Task Role Helpers
# =========================

def is_task_owner(user, task) -> bool:
    return is_authenticated(user) and task.created_by.user_id == user.id


def is_task_assignee(user, task) -> bool:
    return is_authenticated(user) and task.assignments.filter(employee__user=user).exists()


def is_project_team_lead(user, task) -> bool:
    return (
        is_authenticated(user)
        and task.project.memberships.filter(
            employee__user=user,
            role=ProjectMember.Role.TEAM_LEAD
        ).exists()
    )


def has_task_admin_role(user) -> bool:
    return user_has_role(
        user,
        (User.Role.ADMIN,)
    )

def is_manager_of_task(user, task) -> bool:
    if not is_authenticated(user):
        return False

    if user.role != User.Role.MANAGER:
        return False

    # Task creator is direct report
    if (
        task.created_by
        and task.created_by.manager
        and task.created_by.manager.user_id == user.id
    ):
        return True

    # Any assignee is direct report
    return task.assignments.filter(
        employee__manager__user_id=user.id
    ).exists()


# =========================
# Task Permissions
# =========================

def can_view_task(user, task) -> bool:
    if not is_authenticated(user):
        return False

    # 1. Admin override
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    # 2. Project-level access
    project_role = user_project_role(user, task.project)
    if project_role in (
        "owner",
        ProjectMember.Role.PROJECT_MANAGER,
        ProjectMember.Role.TEAM_LEAD,
        ProjectMember.Role.CONTRIBUTOR,
        ProjectMember.Role.VIEWER,
    ):
        return True
    # Manager can view direct report tasks
    if is_manager_of_task(user, task):
        return True

    # 3. Task-level access
    if task.created_by.user_id == user.id:
        return True

    if task.assignments.filter(employee__user=user).exists():
        return True

    log_access_denied(
        user,
        "view_task",
        task.pk,
    )

    return False


def can_manage_task(user, task) -> bool:
    if not is_authenticated(user):
        return False

    # 1. Admin override
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    # 2. Project manager or owner
    project_role = user_project_role(user, task.project)
    if project_role in ("owner", ProjectMember.Role.PROJECT_MANAGER):
        return True

    # 3. Team lead can manage tasks in project
    if project_role == ProjectMember.Role.TEAM_LEAD:
        return True

    # Manager can manage direct report tasks
    if is_manager_of_task(user, task):
        return True
    # 4. Task creator can manage
    if task.created_by.user_id == user.id:
        return True

    log_access_denied(
        user,
        "manage_task",
        task.pk,
    )

    return False


def can_edit_task(user, task) -> bool:
    return can_manage_task(user, task)


def can_execute_task(user, task) -> bool:
    return (
        can_manage_task(user, task)
        or task.assignments.filter(employee__user=user).exists()
    )

def can_comment_task(user, task) -> bool:
    return can_view_task(user, task)

def can_attach_task(user, task) -> bool:
    return can_manage_task(user, task) or task.assignments.filter(employee__user=user).exists()


# =========================
# Employee Access Control
# =========================

def can_access_employee(user, employee) -> bool:
    if not is_authenticated(user):
        return False

    # 1. Superuser / Admin override
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    # 2. HR full access
    if user.role == User.Role.HR_MANAGER:
        return True

    # 3. Department Admin → same department only
    if user.role == User.Role.DEPARTMENT_ADMIN:
        user_profile = getattr(user, "employee_profile", None)

        if not user_profile:
            log_access_denied(
                user,
                "access_employee",
                employee.pk,
            )
            return False

        allowed = (
            getattr(user_profile, "department_id", None)
            == getattr(employee, "department_id", None)
        )

        if not allowed:
            log_access_denied(
                user,
                "access_employee",
                employee.pk,
            )

        return allowed

    # 4. Manager → direct reports + self
    if user.role == User.Role.MANAGER:
        allowed = (
            (employee.manager and employee.manager.user_id == user.id)
            or employee.user_id == user.id
        )

        if not allowed:
            log_access_denied(
                user,
                "access_employee",
                employee.pk,
            )

        return allowed

    # 5. Project Manager → self only
    if user.role == User.Role.PROJECT_MANAGER:
        allowed = employee.user_id == user.id

        if not allowed:
            log_access_denied(
                user,
                "access_employee",
                employee.pk,
            )

        return allowed

    # 6. Employee → self only
    allowed = employee.user_id == user.id

    if not allowed:
        log_access_denied(
            user,
            "access_employee",
            employee.pk,
        )

    return allowed
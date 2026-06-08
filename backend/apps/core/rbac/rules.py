from apps.accounts.models import User
from apps.projects.models import ProjectMember

from .permissions import is_authenticated, user_has_role


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

    if user.is_superuser or user.role in (
        User.Role.ADMIN,
        User.Role.PROJECT_MANAGER,
    ):
        return True

    role = user_project_role(user, project)

    return role in (
        "owner",
        ProjectMember.Role.PROJECT_MANAGER,
    )


def can_view_project(user, project) -> bool:
    if not is_authenticated(user):
        return False

    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    role = user_project_role(user, project)

    return role in (
        "owner",
        ProjectMember.Role.PROJECT_MANAGER,
        ProjectMember.Role.TEAM_LEAD,
        ProjectMember.Role.CONTRIBUTOR,
        ProjectMember.Role.VIEWER,
    )


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
    return user_has_role(user, (User.Role.ADMIN, User.Role.PROJECT_MANAGER))


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

    # 3. Task-level access
    if task.created_by.user_id == user.id:
        return True

    if task.assignments.filter(employee__user=user).exists():
        return True

    # 4. Manager fallback
    if user.role == User.Role.MANAGER:
        return True

    return False


def can_manage_task(user, task) -> bool:
    if not is_authenticated(user):
        return False

    # 1. Admin override
    if user.is_superuser or user.role in (
        User.Role.ADMIN,
        User.Role.PROJECT_MANAGER,
    ):
        return True

    # 2. Project manager or owner
    project_role = user_project_role(user, task.project)
    if project_role in ("owner", ProjectMember.Role.PROJECT_MANAGER):
        return True

    # 3. Team lead can manage tasks in project
    if project_role == ProjectMember.Role.TEAM_LEAD:
        return True

    # 4. Task creator can manage
    if task.created_by.user_id == user.id:
        return True

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
            return False

        return (
            getattr(user_profile, "department_id", None)
            == getattr(employee, "department_id", None)
        )

    # 4. Manager → direct reports + self
    if user.role == User.Role.MANAGER:
        return (
            (employee.manager and employee.manager.user_id == user.id)
            or employee.user_id == user.id
        )

    # 5. Project Manager → self only
    if user.role == User.Role.PROJECT_MANAGER:
        return employee.user_id == user.id

    # 6. Employee → self only
    return employee.user_id == user.id
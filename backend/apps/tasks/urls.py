from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("tasks/", views.TaskListView.as_view(), name="task_list"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="task_create"),
    path("tasks/board/", views.TaskBoardView.as_view(), name="task_board"),
    path("tasks/archive/", views.TaskArchiveListView.as_view(), name="task_archive"),
    path("tasks/<uuid:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("tasks/<uuid:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<uuid:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    path(
        "tasks/<uuid:pk>/archive/",
        views.TaskArchiveView.as_view(),
        name="task_archive_action",
    ),
    path(
        "tasks/<uuid:pk>/status/",
        views.TaskStatusUpdateView.as_view(),
        name="task_status_update",
    ),
    path(
        "tasks/<uuid:pk>/priority/",
        views.TaskPriorityUpdateView.as_view(),
        name="task_priority_update",
    ),
    path(
        "tasks/<uuid:pk>/assignments/",
        views.TaskAssignmentView.as_view(),
        name="task_assignment",
    ),
    path(
        "tasks/<uuid:pk>/comments/",
        views.TaskCommentView.as_view(),
        name="task_comment",
    ),
    path(
        "tasks/<uuid:pk>/attachments/",
        views.TaskAttachmentView.as_view(),
        name="task_attachment",
    ),
    path(
        "tasks/<uuid:pk>/checklists/",
        views.TaskChecklistView.as_view(),
        name="task_checklist",
    ),
    path(
        "tasks/<uuid:pk>/checklists/<uuid:checklist_pk>/items/",
        views.TaskChecklistItemView.as_view(),
        name="task_checklist_item",
    ),
    path(
        "tasks/<uuid:pk>/checklists/items/<uuid:item_pk>/toggle/",
        views.TaskChecklistToggleView.as_view(),
        name="task_checklist_toggle",
    ),
    path(
        "tasks/<uuid:pk>/dependencies/",
        views.TaskDependencyView.as_view(),
        name="task_dependency",
    ),
    path(
        "tasks/<uuid:pk>/dependencies/<uuid:dependency_pk>/delete/",
        views.TaskDependencyDeleteView.as_view(),
        name="task_dependency_delete",
    ),
]

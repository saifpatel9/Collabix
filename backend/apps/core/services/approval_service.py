from django.db import transaction

from apps.core.models import ApprovalInstance, ApprovalStage, ApprovalWorkflow


class ApprovalWorkflowService:
    @staticmethod
    def active_workflows():
        return ApprovalWorkflow.objects.filter(is_active=True).prefetch_related(
            "stages"
        )

    @staticmethod
    @transaction.atomic
    def create_instance(*, workflow, submitted_by):
        first_stage = workflow.stages.order_by("stage_number").first()
        return ApprovalInstance.objects.create(
            workflow=workflow,
            submitted_by=submitted_by,
            current_stage=first_stage,
            status=(
                ApprovalInstance.Status.PENDING
                if first_stage
                else ApprovalInstance.Status.DRAFT
            ),
        )

    @staticmethod
    def pending_count():
        return ApprovalInstance.objects.filter(
            status=ApprovalInstance.Status.PENDING
        ).count()

    @staticmethod
    def create_stage(
        *,
        workflow,
        stage_number,
        approver_role="",
        approver_designation=None,
        auto_escalation_days=0,
    ):
        return ApprovalStage.objects.create(
            workflow=workflow,
            stage_number=stage_number,
            approver_role=approver_role,
            approver_designation=approver_designation,
            auto_escalation_days=auto_escalation_days,
        )

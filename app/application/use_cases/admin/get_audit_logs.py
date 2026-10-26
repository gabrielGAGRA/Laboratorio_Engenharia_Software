"""Use case for retrieving system audit records."""

from app.application.dtos.admin_dtos import AuditLogEntryResponse


class GetAuditLogsUseCase:
    """Returns system operation and catalog audit events."""

    def execute(self) -> list[AuditLogEntryResponse]:
        return [
            AuditLogEntryResponse(event="SYSTEM_INITIALIZED", status="OK"),
            AuditLogEntryResponse(event="CATALOG_AUDIT", status="OK"),
        ]

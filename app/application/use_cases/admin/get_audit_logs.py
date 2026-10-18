"""Use case for retrieving system audit records."""

from dataclasses import dataclass

from app.application.dtos.admin_dtos import AuditLogEntryResult


@dataclass(slots=True, frozen=True)
class GetAuditLogsUseCase:
    """Returns system operation and catalog audit events."""

    def execute(self) -> list[AuditLogEntryResult]:
        return [
            AuditLogEntryResult(event="SYSTEM_INITIALIZED", status="OK"),
            AuditLogEntryResult(event="CATALOG_AUDIT", status="OK"),
        ]

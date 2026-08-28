"""
Models used by the guardrail system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GuardrailStatus(str, Enum):

    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


@dataclass
class GuardrailCheck:

    name: str

    status: GuardrailStatus

    message: str

    details: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class GuardrailResult:

    passed: bool

    status: GuardrailStatus

    checks: list[GuardrailCheck] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def add_check(
        self,
        check: GuardrailCheck,
    ) -> None:

        self.checks.append(check)

        if check.status == GuardrailStatus.FAIL:

            self.passed = False

            self.status = GuardrailStatus.FAIL

            self.errors.append(
                check.message
            )

        elif (
            check.status
            == GuardrailStatus.WARNING
        ):

            self.warnings.append(
                check.message
            )

            if self.status != GuardrailStatus.FAIL:
                self.status = GuardrailStatus.WARNING

    def to_dict(self) -> dict[str, Any]:

        return {
            "passed": self.passed,
            "status": self.status.value,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "details": check.details,
                }
                for check in self.checks
            ],
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }
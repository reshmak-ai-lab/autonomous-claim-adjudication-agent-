from typing import Any

from .room_rent import evaluate_room_rent
from .proportional_deduction import (
    calculate_proportional_deduction,
)
from .waiting_period import evaluate_waiting_period
from .sum_insured import evaluate_sum_insured
from .copay import calculate_copay
from .deductible import apply_deductible
from .exclusions import evaluate_exclusion
from .non_payable_items import (
    evaluate_non_payable_item,
)


class RuleEngine:
    """
    Central deterministic rule engine for claim adjudication.
    """

    def evaluate_room(
        self,
        actual_room_rent: float,
        eligible_room_rent: float,
    ) -> dict[str, Any]:

        return evaluate_room_rent(
            actual_room_rent,
            eligible_room_rent,
        )

    def evaluate_proportional_deduction(
        self,
        actual_room_rent: float,
        eligible_room_rent: float,
        bill_amount: float,
    ) -> dict[str, Any]:

        return calculate_proportional_deduction(
            actual_room_rent,
            eligible_room_rent,
            bill_amount,
        )

    def evaluate_waiting_period(
        self,
        policy_start_date,
        admission_date,
        waiting_period_days: int,
    ) -> dict[str, Any]:

        return evaluate_waiting_period(
            policy_start_date,
            admission_date,
            waiting_period_days,
        )

    def evaluate_sum_insured(
        self,
        claimed_amount: float,
        sum_insured: float,
        already_paid: float = 0.0,
    ) -> dict[str, Any]:

        return evaluate_sum_insured(
            claimed_amount,
            sum_insured,
            already_paid,
        )

    def calculate_copay(
        self,
        eligible_amount: float,
        copay_percentage: float,
    ) -> dict[str, Any]:

        return calculate_copay(
            eligible_amount,
            copay_percentage,
        )

    def apply_deductible(
        self,
        eligible_amount: float,
        deductible: float,
    ) -> dict[str, Any]:

        return apply_deductible(
            eligible_amount,
            deductible,
        )

    def evaluate_exclusion(
        self,
        item: str,
        exclusions: list[str],
    ) -> dict[str, Any]:

        return evaluate_exclusion(
            item,
            exclusions,
        )

    def evaluate_non_payable(
        self,
        item: str,
        non_payable_items: list[str],
    ) -> dict[str, Any]:

        return evaluate_non_payable_item(
            item,
            non_payable_items,
        )
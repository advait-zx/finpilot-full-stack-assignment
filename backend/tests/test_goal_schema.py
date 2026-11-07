from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.goals import GoalCreate


def test_goal_requires_positive_target():
    with pytest.raises(ValidationError):
        GoalCreate(
            goal_type="RETIREMENT",
            goal_name="Retirement",
            target_amount=0,
            current_funded_amount=0,
            target_date=date(2035, 1, 1),
            priority="HIGH",
        )


def test_goal_normalises_enums():
    g = GoalCreate(
        goal_type="travel",
        goal_name="Japan",
        target_amount=100000,
        current_funded_amount=10000,
        target_date=date(2028, 1, 1),
        priority="medium",
    )
    assert g.goal_type == "TRAVEL" and g.priority == "MEDIUM"

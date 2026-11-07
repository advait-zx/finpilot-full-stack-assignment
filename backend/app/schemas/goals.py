from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator

GOAL_TYPES = {"EDUCATION","EMERGENCY_FUND","HOME_PURCHASE","RETIREMENT","TRAVEL","WEALTH_CREATION"}
PRIORITIES = {"LOW","MEDIUM","HIGH"}

class GoalCreate(BaseModel):
    goal_type: str
    goal_name: str = Field(min_length=2, max_length=180)
    target_amount: Decimal = Field(gt=0)
    current_funded_amount: Decimal = Field(ge=0)
    target_date: date
    priority: str

    @model_validator(mode="after")
    def validate_enums(self):
        self.goal_type = self.goal_type.upper()
        self.priority = self.priority.upper()
        if self.goal_type not in GOAL_TYPES:
            raise ValueError("invalid goal_type")
        if self.priority not in PRIORITIES:
            raise ValueError("invalid priority")
        return self

class GoalUpdate(BaseModel):
    goal_name: str | None = Field(default=None, min_length=2, max_length=180)
    target_amount: Decimal | None = Field(default=None, gt=0)
    current_funded_amount: Decimal | None = Field(default=None, ge=0)
    target_date: date | None = None
    priority: str | None = None

    @model_validator(mode="after")
    def validate_priority(self):
        if self.priority is not None:
            self.priority = self.priority.upper()
            if self.priority not in PRIORITIES:
                raise ValueError("invalid priority")
        return self

class GoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    goal_id: str
    customer_id: str
    goal_type: str
    goal_name: str
    target_amount: Decimal
    current_funded_amount: Decimal
    target_date: date
    priority: str
    funded_percentage: float
    overdue: bool
    inconsistent: bool

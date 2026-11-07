from datetime import date
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.db.session import get_db
from app.models.entities import Customer, Goal
from app.schemas.goals import GoalCreate, GoalOut, GoalUpdate

router = APIRouter(tags=["goals"], dependencies=[Depends(current_user)])

def serialize(g: Goal) -> GoalOut:
    pct = float(g.current_funded_amount / g.target_amount * 100) if g.target_amount else 0
    return GoalOut(goal_id=g.goal_id, customer_id=g.customer_id, goal_type=g.goal_type, goal_name=g.goal_name, target_amount=g.target_amount, current_funded_amount=g.current_funded_amount, target_date=g.target_date, priority=g.priority, funded_percentage=round(pct,2), overdue=g.target_date < date.today() and g.current_funded_amount < g.target_amount, inconsistent=g.current_funded_amount > g.target_amount)

@router.get("/customers/{customer_id}/goals", response_model=list[GoalOut])
def list_goals(customer_id: str, db: Session = Depends(get_db)):
    if not db.get(Customer, customer_id): raise HTTPException(404,"Customer not found")
    return [serialize(g) for g in db.scalars(select(Goal).where(Goal.customer_id==customer_id).order_by(Goal.target_date)).all()]

@router.post("/customers/{customer_id}/goals", response_model=GoalOut, status_code=201)
def create_goal(customer_id: str, payload: GoalCreate, db: Session = Depends(get_db)):
    if not db.get(Customer, customer_id): raise HTTPException(404,"Customer not found")
    g=Goal(goal_id=f"G-{uuid4().hex[:12].upper()}", customer_id=customer_id, **payload.model_dump())
    db.add(g); db.commit(); db.refresh(g)
    return serialize(g)

@router.patch("/goals/{goal_id}", response_model=GoalOut)
def update_goal(goal_id: str, payload: GoalUpdate, db: Session = Depends(get_db)):
    g=db.get(Goal,goal_id)
    if not g: raise HTTPException(404,"Goal not found")
    for k,v in payload.model_dump(exclude_unset=True).items(): setattr(g,k,v)
    db.commit(); db.refresh(g)
    return serialize(g)

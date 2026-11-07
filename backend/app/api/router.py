from fastapi import APIRouter

from app.api.routes import admin, auth, customers, goals, portfolio, transactions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(customers.router)
api_router.include_router(portfolio.router)
api_router.include_router(transactions.router)
api_router.include_router(goals.router)
api_router.include_router(admin.router)

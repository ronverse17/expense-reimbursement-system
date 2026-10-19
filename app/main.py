
from fastapi import FastAPI

from app.api.routes.invoices import router as invoices_router


app = FastAPI(
    title="Expense Reimbursement System",
    description="Backend API for invoice processing and expense claims.",
    version="0.1.0",
)

app.include_router(invoices_router)


@app.get("/")
def root():
    return {
        "message": "Expense Reimbursement System API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }

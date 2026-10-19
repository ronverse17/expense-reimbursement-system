from fastapi import FastAPI

app = FastAPI(
    title="Expense Reimbursement System",
    description="Backend API for invoice processing and expense claims.",
    version="0.1.0",
)


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

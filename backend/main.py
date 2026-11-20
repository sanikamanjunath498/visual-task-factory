import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Allow importing from the factory folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from factory.generator import generate_task, OUTPUT_DIR
from factory.evaluator import evaluate_model

app = FastAPI(title="Visual Task Factory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated synthetic images directly to frontend
app.mount("/static", StaticFiles(directory=OUTPUT_DIR), name="static")

TASK_DB = []

class BatchRequest(BaseModel):
    count: int = 3
    difficulty: int = 3

@app.post("/api/generate")
def create_batch(req: BatchRequest):
    new_tasks = []
    start_id = len(TASK_DB) + 1
    for i in range(req.count):
        task = generate_task(task_id=start_id + i, difficulty=req.difficulty)
        TASK_DB.append(task)
        new_tasks.append(task)
    return {"generated": len(new_tasks), "tasks": new_tasks}

@app.post("/api/evaluate")
def run_benchmark(model_name: str = "gemini-2.5-flash"):
    if not TASK_DB:
        return {
            "model": model_name,
            "total_tested": 0,
            "accuracy_percent": 0,
            "results": []
        }

    # Evaluates the latest 3 tasks so it finishes in ~6 seconds without hitting Free Tier rate limits
    results = []
    for task in TASK_DB[-3:]:
        res = evaluate_model(task, model_name=model_name)
        results.append(res)
    
    accuracy = sum(1 for r in results if r["passed"]) / len(results)
    return {
        "model": model_name,
        "total_tested": len(results),
        "accuracy_percent": round(accuracy * 100, 1),
        "results": results
    }

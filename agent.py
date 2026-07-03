# Entry point for web server
from fastapi import FastAPI
import uvicorn
from multiagent_orchestration import full_intel_workflow

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/research")
async def research(topic: str):
    report = await full_intel_workflow(topic)
    return {"report": report}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
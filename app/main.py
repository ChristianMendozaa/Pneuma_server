from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatRequest, ChatResponse
from .agent import analyze_data
from dotenv import load_dotenv
import os
import traceback


load_dotenv()

app = FastAPI(title="Pneuma API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "service": "Pneuma Backend"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Call the agent
        result = analyze_data(request.message, request.csv_url)
        
        # Validate/clean result to match response model if necessary
        # The agent returns a dict, Pydantic will validate it against ChatResponse
        return result
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse
from agent import handle_user_message

app = FastAPI(title="Eightfold Company Research Assistant")

# For demo, allow everything (you can tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    result = handle_user_message(
        session_id=req.session_id,
        message=req.message,
        persona=req.persona,
    )
    return ChatResponse(
        reply=result["reply"],
        mode=result["mode"],
        company=result["company"],
        account_plan=result["account_plan"],
    )

@app.get("/health")
def health():
    return {"status": "ok"}
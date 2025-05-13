from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from weaviate_calibrate_companies import query_weaviate_agent
from crew.src.company_description_retrieval_automation.crew import CompanyDescriptionRetrievalAutomationCrew

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class CompanyRequest(BaseModel):
    company_name: str

class ChatResponse(BaseModel):
    response: str

@app.post("/company-info")
async def get_company_description(request: CompanyRequest):
    try:
        crew = CompanyDescriptionRetrievalAutomationCrew()
        result = crew.crew().kickoff(inputs={'company_name': request.company_name})
        return {"description": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    resp = query_weaviate_agent(req.message)
    return ChatResponse(response=resp)

@app.get("/")
async def root():
    return {"message": "Hello World"} 
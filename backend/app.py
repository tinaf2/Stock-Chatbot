from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pinecone import Pinecone
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from codebase_rag import perform_rag

load_dotenv()  

# CORS configuration to allow React frontend to communicate with the backend
origins = [
    "http://localhost:3000",  # React development server
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define Pydantic models for request and response
class QueryRequest(BaseModel):
    query: str  # User's question/query

class QueryResponse(BaseModel):
    response: str  # LLM's response


# Define POST endpoint for handling user queries
@app.post("/query", response_model=QueryResponse)
async def handle_query(query_request: QueryRequest):
    augmented_query = query_request.query  # Get query from the frontend
    
    try:
        response = perform_rag(augmented_query)  # Perform RAG generation using the query
        
        return QueryResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


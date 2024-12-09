from http import client
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import os
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv() 

def get_huggingface_embeddings(text, model_name="sentence-transformers/all-mpnet-base-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(text)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

pinecone_index = pc.Index("stocks")

if 'stocks' not in pc.list_indexes().names():
    pc.create_index(
        name='stocks',
        dimension=768,  
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1',
        )
    )
    pinecone_index = pc.Index("stocks")  # Access the newly created index

# Initialize vector store
vectorstore = Pinecone(index_name="stocks", embedding=HuggingFaceEmbeddings())

# Initialize the Groq client with the provided API key
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")  
)


def perform_rag(query):
    query_embedding = get_huggingface_embeddings(query)

    top_matches = pinecone_index.query(vector=query_embedding.tolist(), top_k=5, include_metadata=True, namespace="stocks")

    # Get the list of retrieved texts
    contexts = [item['metadata']['text'] for item in top_matches['matches']]

    print(f"Contexts fetched from Pinecone: {contexts}")

    augmented_query = "<CONTEXT>\n" + "\n\n-------\n\n".join(contexts[ : 10]) + "\n-------\n</CONTEXT>\n\n\n\nMY QUESTION:\n" + query

    print(f"Augmented query: {augmented_query}")


    system_prompt = f"""You are an expert at providing answers about stocks. Please answer my question provided."""

    llm_response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": augmented_query}
        ]
    )

    return llm_response.choices[0].message.content





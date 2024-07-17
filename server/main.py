from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import joblib
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Constants
MODEL_ROLE = 'ai'
DATA_DIR = 'data/'
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    chat_id: str
    chat_title: str
    messages: list[Message]
    gemini_history: list[dict]

class SendMessageRequest(BaseModel):
    chat_id: str
    user_message: str

class TranslationRequest(BaseModel):
    source_language: str
    content: str
    target_language: str

# In-memory store for past chats
try:
    past_chats = joblib.load(f'{DATA_DIR}/past_chats_list')
except FileNotFoundError:
    past_chats = {}

# Helper functions
def save_chat_history(chat_id, messages, gemini_history):
    joblib.dump(messages, f'{DATA_DIR}/{chat_id}-st_messages')
    joblib.dump(gemini_history, f'{DATA_DIR}/{chat_id}-gemini_messages')

def load_chat_history(chat_id):
    try:
        messages = joblib.load(f'{DATA_DIR}/{chat_id}-st_messages')
        gemini_history = joblib.load(f'{DATA_DIR}/{chat_id}-gemini_messages')
    except FileNotFoundError:
        messages = []
        gemini_history = []
    return messages, gemini_history

async def get_data(src, msg, target, srv_id):
    url = 'https://dhruva-api.bhashini.gov.in/services/inference/pipeline'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'sTDAW0anybv8208p1Orv-VtSWgGjBXl1qmJbNErLpFtPNdt4cMMzAl127bu7lhsO'
    }
    payload = {
        "inputData": {
            "input": [
                {
                    "source": msg
                }
            ]
        },
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": src,
                        "targetLanguage": target
                    },
                    "serviceId": srv_id
                }
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

# Pre-prompt for legal context
PRE_PROMPT = """
You are an AI assistant specialized in law and legal rules, representing Nyayved. You know every legal thing to handle situations and can give easy explanations of hard legal jargons. You will only reply to legal-related questions such as legal advice, legal definitions, or legal procedures. If a question is not related to law and legal matters, you will respond with: "This question is not related to law and legal matters, so I can't answer it."
If someone greets you with "hi", "hello", or any other greeting, or if they ask about you, respond with: "Hello! I am a chatbot from Nyayved, here to assist you with legal knowledge and solutions to your queries and problems. How can I help you today?"
If someone ask you to what this project about, respond with: "Nyayved is a chatbot that provides legal advice, legal definitions, and legal procedures. It is designed to assist you with legal knowledge and solutions to your queries and problems."
"""

# Endpoints

@app.get("/")
async def welcome():
    return {"message": "Welcome to the Nyayved Chatbot API. Please use the /new_chat/ endpoint to start a new chat."}

@app.post("/new_chat/")
async def new_chat():
    chat_id = str(time.time())
    chat_title = "New Chat"
    past_chats[chat_id] = {"title": chat_title, "first_message_received": False}
    joblib.dump(past_chats, f'{DATA_DIR}/past_chats_list')
    return {"chat_id": chat_id, "chat_title": chat_title}

@app.post("/send_message/")
async def send_message(request: SendMessageRequest):
    chat_id = request.chat_id
    user_message = request.user_message
    
    if chat_id not in past_chats:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages, gemini_history = load_chat_history(chat_id)
    
    # Add user message to chat history
    messages.append({"role": "user", "content": user_message})

    # Update chat title if it's the first message
    if not past_chats[chat_id]["first_message_received"]:
        past_chats[chat_id]["title"] = user_message
        past_chats[chat_id]["first_message_received"] = True
        joblib.dump(past_chats, f'{DATA_DIR}/past_chats_list')

    # Initialize the generative model and chat
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=gemini_history)

    # Prepend pre-prompt to user message
    full_message = PRE_PROMPT + "\nUser: " + user_message

    # Send message to AI
    response = chat.send_message(full_message)
    
    # Collect full response
    full_response = ' '.join([chunk.text for chunk in response])

    # Add assistant response to chat history
    messages.append({"role": MODEL_ROLE, "content": full_response, "avatar": '✨'})

    # Update gemini history
    gemini_history = chat.history

    # Save chat history
    save_chat_history(chat_id, messages, gemini_history)

    return {"response": full_response, "messages": messages}

@app.get("/get_chats/")
async def get_chats():
    # Return only the titles
    return {chat_id: chat_data["title"] for chat_id, chat_data in past_chats.items()}

@app.get("/get_chat_history/{chat_id}")
async def get_chat_history(chat_id: str):
    if chat_id not in past_chats:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages, _ = load_chat_history(chat_id)
    return {"chat_title": past_chats[chat_id]["title"], "messages": messages}

@app.post("/scaler/translate")
async def translate_text(request: TranslationRequest):
    src = request.source_language
    content = request.content
    target = request.target_language
    service_id = "ai4bharat/indictrans-v2-all-gpu--t4"

    if len(src) != 2 or len(target) != 2:
        raise HTTPException(status_code=400, detail="Invalid Language Codes")

    try:
        data = await get_data(src, content, target, service_id)
        return {
            "status_code": 200,
            "message": "success",
            "translated_content": data['pipelineResponse'][0]['output'][0]['target']
        }
    except Exception as e:
        error_message = str(e) if e else "Unknown error"
        raise HTTPException(status_code=500, detail=error_message)

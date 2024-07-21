### Judgment Delivery Enhancement
Build a system that assists judges in drafting judgments, translating legal jargon into layman’s terms, and disseminating judgments in multiple languages for broader accessibility. Design a solution that ensures the clarity and legal integrity of judgments while making them comprehensible to the public.

https://www.bhashabandhu.com/

# NyayVed

1. **Interactive AI Chat Sessions**: Users can engage in interactive chat sessions with an AI model, allowing them to ask questions about legal matters and receive clear, understandable responses. The AI is designed to only answer questions related to law and legal issues, ensuring relevance and accuracy.

2. **Memory Update and Chat History**: The system includes the ability to update the AI's memory, enhancing its responses over time. Additionally, it saves chat histories, enabling users to review past interactions and maintain continuity in their inquiries.

3. **Translation to Local Languages**: The web app provides translations of the AI responses into any local language of India, making legal information accessible to non-native speakers and those in rural areas.

By integrating these features, our solution aims to bridge the communication gap in the legal system, making justice more accessible and understandable to everyone, regardless of their educational or linguistic background. This approach ensures that legal information is both clear and legally accurate, facilitating better understanding and empowerment for individuals across diverse communities.

Frontend Deployed at : https://nyayved.vercel.app

Backend Deployed at : https://server-fast-api.onrender.com

# Techstacks

**Frontend**: Vite + React

**Backend**: FastAPI (Python)

**APIs**: Gemini and Bhashini

# Installation Guide

```bash
git clone https://github.com/deepraj21/bhashabandhu-hackathon
```

```bash
cd bhashabandhu-hackathon
```
Open Two Terminals
```bash
## 1st Terminal for Server
cd server

## Craete a .env file with your geminiAPI
GOOGLE_API_KEY=Your_API_key

## create virtual environment
python -m venv venv

## Activate virtual environment
./venv/Scripts/activate

## Install Dependencies
pip install -r requirements.txt

## Run the server FASTAPI
uvicorn main:app --reload
```
```bash
## 2nd Terminal for Client
cd client

## Install Dependencies
npm install

## Run the viteApp
npm run dev
```


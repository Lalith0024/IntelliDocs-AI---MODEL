import os
import json
from groq import Groq
from app.core.config import settings

def get_client():
    if settings.GROQ_API_KEY:
        return ("groq", Groq(api_key=settings.GROQ_API_KEY))
    elif settings.OPENAI_API_KEY:
        from openai import OpenAI
        return ("openai", OpenAI(api_key=settings.OPENAI_API_KEY))
    else:
        return (None, None)

def generate_answer(question: str, docs: list[dict], user_name: str = "Friend", intent: str = "query") -> str:
    provider, client = get_client()
    if not client: return "Configure API Key."

    persona_prompts = {
        "summary": "You are the 'Intellidocs Summary Specialist'. Provide a structured bulleted summary.",
        "audit": "Identify gaps in the document.",
        "timeline": "Create a chronological timeline of events.",
        "query": "Answer accurately. If explaining, do NOT generate flashcards. Ask: 'Would you like some flashcards?' instead."
    }

    base_persona = persona_prompts.get(intent, persona_prompts["query"])
    context = "\n\n".join([f"DOC: {d['filename']}\nCHUNK: {d['content']}" for d in docs]) if docs else ""
    guardrail = "\nIF_NO_CONTEXT: politely refuse to answer." if not docs else ""

    prompt = f"System: {base_persona}\nContext:\n{context}{guardrail}\n\nQuery: {question}"

    try:
        model_name = "llama-3.1-8b-instant" if provider == "groq" else "gpt-3.5-turbo"
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {str(e)[:50]}"

def generate_dynamic_suggestions(question: str, context_answer: str) -> list[str]:
    provider, client = get_client()
    if not client: return ["Tell me more", "Summarize", "Key takeaways"]
    
    prompt = f"Generate 3 follow-up questions for: '{question}'. Return ONLY a JSON array."
    try:
        model_name = "llama-3.1-8b-instant" if provider == "groq" else "gpt-3.5-turbo"
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)[:3]
    except:
        return ["Tell me more", "What next?", "Explain further"]

async def generate_answer_stream(question: str, docs: list[dict], user_name: str = "Friend", intent: str = "query"):
    provider, client = get_client()
    if not client: 
        yield "data: [ERROR] Configure Your API Keys\n\n"
        return

    persona_prompts = {
        "summary": "Summarize in 3-5 bullet points. Use ```summary block.",
        "audit": "Audit for gaps. Use ```insight block.",
        "timeline": "Format inside an ```insight block.",
        "quiz": "Return STRICTLY JSON inside ```quiz block.",
        "query": "Answer using Markdown. \nSTRICT NEGATIVE CONSTRAINT: NEVER use 'Front:' or 'Back:' labels in your response. NEVER. If you use flashcards, ONLY use the ```flashcard block. \nIF EXPLAINING: Provide explanation then ask: 'Would you like some flashcards for this?'. \nIF COMPANY QUERY: Use a ```chart block for revenue/growth. \nOnly generate the ```flashcard block if the user says 'yes' or asks for it directly."
    }

    base_persona = persona_prompts.get(intent, persona_prompts["query"])
    context = "\n\n".join([f"SOURCE: {d['filename']}\nCONTENT: {d['content']}" for d in docs]) if docs else ""
    guardrail = "\nIF_NO_CONTEXT: Say exactly: 'I don't have enough context...'" if not docs else ""

    prompt = f"System: {base_persona}\nContext: {context}{guardrail}\nQuestion: {question}"

    try:
        model_name = "llama-3.1-8b-instant" if provider == "groq" else "gpt-4"
        
        stream = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500,
            stream=True,
        )
        
        for chunk in stream:
            content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
            if content:
                yield f"data: {json.dumps({'content': content})}\n\n"
        
        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)[:100]})}\n\n"

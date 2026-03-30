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
    """
    Standard Generation Hub (Synchronous Fallback)
    """
    provider, client = get_client()
    if not client: return "Configure API Key."

    persona_prompts = {
        "summary": "You are the 'Intellidocs Summary Specialist'. Provide a structured bulleted summary of the context.",
        "audit": "You are the 'Intellidocs Logic Auditor'. Find GAPS, unaddressed risks, and MISSING info in the documents.",
        "timeline": "You are the 'Intellidocs Chronology Specialist'. Create a strict chronological timeline of events.",
        "query": "You are the 'Intellidocs Intelligence Assistant'. Answer direct questions with sophisticated sophisticated RAG context."
    }

    base_persona = persona_prompts.get(intent, persona_prompts["query"])
    context = "\n\n".join([f"DOC: {d['filename']}\nCHUNK: {d['content']}" for d in docs]) if docs else "No docs found."

    prompt = f"{base_persona}\n\nUSER_NAME: {user_name}\nREPLY_DIRECTLY: Yes\nCITE_SOURCES: Mandatory\n\nCONTEXT:\n{context}\n\nQUERY: {question}"

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
    if not client: return ["Tell me more about this", "What are the key takeaways?", "Can you summarize?"]
    
    prompt = f"Based on the user's question: '{question}' and the AI output snippet: '{context_answer[-500:]}', generate exactly 3 short, distinct, high-quality follow-up questions the user could ask next to dive deeper. Return ONLY a JSON array of 3 strings. Example: [\"question 1\", \"question 2\", \"question 3\"]"
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
        arr = json.loads(content)
        if isinstance(arr, list) and len(arr) >= 3:
            return arr[:3]
    except Exception as e:
        pass
    
    return ["Tell me more about this", "What are the key takeaways?", "Can you explain this simply?"]

async def generate_answer_stream(question: str, docs: list[dict], user_name: str = "Friend", intent: str = "query"):
    """
    Production-Grade 'Neural Stream' Generator:
    This yields word-by-word chunks to the frontend for zero-friction interaction.
    """
    provider, client = get_client()
    if not client: 
        yield "data: [ERROR] Configure Your API Keys in .env\n\n"
        return

    persona_prompts = {
        "summary": "Summarize the context in 3-5 high-impact bullet points. Be direct.",
        "audit": "Audit the context for gaps, risks, or missing data. Use bullet points.",
        "timeline": "Extract all dates and events into a chronological list.",
        "query": "Answer the query based on the context. Cite the filename at the end."
    }

    base_persona = persona_prompts.get(intent, persona_prompts["query"])
    context = "\n\n".join([f"SOURCE: {d['filename']}\nCONTENT: {d['content']}" for d in docs]) if docs else ""

    prompt = f"Persona: {base_persona}\nUser: {user_name}\nContext: {context}\nQuestion: {question}"

    try:
        model_name = "llama-3.1-8b-instant" if provider == "groq" else "gpt-3.5-turbo"
        
        # Async-capable stream call
        stream = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1200,
            stream=True,
        )
        
        for chunk in stream:
            content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
            if content:
                # We yield in SSE (Server-Sent Events) compatible format
                yield f"data: {json.dumps({'content': content})}\n\n"
        
        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)[:100]})}\n\n"

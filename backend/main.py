import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from supabase import create_client, Client

app = FastAPI(title="Generador de Contenido SaaS")

# Conexión al motor gratuito de Groq
groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class GenerateRequest(BaseModel):
    email: str
    prompt: str

@app.get("/")
def home():
    return {"message": "Backend activo con Groq"}

@app.post("/api/v1/generar")
def generar_contenido(req: GenerateRequest):
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio.")

    # 1. Consulta de usuario en Supabase
    res = supabase.table("profiles").select("*").eq("email", email).execute()
    user_data = res.data

    if isinstance(user_data, str):
        try: user_data = json.loads(user_data)
        except Exception: user_data = []

    # 2. Asignación inicial de 3 créditos
    if not user_data:
        new_user = {"email": email, "credits": 3}
        supabase.table("profiles").insert(new_user).execute()
        credits_left = 3
    else:
        row = user_data[0] if isinstance(user_data, list) and len(user_data) > 0 else user_data
        credits_left = row.get("credits", 3) if isinstance(row, dict) else 3

    # 3. Control de saldo
    if credits_left <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Has agotado tus 3 créditos gratuitos. Haz clic en 'Comprar más créditos' para continuar."
        )

    # 4. Generación optimizada con Llama 3.1
    system_prompt = (
        "Eres un Copywriter profesional y estratega de contenido viral. "
        "Escribe respuestas con ganchos (hooks) atractivos, estructura clara, "
        "emojis estratégicos y llamados a la acción efectivos."
    )

    try:
        response = openai_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.prompt}
            ],
            max_tokens=600
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA: {str(e)}")

    # 5. Descuento de crédito
    new_credits = credits_left - 1
    supabase.table("profiles").update({"credits": new_credits}).eq("email", email).execute()

    return {
        "result": generated_text,
        "credits_left": new_credits
    }

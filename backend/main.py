import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from supabase import create_client, Client

app = FastAPI(title="Generador de Contenido SaaS")

groq_key = os.getenv("GROQ_API_KEY")

# Forzar la URL base del servidor de Groq
openai_client = OpenAI(
    api_key=groq_key or "missing_key",
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
    if not groq_key or "gsk_" not in groq_key:
        raise HTTPException(
            status_code=500, 
            detail="Falta configurar la variable GROQ_API_KEY correctamente en el panel de Render."
        )

    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio.")

    # 1. Consulta en Supabase
    res = supabase.table("profiles").select("*").eq("email", email).execute()
    user_data = res.data

    if isinstance(user_data, str):
        try: user_data = json.loads(user_data)
        except Exception: user_data = []

    # 2. Control de créditos
    if not user_data:
        new_user = {"email": email, "credits": 3}
        supabase.table("profiles").insert(new_user).execute()
        credits_left = 3
    else:
        row = user_data[0] if isinstance(user_data, list) and len(user_data) > 0 else user_data
        credits_left = row.get("credits", 3) if isinstance(row, dict) else 3

    if credits_left <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Has agotado tus 3 créditos gratuitos. Haz clic en 'Comprar más créditos' para continuar."
        )

    # 3. Llamada al modelo Llama 3.3 en Groq
    try:
        response = openai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un Copywriter profesional y estratega de contenido viral."},
                {"role": "user", "content": req.prompt}
            ],
            max_tokens=600
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA: {str(e)}")

    # 4. Descontar crédito
    new_credits = credits_left - 1
    supabase.table("profiles").update({"credits": new_credits}).eq("email", email).execute()

    return {
        "result": generated_text,
        "credits_left": new_credits
    }

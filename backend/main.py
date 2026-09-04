import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client

app = FastAPI(title="Generador de Contenido SaaS")

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
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or not groq_key.startswith("gsk_"):
        raise HTTPException(
            status_code=500, 
            detail="Error: La variable GROQ_API_KEY no está configurada correctamente en Render."
        )

    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio.")

    # 1. Consulta en Supabase
    res = supabase.table("profiles").select("*").eq("email", email).execute()
    user_data = res.data

    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)
        except Exception:
            user_data = []

    # 2. Verificar o inicializar usuario
    if not user_data:
        credits_left = 3
    else:
        row = user_data[0] if isinstance(user_data, list) and len(user_data) > 0 else user_data
        credits_left = row.get("credits", 3) if isinstance(row, dict) else 3

    # 3. Validar créditos disponibles
    if credits_left <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Has agotado tus 3 créditos gratuitos. Haz clic en 'Comprar más créditos' para continuar."
        )

    # 4. Generar respuesta con Groq
    try:
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Copywriter experto y estratega de contenido viral para redes sociales."
                },
                {"role": "user", "content": req.prompt}
            ],
            max_tokens=1000
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA de Groq: {str(e)}")

    # 5. Restar crédito y guardar usando upsert
    new_credits = credits_left - 1
    supabase.table("profiles").upsert({"email": email, "credits": new_credits}).execute()

    return {
        "result": generated_text,
        "credits_left": new_credits
    }

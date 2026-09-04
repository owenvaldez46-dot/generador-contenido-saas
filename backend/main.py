import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client

app = FastAPI(title="Generador de Contenido SaaS")

# Configuración de Supabase
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
            detail="Error: La variable GROQ_API_KEY no está configurada o no empieza por 'gsk_' en Render."
        )

    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio.")

    # 1. Consulta en Supabase para obtener el usuario
    res = supabase.table("profiles").select("*").eq("email", email).execute()
    user_data = res.data

    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)
        except Exception:
            user_data = []

    # 2. Control y creación de créditos de usuario
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
            detail="Has agotado tus créditos gratuitos. Haz clic en 'Comprar más créditos' para continuar."
        )

    # 3. Llamada al mejor modelo de Groq (openai/gpt-oss-120b)
    try:
        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Eres un Copywriter experto y estratega de contenido viral para redes sociales "
                        "(YouTube Shorts, TikTok, Instagram Reels). Tus guiones deben ser altamente adictivos, "
                        "con un gancho potente en los primeros 3 segundos, desarrollo dinámico y una llamada "
                        "a la acción directa."
                    )
                },
                {"role": "user", "content": req.prompt}
            ],
            max_tokens=1000
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA de Groq: {str(e)}")

    # 4. Descontar crédito en Supabase
    new_credits = credits_left - 1
    supabase.table("profiles").update({"credits": new_credits}).eq("email", email).execute()

    return {
        "result": generated_text,
        "credits_left": new_credits
    }

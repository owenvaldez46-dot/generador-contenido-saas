import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client

app = FastAPI(title="Generador de Contenido SaaS")

supabase_url = os.getenv("SUPABASE_URL", "").strip()
supabase_key = os.getenv("SUPABASE_KEY", "").strip()
supabase: Client = create_client(supabase_url, supabase_key)

class GenerateRequest(BaseModel):
    email: str
    prompt: str

@app.get("/")
def home():
    return {"message": "Backend activo con Groq y Supabase"}

@app.post("/api/v1/generar")
def generar_contenido(req: GenerateRequest):
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key or not groq_key.startswith("gsk_"):
        raise HTTPException(
            status_code=500, 
            detail="Error: GROQ_API_KEY no está configurada correctamente en Render."
        )

    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio.")

    # 1. Consultar correo en Supabase
    try:
        res = supabase.table("profiles").select("*").eq("email", email).execute()
        user_data = res.data
    except Exception as db_err:
        raise HTTPException(status_code=500, detail=f"Error consultando la base de datos: {str(db_err)}")

    # 2. Determinar créditos del usuario
    if not user_data or len(user_data) == 0:
        credits_left = 3
        is_new_user = True
    else:
        row = user_data[0] if isinstance(user_data, list) else user_data
        credits_left = int(row.get("credits", 0)) if isinstance(row, dict) else 0
        is_new_user = False

    # 3. Validar si tiene créditos disponibles
    if credits_left <= 0:
        raise HTTPException(
            status_code=400, 
            detail=f"El correo '{email}' ha agotado sus 3 créditos gratuitos. Haz clic en 'Comprar más créditos' para continuar."
        )

    # 4. Generar contenido con IA
    try:
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "Eres un Copywriter experto y estratega de contenido viral."},
                {"role": "user", "content": req.prompt}
            ],
            max_tokens=1000
        )
        generated_text = response.choices[0].message.content
    except Exception as groq_err:
        raise HTTPException(status_code=500, detail=f"Error en la IA de Groq: {str(groq_err)}")

    # 5. Guardar descuento de crédito en Supabase
    new_credits = credits_left - 1
    try:
        if is_new_user:
            supabase.table("profiles").insert({"email": email, "credits": new_credits}).execute()
        else:
            supabase.table("profiles").update({"credits": new_credits}).eq("email", email).execute()
    except Exception as save_err:
        raise HTTPException(status_code=500, detail=f"Error al guardar crédito en Supabase: {str(save_err)}")

    return {
        "result": generated_text,
        "credits_left": new_credits,
        "email": email
    }

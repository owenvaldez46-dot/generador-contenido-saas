import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client

app = FastAPI(title="Generador de Contenido SaaS")

# Cargar y limpiar variables de entorno
supabase_url = os.getenv("SUPABASE_URL", "").strip()
supabase_key = os.getenv("SUPABASE_KEY", "").strip()

if not supabase_url or not supabase_key:
    print("ALERTA: SUPABASE_URL o SUPABASE_KEY no están configuradas correctamente.")

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
            detail="Error: GROQ_API_KEY no está configurada o no empieza con 'gsk_' en Render."
        )

    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio.")

    # 1. Consultar usuario en Supabase
    try:
        res = supabase.table("profiles").select("*").eq("email", email).execute()
        user_data = res.data
    except Exception as db_read_err:
        raise HTTPException(
            status_code=500,
            detail=f"Error al leer base de datos: {str(db_read_err)}"
        )

    # 2. Verificar créditos
    if not user_data or len(user_data) == 0:
        credits_left = 3
        is_new_user = True
    else:
        row = user_data[0] if isinstance(user_data, list) else user_data
        credits_left = row.get("credits", 0) if isinstance(row, dict) else 0
        is_new_user = False

    if credits_left <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Has agotado tus 3 créditos gratuitos. Haz clic en 'Comprar más créditos' para continuar."
        )

    # 3. Generar contenido con Groq
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

    # 4. Guardar créditos actualizados (Insert / Update explícito)
    new_credits = credits_left - 1

    try:
        if is_new_user:
            save_res = supabase.table("profiles").insert({"email": email, "credits": new_credits}).execute()
        else:
            save_res = supabase.table("profiles").update({"credits": new_credits}).eq("email", email).execute()

        # Verificar si la base de datos realmente guardó la fila
        if not save_res.data:
            raise Exception("La base de datos aceptó el comando pero devolvió 0 filas modificadas.")

    except Exception as db_write_err:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar crédito en Supabase: {str(db_write_err)}"
        )

    return {
        "result": generated_text,
        "credits_left": new_credits
    }

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
from PyPDF2 import PdfReader
import subprocess

# Configuration des templates
templates = Jinja2Templates(directory="../frontend/templates")

# Créer un APIRouter
router = APIRouter()

# Fonction pour extraire le texte d'un PDF
def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        content = "".join([page.extract_text() + "\n" for page in reader.pages])
        return content
    except Exception as e:
        return ""

# Fonction pour diviser le texte en sections
def split_into_chunks_dynamic(text):
    chunks = {}
    current_chunk = "Section 1"
    chunks[current_chunk] = ""

    lines = text.split("\n")
    section_index = 1

    for line in lines:
        line = line.strip()
        if not line:
            section_index += 1
            current_chunk = f"Section {section_index}"
            chunks[current_chunk] = ""
        else:
            chunks[current_chunk] += line + " "

    for section in chunks:
        chunks[section] = chunks[section].strip()

    return chunks

# Fonction pour structurer les informations extraites
def extract_info_from_text(text):
    chunks = split_into_chunks_dynamic(text)
    return {"sections": [{"title": section, "content": content} for section, content in chunks.items()]}

# Route pour afficher la page de génération de lettre
@router.get("/generate_letter", response_class=HTMLResponse)
async def generate_letter_page(request: Request):
    """
    Affiche la page de génération de lettre.
    """
    return templates.TemplateResponse("generate_letter.html", {"request": request, "extracted_data": None, "generated_letter": None})

# Route pour extraire les informations d'un fichier PDF
@router.post("/extract_pdf_text", response_class=HTMLResponse)
async def extract_pdf_text(request: Request, file: UploadFile = File(...)):
    """
    Extrait le texte d'un fichier PDF et affiche les sections sur la même page.
    """
    temp_file = f"temp_{file.filename}"
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")
        # Sauvegarder le fichier temporairement
        with open(temp_file, "wb") as f:
            f.write(await file.read())

        # Extraire le texte
        text = extract_text_from_pdf(temp_file)
        if not text.strip():
            raise HTTPException(status_code=500, detail="Impossible d'extraire le contenu du fichier PDF.")
        
        # Structurer les informations
        info = extract_info_from_text(text)

        # Retourner les sections extraites pour les afficher
        return templates.TemplateResponse("generate_letter.html", {
            "request": request,
            "extracted_data": info["sections"],
            "generated_letter": None
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Modèle pour la génération de lettre
class ChatRequest(BaseModel):
    user_message: str

# Route pour générer une lettre de motivation
@router.post("/generate_letter", response_class=HTMLResponse)
async def generate_letter(request: Request, user_message: str = Form(...)):
    """
    Gère la génération de lettre de motivation.
    """
    try:
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="Le message utilisateur est vide.")

        # Prompt pour le modèle de génération
        prompt = f"""
        Vous êtes un assistant conversationnel. L'utilisateur fournit des informations personnelles et professionnelles.
        Vous devez rédiger une lettre de motivation basée sur les informations suivantes :
        
        {user_message}
        """
        # Appel au modèle de génération de texte (Ollama ou autre)
        result = subprocess.run(
            ["ollama", "run", "llama3.2:latest"],
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Ollama Error: {result.stderr}")

        # Résultat généré
        response_text = result.stdout.strip()

        # Retourner la lettre générée pour l'afficher
        return templates.TemplateResponse("generate_letter.html", {
            "request": request,
            "extracted_data": None,
            "generated_letter": response_text
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération de la lettre : {str(e)}")

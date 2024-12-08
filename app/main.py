import json
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from werkzeug.security import generate_password_hash
import os
from fastapi.staticfiles import StaticFiles
# Importation des routers
from routers import users
from routers.matching import router as matching_router

# Connexion à la base de données
from database.connection import get_snowflake_connection
from database.queries import get_user_by_email, insert_user

# Création de l'application FastAPI
app = FastAPI()

# Configuration des fichiers statiques et des templates

app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "../frontend/public")), name="static")


templates = Jinja2Templates(directory="../frontend/templates")

# Inclusion des routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(matching_router, prefix="/api", tags=["matching"])

# Nouvelle interface : Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    owners = [
        {"name": "Hibatallah Samy", "image": "/static/image/owner1.jpg", "role": "développeuse en web et IA"},
        {"name": "Marouane Bouhouch", "image": "/static/image/owner2.jpg", "role": "développeur en web et IA"},
        {"name": "Rania Chibane", "image": "/static/image/owner3.jpg", "role": "développeuse en web et IA"},
        {"name": "Jad Ghetreff", "image": "/static/image/owner4.jpg", "role": "développeur en web et IA"},
    ]
    return templates.TemplateResponse("index.html", {"request": request, "owners": owners})

# Nouvelle interface : Page d'inscription (GET)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Nouvelle interface : Page d'inscription (POST)
@app.post("/register")
async def register_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form("candidat")
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match!")
    # Hash du mot de passe pour la sécurité
    password_hash = generate_password_hash(password)
    try:
        # Insérer l'utilisateur dans la base de données
        insert_user(f"{first_name} {last_name}", email, password_hash, role)
        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

# Nouvelle interface : Page de connexion (GET)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Nouvelle interface : Page de connexion (POST)
@app.post("/login")
async def login_user(email: str = Form(...), password: str = Form(...)):
    user = get_user_by_email(email)
    if user:
        redirect_url = "/dashbord"
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="user", value=json.dumps(user), httponly=True)
        return response
    else:
        return {"error": "Invalid credentials"}

# Nouvelle interface : Tableau de bord
@app.get("/dashbord", response_class=HTMLResponse)
async def dashbord_page(request: Request):
    user_cookie = request.cookies.get("user")
    user = json.loads(user_cookie) if user_cookie else None
    return templates.TemplateResponse("dashbord.html", {"request": request, "user": user})

# Route pour le logout
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="user")  # Supprimer le cookie utilisateur
    return response

# Route pour afficher la page de génération de lettre
@app.get("/generate_letter", response_class=HTMLResponse)
async def generate_letter_page(request: Request):
    return templates.TemplateResponse("generate_letter.html", {"request": request})

# Route pour traiter la génération de lettre
@app.post("/generate_letter")
async def handle_generate_letter(user_message: str = Form(...)):
    if not user_message.strip():
        raise HTTPException(status_code=400, detail="Le message utilisateur est vide.")
    # Ajoutez votre logique pour générer la lettre ici
    response_text = f"Lettre générée avec succès pour le message : {user_message}"
    return {"message": "Lettre générée avec succès", "response": response_text}


from ollama._client import Client

client = Client()

def test_ollama():
    response = client.generate("llama3.2:latest", "Hello, how are you?")
    print(response)

# Appel du test avant de lancer l'application
test_ollama()

# Lancement de l'application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)








# Connexion à Snowflake
try:
    conn = get_snowflake_connection()
    print("Connexion à Snowflake réussie !")
    conn.close()
except Exception as e:
    print(f"Erreur lors de la connexion à Snowflake : {e}")

# Point d'entrée de l'application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="localhost", port=8000)

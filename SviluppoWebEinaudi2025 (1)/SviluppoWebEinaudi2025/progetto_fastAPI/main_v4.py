from typing import Dict
from fastapi import Form, FastAPI, Response, HTTPException, status, Request
from fastapi import Depends
from schema import User, UserCreate
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi_login import LoginManager
from datetime import timedelta
import os
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector  # Importo il connettore MySQL

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
SECRET = os.urandom(24).hex()
manager = LoginManager(SECRET, '/login', use_cookie=True, default_expiry=timedelta(minutes=20))

# Configurazione della connessione al DB (Modifica i dati in base al tuo DB)
db_config = {
    'host': 'sql7.freesqldatabase.com',         # Indirizzo del tuo DB
    'user': 'sql7765718',        # Nome utente del DB
    'password': 'aKDVVF7wAK',  # Password del DB
    'database': 'sql7765718', # Nome del DB
}

# Funzione per connettersi al DB
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@manager.user_loader()
def load_user(user: str):
    # Connessione al DB per caricare l'utente
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM utenti WHERE nome_utente = %s", (user,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data
@app.post("/login_API")
def login(user: User, response: Response):
    name = user.username
    password = user.password
    user = load_user(name)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=name))
    manager.set_cookie(response, access_token)
    return "ok"

@app.post("/reg")
def register(user: UserCreate):
    if user.password != user.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Errore le due password non coincidono")
    
    # Verifica se l'username è già registrato
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM utenti WHERE username = %s", (user.username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Errore username occupato")
    
    # Registrazione dell'utente
    cursor.execute("INSERT INTO utenti (username, password) VALUES (%s, %s)", (user.username, user.password))
    conn.commit()
    conn.close()
    
    return {"message": "registrazione avvenuta con successo"}

@app.get("/info_protetta")
def profilo_utente(saluto: str, user=Depends(manager)):
    return saluto + " " + user["username"]

@app.get("/primo_ingresso")
def primo_ingr():
    return "ciao Benvenuto"

@app.get("/pagina_html", response_class=HTMLResponse)
def pagina_html():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Benvenuto</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    color: #333;
                    text-align: center;
                    padding: 20px;
                }
                h1 {
                    color: #4CAF50;
                }
                a {
                    text-decoration: none;
                    color: #4CAF50;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <h1>Benvenuto nella mia applicazione FastAPI!</h1>
            <p>Questa è una semplice pagina HTML restituita da un endpoint FastAPI.</p>
            <a href="/primo_ingresso">Vai all'endpoint /primo_ingresso</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/")
def login_page(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    return response

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": "", "titolo": "Homepage"})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Verifica nel DB se l'utente esiste
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM utenti WHERE nome_utente = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user["password"] == password:
        response = RedirectResponse(url="/dashboard", status_code=303)
        return response

    return templates.TemplateResponse("login.html", {"request": request, "message": "Credenziali errate!"})
    
@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

from typing import Dict
from fastapi import Form,FastAPI, Response, HTTPException, status, Request
from fastapi import Depends
from schema import User, UserCreate
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi_login import LoginManager
from datetime import timedelta
import os
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") 
templates = Jinja2Templates(directory="templates")
SECRET = os.urandom(24).hex()
manager = LoginManager(SECRET, '/login', use_cookie=True, default_expiry = timedelta(minutes=20))

# fake database
fake_db = {"nome.cognome" : {"username": "nome.cognome", 'password': 'password_prova'}}


@manager.user_loader()
def load_user(user: str):
    return fake_db.get(user)

@app.post("/login_API")
def login(user: User, response: Response):
    name = user.username
    password = user.password
    user = load_user(name)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=name)
    )
    manager.set_cookie(response, access_token)
    return "ok"

@app.post("/reg")
def register(user: UserCreate):
    if user.password != user.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Errore le due password non coincidono")
    if user.username in fake_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Errore username occupato")
    
    fake_db[user.username] = {"username": user.username, "password": user.password}
    return {"message": "registrazione avvenuta con successo"}



@app.get("/info_protetta")
def profilo_utente(saluto : str , user = Depends(manager)):
	return saluto + " " + user["username"]



@app.get("/primo_ingresso")
def primo_ingr():
    return "ciao Benvenuto"


@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": "","titolo": "Homepage"})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in fake_db:
        credenziali = fake_db[username]
        if credenziali["username"] == username and credenziali["password"] == password:
            response = RedirectResponse(url="/dashboard", status_code=303)
            return response

    return templates.TemplateResponse("login.html", {"request": request, "message": "Credenziali errate!"})


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
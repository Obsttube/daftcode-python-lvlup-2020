from typing import Dict
from hashlib import sha256
from fastapi import FastAPI, Request, Response, status, Cookie, HTTPException, Query, Body, Form, Depends
from starlette.responses import RedirectResponse
from pydantic import BaseModel

# for debug
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
# end

from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import secrets

app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")
app.secret_key = "wUYwdjICbQP70WgUpRajUwxnGChAKmRtfQgYASazava4p5In7pZpFPggdB4JDjlv"
app.patients={}#{"id_1": {"name": "IMIE", "surname": "NAZWISKO"}, "id_2": {"name": "IMIE", "surname": "NAZWISKO"}}
app.next_patient_id=0
app.users={"trudnY":"PaC13Nt"}
app.sessions={}

# for debug
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(jsonable_encoder({"detail": exc.errors(), "body": exc.body}))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
# end

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

def check_cookie(session_token: str = Cookie(None)):
    print(session_token)
    print(app.sessions)
    if session_token not in app.sessions:
        session_token = None
    return session_token

@app.get("/welcome")
def welcome(request: Request, response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Log in to access this page."
    username = app.sessions[session_token]
    return templates.TemplateResponse("welcome.html", {"request": request, "user": username})

def login_check_cred(credentials: HTTPBasicCredentials = Depends(security)):
    correct = False
    for username, password in app.users.items():
        correct_username = secrets.compare_digest(credentials.username, username)
        correct_password = secrets.compare_digest(credentials.password, password)
        if (correct_username and correct_password):
            correct = True
    if not correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
    app.sessions[session_token]=credentials.username
    return session_token


@app.get("/login") # for easier testing in the browser
@app.post("/login")
def login(response: Response, session_token: str = Depends(login_check_cred)):
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/welcome"
    response.set_cookie(key="session_token", value=session_token)

@app.get("/logout") # for easier testing in the browser
@app.post("/logout")
def logout(response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Log in to access this page."
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/"
    app.sessions.pop(session_token)

@app.get("/method")
@app.post("/method")
@app.put("/method")
@app.delete("/method")
def get_method(request: Request):
    return {"method": str(request.method)}

class PatientRq(BaseModel):
    name: str
    surname: str

@app.post("/patient")
def add_patient(response: Response, rq: PatientRq, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Log in to access this page."
    pid=f"id_{app.next_patient_id}"
    app.patients[pid]=rq.dict()
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{pid}"
    app.next_patient_id+=1
    print(app.patients)

@app.get("/patient")
def get_all_patients(response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Log in to access this page."
    print(app.patients)
    return app.patients

@app.get("/patient/{pid}")
def get_patient(pid: str, response: Response, status_code=status.HTTP_200_OK, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Log in to access this page."
    print(pid)
    if pid in app.patients:
        print(app.patients[pid])
        return app.patients[pid]
    response.status_code = status.HTTP_204_NO_CONTENT

@app.delete("/patient/{pid}")
def remove_patient(pid: str, response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Log in to access this page."
    print(app.patients)
    app.patients.pop(pid, None)
    print(app.patients)
from typing import Dict
from hashlib import sha256
from fastapi import FastAPI, Request, Response, status, Cookie, HTTPException, Query
from starlette.responses import RedirectResponse
from pydantic import BaseModel


app = FastAPI()
app.secret_key = "wUYwdjICbQP70WgUpRajUwxnGChAKmRtfQgYASazava4p5In7pZpFPggdB4JDjlv"
app.patients=[]


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/welcome")
def welcome():
    return "Jakiś powitalny tekst!"

@app.post("/login")
def create_cookie(response: Response, login: str = None, password: str = Query(None, alias="pass")):
    if login == "trudnY" and str(password) == "PaC13Nt":
        response.status_code = status.HTTP_302_FOUND
        response.headers["Location"] = "/welcome"
        session_token = sha256(bytes(f"{login}{password}{app.secret_key}", encoding='utf8')).hexdigest()
        response.set_cookie(key="session_token", value=session_token)
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED

@app.get("/method")
@app.post("/method")
@app.put("/method")
@app.delete("/method")
def get_method(request: Request):
    return {"method": str(request.method)}

class PatientRq(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: Dict


@app.post("/patient", response_model=PatientResp)
def receive_patient(rq: PatientRq): 
    app.patients.append(rq.dict())
    return PatientResp(id=len(app.patients)-1, patient=rq.dict())

@app.get("/patient/{pk}")
def get_patient(pk: int, response: Response, status_code=status.HTTP_200_OK):
    if len(app.patients)>pk:
        return app.patients[pk]
    response.status_code = status.HTTP_204_NO_CONTENT
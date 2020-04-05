from typing import Dict

from fastapi import FastAPI, Request

from pydantic import BaseModel


app = FastAPI()
app.num_of_patients=0


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method")
@app.post("/method")
@app.put("/method")
@app.delete("/method")
def get_method(request: Request):
    return {"method": str(request.method)}

class PatientRq(BaseModel):
    name: str
    surname: str


class PatientResp(BaseModel):
    id: int = app.num_of_patients
    patient: dict


@app.post("/patient", response_model=PatientResp)
def receive_patient(rq: PatientRq):
    return PatientResp(patient=rq.dict())





class HelloResp(BaseModel):
    msg: str


@app.get("/hello/{name}", response_model=HelloResp)
def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")
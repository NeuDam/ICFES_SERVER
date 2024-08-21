from fastapi import FastAPI
from pydantic import BaseModel
from icfes import Icfes

app = FastAPI()

class BodyRequest(BaseModel):
	document: int
	born: str
	young: bool

@app.get('/')
async def root():
	return {"status": True, "message": "Server is alive :)"}

@app.post('/consulta')
async def query_icfes(body: BodyRequest):
	response = Icfes(born_date="00/00/2000", young=True, document=123456789).query_test()
	return response
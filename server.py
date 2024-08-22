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
	response = Icfes(born_date=body.born, young=body.young, document=body.document).query_test()
	return response

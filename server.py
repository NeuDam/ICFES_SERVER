from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from icfes import Icfes

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://icfes-consultas.vercel.app"],  # Permitir todas las fuentes, puedes restringir esto a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from icfes import Icfes
import os

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://icfes-consultas.vercel.app"],  # Permitir todas las fuentes, puedes restringir esto a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Lista para almacenar los correos electrónicos
email_list: List[str] = []

# Scheduler para ejecutar la tarea programada
scheduler = BackgroundScheduler()

class BodyRequest(BaseModel):
    document: int
    born: str
    young: bool

class EmailRequest(BaseModel):
    document: int
    born: str
    email: EmailStr

def parse_information(data, document):

    examenes = """
    """

    for examen in data["examenes"]:

        materias_puntaje = """"""

        for materia in examen["puntajeMaterias"]:
            css_class = (
                "background-color: rgba(255, 0, 0, 0.12);" if materia["code"] == "ING" else
                "background-color: rgba(0, 153, 255, 0.12);" if materia["code"] == "MAT" else
                "background-color: rgba(0, 155, 0, 0.12);" if materia["code"] == "CIE" else
                "background-color: rgba(78, 0, 155, 0.12);" if materia["code"] == "LEC" else
                "background-color: rgba(255, 85, 0, 0.12);"
            )

            # Crear el contenido HTML con estilos en línea
            html_content = f"""
            <div style="width: 45%; height: 130px; padding: 10px; border-radius: 8px; position: relative; {css_class}">
                <h5 style="margin: 0; text-align: center; font-size: 1.2em;">
                    {materia['code']}<span style="font-size: .7em !important; margin-left: 5px;">{materia['puntaje']}</span>
                </h5>
                <span style="display: block; width: 100%; text-align: center; position: absolute; bottom: 5px; left: 0;">
                    {materia['nombrePrueba']}
                </span>
            </div>
            """

            materias_puntaje += html_content


        examenes += f"""
            <div style="background-color: #404040eb; padding: 8px; border-radius: 8px; margin-bottom: 20px;">
                  <span style="font-weight: bold; font-size: large; display: block; text-align: center; margin-bottom: 30px; color: white;">
                      {examen['ACREGISTRO']}
                  </span>
                  <article style="display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 10px 20px; border-radius: 10px;">
                    <section style="width: 100%; text-align: center;">
                      <img src="https://static1.moviewebimages.com/wordpress/wp-content/uploads/2022/06/Homelander-in-the-Boys.jpg" alt="" style="width: 150px; height: 150px; object-fit: cover; border-radius: 50%; background-color: #8f4cfc57;" />
                      <h3 style="text-align: center; color: white;">{data['estudiante']}</h3>
                    </section>
                    <section style="width: 100%; text-align: center;">
                      <span style="font-size: 2.5em; font-weight: bold; color: greenyellow;">{examen['puntaje']}</span>
                    </section>
                  </article>
                  <span style="text-align: center; width: 100%; display: block; font-style: italic; color: white; margin-bottom: 40px;">
                      &quot;{examen['mensajeMotivacional']}&quot;
                  </span>
                  <article style="display: flex; justify-content: space-evenly; flex-wrap: wrap; gap: 2em;">
                    {materias_puntaje}
                  </article>
            </div>
        """

    body_html = f"""
        <h2 style="text-align: center; margin-bottom: 60px; color: #fff;">Resultados para {document}</h2>
        <div>
            {examenes}
        </div>
    """

    return """
        <html>
          <head>
          <style>
            @media screen and (min-width: 768px) {
                .container-examen {
                    background-color: #404040eb;
                    padding: 8px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }

                .main-top-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 20px;
                    border-radius: 10px;
                }

                .main-top-header section {
                    width: 50%;
                    text-align: center;
                }

                .main-top-header section span {
                    display: block;
                    text-align: center;
                    font-size: 4em;
                    font-weight: bold;
                    color: greenyellow;
                }

                .card {
                    width: 90%;
                    height: 100px;
                    padding: 10px;
                    border-radius: 8px;
                    position: relative;
                }

                .name-materia {
                    font-size: 1em;
                }

                .main-top-header section span {
                    font-size: 4em;
                }
            }
          </style>
          </head>
          <body style="margin: 0; min-height: 100vh; background-color: #181818; color: white; opacity: 1; background-image: radial-gradient(#8f4cfc57 2px, #181818 2px); background-size: 40px 40px;">
            """ + body_html + """
          </body>
        </html>
    """

@app.get('/')
async def root():
    return {"status": True, "message": "Server is alive :)"}

@app.post('/consulta')
async def query_icfes(body: BodyRequest):
    response = Icfes(born_date=body.born, young=body.young, document=body.document).query_test()
    return response

@app.post('/subscribe')
async def subscribe_email(email_request: EmailRequest):
    email = email_request
    if email.email not in email_list:
        email_list.append(email)
    return {"status": "success", "message": f"Email {email.email} added to the list."}

def send_emails():
    # Configuración del servidor de correo (ejemplo con Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "icfesnotificador@gmail.com"
    smtp_password = os.getenv("gmail_password")

    # Crear el mensaje de correo electrónico
    subject = "Resultado de tu prueba ICFES"

    for email in email_list:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = str(email.email)
        msg['Subject'] = subject

        response = Icfes(born_date=email.born, young=True, document=email.document).query_test()

        my_information = parse_information(response, email.document)

        msg.attach(MIMEText(my_information, 'html'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email.email, msg.as_string())
            server.quit()
            print(f"Correo enviado a {str(email.email)}")
        except Exception as e:
            print(f"Error al enviar correo a {str(email.email)}: {e}")

# Programar la tarea para que se ejecute a las 8:00 AM todos los días
trigger = CronTrigger(hour=15, minute=14)
scheduler.add_job(send_emails, trigger)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

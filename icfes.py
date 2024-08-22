import requests

class Icfes():
    def __init__(self, born_date: str, young: bool, document: int) -> None:
        self.born_date = born_date
        self.young = young
        self.document = document
        self.token = None
        self.name = None
        pass

    def auth_request(self):
        url = "https://resultadosbackendoci.icfes.edu.co/api/segurity/autenticacionResultados"

        post_data = {"tipoDocumento": "TI" if self.young else "CC","numeroDocumento":self.document,"fechaNacimiento":self.born_date,"identificacionUnica":None}

        r = requests.post(url=url, headers={"Content-Type": "application/json"}, json=post_data).json()

        print(r)

        try:
            self.token = r["token"]
        except KeyError:
            return False, {"status": False, "message": "Error en datos ingresados"}

        data = [{"numeroRegistro": test["numeroRegistro"], "examen": test["datosParametros"]["examen"], "periodo": test["datosParametros"]["periodoAnioExamen"]} for test in r["datosAutenticacion"]]

        self.get_name_student(data)
        return True, data
    
    def get_name_student(self, data):
        url = f"https://resultadosbackendoci.icfes.edu.co/api/datos-basicos/datosBasicosRespuesta?examen={data[0]['examen']}&identificacionUnica={data[0]['numeroRegistro']}"
    
        r = requests.get(url=url, headers={"Content-Type": "application/json", "Authorization": self.token}).json()

        self.name = f'{r["nombres"]["primerNombre"]} {r["nombres"]["primerApellido"]} {r["nombres"]["segundoApellido"]}'

    def get_score_student(self, data):
        url = f"https://resultadosbackendoci.icfes.edu.co/api/resultados/datosReporteGeneral?identificacionUnica={data['numeroRegistro']}&examen={data['examen']}&periodoAnioExamen={data['periodo']}"

        r = requests.get(url=url, headers={"Content-Type": "application/json", "Authorization": self.token}).json()


        final_data = {
            "ACREGISTRO": data["numeroRegistro"],
            "puntaje": r["resultadosGenerales"]["puntajeGlobal"],
            "mensajeMotivacional": r["resultadosGenerales"]["descripcionPercentilNacional"],
            "puntajeMaterias": [ {"code": y["codigoPrueba"], "nombrePrueba": y["nombrePrueba"], "puntaje": y["puntajePrueba"], "nivel": y["ponderacionPrueba"]} for y in r["consultarPuntaje"]["puntajes"]]
        }

        return final_data

    def query_test(self):

        final_data = list()


        success_request, first_response = self.auth_request()

        if not success_request:
            return first_response
        
        for exam in first_response:
            final_data.append(self.get_score_student(data=exam))

        return {
            "status": True,
            "estudiante": self.name,
            "examenes":final_data
        }

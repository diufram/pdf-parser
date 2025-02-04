from flask import Flask, request, jsonify
import pdfplumber
import os
import requests
import shutil
from get_data_xml import get_data_xml
from get_data_pdf import get_data_pdf

from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/api/upload-pdf', methods=['POST'])
def procesarPDF():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Guardar el archivo temporalmente
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        try:
            r = get_data_pdf(file_path)
            os.remove(file_path)  # Eliminar archivo temporal
            return jsonify(r),200
        except Exception as e:
            os.remove(file_path)
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400


@app.route('/api/upload-xml', methods=['POST'])
def procesarXML():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_filexml(file.filename):
        # Guardar el archivo temporalmente
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        try:
            r = get_data_xml(file_path)
            os.remove(file_path)  # Eliminar archivo temporal
            return jsonify(r)
        except Exception as e:
            os.remove(file_path)
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400
def allowed_file(filename):
    return filename.lower().endswith('.pdf')

def allowed_filexml(filename):
    return filename.lower().endswith('.xml')

def createInvoicePdf(directorio,cookies_dict):
                        archivos_pdf = [f for f in os.listdir(directorio) if f.lower().endswith('.pdf')]
                            # Definir las rutas de las carpetas
                        directorio_exito = os.path.join(directorio, "exito-pfd")
                        directorio_errores = os.path.join(directorio, "errores-pfd")

                        # Crear las carpetas si no existen
                        os.makedirs(directorio_exito, exist_ok=True)
                        os.makedirs(directorio_errores, exist_ok=True)
                        # Procesar cada archivo PDF
                        for archivo in archivos_pdf:
                            file_path = os.path.join(directorio, archivo)
                            archivo_destino_exito = os.path.join(directorio_exito, archivo)
                            archivo_destino_error = os.path.join(directorio_errores, archivo)

                            try:
                                # Extraer datos del PDF
                                r = get_data_pdf(file_path)
                                
                                resCreateInvoice = requests.post(
                                    f"https://sap.icorebiz.net/b1s/v2/Drafts",
                                    json=r,
                                    cookies=cookies_dict  # Pasar el diccionario de cookies
                                )

                                #print(f"INVOICE {resCreateInvoice.json()}")

                                shutil.move(file_path, archivo_destino_exito)
                            except Exception as e:
                                shutil.move(file_path, archivo_destino_error)
                                print(f"Ocurrio un error al procesar: {e}")


def createInvoiceXml(directorio,cookies_dict):
                        archivos_pdf = [f for f in os.listdir(directorio) if f.lower().endswith('.xml')]
                            # Definir las rutas de las carpetas
                        directorio_exito = os.path.join(directorio, "exito-xml")
                        directorio_errores = os.path.join(directorio, "errores-xml")

                        # Crear las carpetas si no existen
                        os.makedirs(directorio_exito, exist_ok=True)
                        os.makedirs(directorio_errores, exist_ok=True)
                        # Procesar cada archivo PDF
                        for archivo in archivos_pdf:
                            file_path = os.path.join(directorio, archivo)
                            archivo_destino_exito = os.path.join(directorio_exito, archivo)
                            archivo_destino_error = os.path.join(directorio_errores, archivo)

                            try:
                                # Extraer datos del PDF
                                r = get_data_xml(file_path)
                                
                                resCreateInvoice = requests.post(
                                    f"https://sap.icorebiz.net/b1s/v2/Drafts",
                                    json=r,
                                    cookies=cookies_dict  # Pasar el diccionario de cookies
                                )

                                #print(f"INVOICE {resCreateInvoice.json()}")

                                shutil.move(file_path, archivo_destino_exito)
                            except Exception as e:
                                shutil.move(file_path, archivo_destino_error)
                                print(f"Ocurrio un error al procesar: {e}")

@app.route('/api/imp-repository', methods=['POST'])
def sendInvoices():
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    username = data['UserName']
    password = data['Password']
    companydb = data['CompanyDB']
    tipo = data['tipo']
    req = {
        "CompanyDB": companydb,
        "UserName": username,
        "Password": password,
        "Language": 23,
    }

    # Hacer la solicitud POST para iniciar sesión
    response = requests.post("https://sap.icorebiz.net/b1s/v2/Login", json=req)

    # Acceder al directorio (suponiendo que 'url' es la clave en el JSON)
    directorio = data['url']
    try:

        if response.status_code == 200:
            print("Inicio de sesión exitoso")
            
            # Acceder a las cookies de la respuesta
            cookies = response.cookies

            # Mostrar todas las cookies
            print("Cookies recibidas:")
            cookies_dict = {cookie.name: cookie.value for cookie in cookies}
            for name, value in cookies_dict.items():
                print(f"{name} = {value}")


            
            if os.path.exists(directorio):
                if(tipo == 2): #SOLO PARA PDF
                        createInvoicePdf(directorio=directorio, cookies_dict= cookies_dict)
                if(tipo == 1): #SOLO PARA XML
                      createInvoiceXml(directorio=directorio, cookies_dict= cookies_dict)
                if(tipo == 0): #SOLO PARA XML
                      createInvoiceXml(directorio=directorio, cookies_dict= cookies_dict)
                      createInvoicePdf(directorio=directorio, cookies_dict= cookies_dict)

            else:
                     raise Exception(f"El directorio no se encuentra:{directorio}")


        else:
            raise Exception("Erorr con las credenciales configuradas")

    except  Exception as e:
         return jsonify({"error": str(e)}), 400
 

    return jsonify({"message": "Facturas procesadas con exito"}), 200



if __name__ == '__main__':
    app.run(debug=True, port=5001)

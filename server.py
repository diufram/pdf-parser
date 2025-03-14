from flask import Flask, request, jsonify
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
                        if archivos_pdf:
                            # Definir las rutas de las carpetas
                            directorio_exito = os.path.join(directorio, "exito-pfd")
                            directorio_errores = os.path.join(directorio, "errores-pfd")

                            # Crear las carpetas si no existen
                            os.makedirs(directorio_exito, exist_ok=True)
                            os.makedirs(directorio_errores, exist_ok=True)
                            errors_or_exito = {}
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

                                    if(resCreateInvoice.status_code != 201):
                                        data = resCreateInvoice.json()
                                        message = data['error']['message']
                                        raise Exception(message)

                                    shutil.move(file_path, archivo_destino_exito)
                                    errors_or_exito.setdefault("exitos", []).append(f"{archivo} \n")
                                    
                                except Exception as e:
                                    shutil.move(file_path, archivo_destino_error)
                                    errors_or_exito.setdefault("errores", []).append(f"{archivo} {e} \n")
                                    #print(f"Ocurrio un error al procesar: {e}")      
                        else:
                             raise Exception("No hay Archivos Pdf en el directorio para procesar")                       
                        return errors_or_exito
                      
def createInvoiceXml(directorio,cookies_dict):
                        archivos_xml = [f for f in os.listdir(directorio) if f.lower().endswith('.xml')]
                        if archivos_xml:
                            # Definir las rutas de las carpetas
                            directorio_exito = os.path.join(directorio, "exito-xml")
                            directorio_errores = os.path.join(directorio, "errores-xml")

                            # Crear las carpetas si no existen
                            os.makedirs(directorio_exito, exist_ok=True)
                            os.makedirs(directorio_errores, exist_ok=True)
                            errors_or_exito = {}
                            # Procesar cada archivo PDF
                            for archivo in archivos_xml:
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

                                    if(resCreateInvoice.status_code != 201):
                                        data = resCreateInvoice.json()
                                        message = data['error']['message']
                                        raise Exception(message)
                                    errors_or_exito.setdefault("exitos", []).append(f"{archivo} \n")
                                    shutil.move(file_path, archivo_destino_exito)
                                    
                                except Exception as e:
                                    shutil.move(file_path, archivo_destino_error)
                                    errors_or_exito.setdefault("errores", []).append(f"{archivo} {e} \n")
                                    #print(f"Ocurrio un error al procesar: {e}")
                        else:                         
                            raise Exception("No hay Archivos Xml en el directorio para procesar")  
                        return errors_or_exito

@app.route('/api/imp-repository', methods=['POST'])
def sendInvoices():
    data = request.get_json() 
    tipo = data['tipo']
    session = data['session']
    name = session.split('=')[0]
    value = session.split('=')[1]
    repository = data['url']
    content = {
         "pdfse":[],
         "xmlse":[]
    }
    directorio_actual = os.getcwd()
    directorio = os.path.join(directorio_actual, repository)
    try:
        if(tipo != -1):

                cookies_dict = {name: value}

                if os.path.exists(directorio):
                    try:
                        if(tipo == 2): #SOLO PARA PDF
                            content = createInvoicePdf(directorio=directorio, cookies_dict= cookies_dict)
                        
                        if(tipo == 1): #SOLO PARA XML
                            content =  createInvoiceXml(directorio=directorio, cookies_dict= cookies_dict)
                        if(tipo == 0): #PARA AMBOS
                            try:
                                xml = createInvoiceXml(directorio=directorio, cookies_dict=cookies_dict)
                                content.setdefault("xmls", []).append(f"{xml} \n")
                            except Exception as e:
                                #print(e)
                                content.setdefault("xmlse", []).append(f"{e} \n")
                            
                            try:
                                pdf = createInvoicePdf(directorio=directorio, cookies_dict=cookies_dict)
                                content.setdefault("pdfs", []).append(f"{pdf} \n")
                            except Exception as e:
                                #print(e)
                                content.setdefault("pdfse", []).append(f"{e} \n")
                    except Exception as e:

                        raise Exception(e)
                

                else:
                    raise Exception(f"La carpeta del repositorio configurado no existe: {repository}")
        else:
             raise Exception("Seleccione alguno de los 2 Tipos de archivos para procesar (pdf,xml)")

    except  Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Facturas procesadas", "content": content}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)

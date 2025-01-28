from flask import Flask, request, jsonify
import pdfplumber
import os
import re
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
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
            # Extraer texto y tablas del PDF
            data = extract_pdf_data(file_path)
            os.remove(file_path)  # Eliminar archivo temporal
            cabecera = data["tables"][1][0]
            indicesCabecera = getCabeceraPos(cabecera)
            finTable = getFin(data["tables"][1])
            textLimpio= data["text"]
            items = getDataTable(data["tables"][1],finTable,indicesCabecera)
            nitRuc = getNitRuc(textLimpio)
            fecha = getFecha(textLimpio)
            r = {"DocDate": fecha.split(' ')[0],
                "CardCode": nitRuc,
                "FederalTaxID": nitRuc,
                "DocumentLines": items
                }
            return jsonify(r)
        except Exception as e:
            os.remove(file_path)
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400

def allowed_file(filename):
    return filename.lower().endswith('.pdf')

def getFecha(text):
    pattern = r"\b\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}\b"
    match = re.search(pattern, text)

    if match:
        return match.group()
    else:
        pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        match = re.search(pattern, text)
        if match:
            return match.group()
        else:
            print("No se encontró una fecha y hora.")

def getNitRuc(text):
    pattern = r"\b\d{8}-\d{1}\b"
    match = re.search(pattern, text)
    if match:
        return match.group()
    else:
        print("No se encontró un RUC.")

def getCodCliente(list):
    return 1

def extract_pdf_data(file_path):
    data = {
        "text": "",
        "tables": []
    }

    with pdfplumber.open(file_path) as pdf:
        # Extraer texto del PDF
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

        data["text"] = text

        # Extraer tablas del PDF
        tables = []
        page = pdf.pages[0] 
        for page in pdf.pages:
            table = page.extract_tables()
            if table:
                tables.extend(table)

        # Agregar las tablas al resultado
        data["tables"] = table

    return data

def getCabeceraPos(lista):
  indices = []
  for index, row in enumerate(lista):
      if row is not None: 
        if "Cod" in row:
            #print(index)
            indices.append(index)
        if "Cant." in row:
            #print(index)
            indices.append(index)
        if "Precio" in row:
            #print(index)
            indices.append(index)
        if "Descripcion" in row:
            #print(index)
            indices.append(index)

        if "Cantidad" in row:
            #print(index)
            indices.append(index)
        if "Descripción" in row:
            #print(index)
            indices.append(index)
  return indices


def getFin(list):
    for index, row in enumerate(list):  
        if "SUBTOTAL:" in row:
            return index

def getDataTable(list, fin,indices):
    print(list)
    data = []
    for index, row in enumerate(list):  
        if index>0 and index <fin:
          data.append({"ItemCode":row[indices[0]],
                       "ItemDescription":row[indices[1]],
                       "Quantity":row[indices[2]],
                       "PriceAfterVAT":row[indices[3]]
                       })
    return data

if __name__ == '__main__':
    app.run(debug=True, port=5001)

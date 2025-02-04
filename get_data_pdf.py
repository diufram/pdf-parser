import re
import pdfplumber
from datetime import datetime

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
            raise Exception("Error al obtener la fecha")

def getNitRuc(text):
    pattern = r"\b\d{8}-\d{1}\b"
    match = re.search(pattern, text)
    if match:
        return match.group()
    else:
        raise Exception("Error al obtener el Nit/Ruc")

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
    #print(list)
    data = []
    for index, row in enumerate(list):  
        if index>0 and index <fin:
          if(row[indices[1]] != None or row[indices[2]] != None or row[indices[3]] != None):
            data.append({#"ItemCode":row[indices[0]],
                       "ItemDescription":row[indices[1]],
                       "Quantity":row[indices[2]],
                       "PriceAfterVAT":row[indices[3]]
                       })
          else: 
              raise Exception("Error al obtener los datos de los articulos")
    return data


def convertir_fecha(fecha_str):
    # Definir el formato actual de la fecha
    formato_original = "%d-%m-%Y %H:%M:%S"
    # Convertir la cadena de fecha a un objeto datetime
    fecha_obj = datetime.strptime(fecha_str, formato_original)

    # Definir el formato deseado (yyyy-MM-dd)
    formato_deseado = "%Y-%m-%d"
    # Convertir el objeto datetime a una cadena con el formato deseado
    fecha_formateada = fecha_obj.strftime(formato_deseado)

    return fecha_formateada


def get_data_pdf(archivo):

        # Extraer datos del PDF
        data = extract_pdf_data(archivo)

        # Extraer los detalles necesarios del archivo PDF
        cabecera = data["tables"][1][0]  # Ajusta según la estructura de tu PDF
        indicesCabecera = getCabeceraPos(cabecera)
        finTable = getFin(data["tables"][1])
        textLimpio = data["text"]
        items = getDataTable(data["tables"][1], finTable, indicesCabecera)
        nitRuc = getNitRuc(textLimpio)  # Obtén el Nit o RUC
        fecha = getFecha(textLimpio)  # Extrae la fecha si es necesario
        fechaFormateada = convertir_fecha(fecha_str=fecha)
        # Construir el diccionario con los datos extraídos
        req = {
            "DocDate": fechaFormateada,  # Puedes modificar la fecha o extraerla del texto
            "CardCode": "PL0009",  # Modifica el CardCode según lo que necesites
            "FederalTaxID": nitRuc,
            "U_ORIGEN": "DMS",
            "DocObjectCode": 18,
            "GroupNumber": 1,
            "PaymentGroupCode": 1,
            "DocType": "S",
            "DocumentLines": items  # Los productos/items obtenidos del PDF
        }

        # Devuelve el diccionario con los datos procesados
        return req

        


import os
from get_data_xml import get_data_xml
from get_data_pdf import get_data_pdf
def getDatosXml():
    directorio = "/Users/matias/Downloads/Paraguay"
    if not os.path.exists(directorio):
        print(f"El directorio '{directorio}' no existe.")
    else:
        # Recorrer los archivos en el directorio
        for archivo in os.listdir(directorio):
            if archivo.endswith(".pdf"):  # Filtrar solo archivos XML
                ruta_completa = os.path.join(directorio, archivo)
                print(f"\nProcesando archivo: {ruta_completa}")

                # Llamar a la función y obtener los detalles
                detalles_productos = get_data_pdf(ruta_completa)

                print(detalles_productos)

getDatosXml()
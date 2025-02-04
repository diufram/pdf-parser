import os
import xml.etree.ElementTree as ET

def get_data_xml(archivo_xml):
    
    detalles = []

    # Verificar si el archivo existe
    if not os.path.exists(archivo_xml):
        print(f"El archivo '{archivo_xml}' no existe.")
        return detalles

    # Cargar el archivo XML
        tree = ET.parse(archivo_xml)
        root = tree.getroot()

        # Obtener el espacio de nombres del XML
        namespace = root.tag.split("}")[0].strip("{")  # Extraer el namespace
        ns = {"ns": namespace}  # Definir prefijo para búsqueda

        # Buscar el campo dRucEm dentro del XML con namespace
        dRucEm = root.find(".//ns:dRucEm", ns)
        fecha = root.find(".//ns:dFeEmiDE", ns)

        # Buscar todos los productos <gCamItem>
        items = root.findall(".//ns:gCamItem", ns)

        if dRucEm is not None:
            print(f"dRucEm: {dRucEm.text}")
        else:
            print("No se encontró la etiqueta <dRucEm>.")

        if fecha is not None:
            print(f"Fecha: {fecha.text}")
        else:
            print("No se encontró la etiqueta <dFeEmiDE>.")

        # Imprimir los productos
        if items:
            for item in items:
                dCodInt = item.find("ns:dCodInt", ns)
                dDesProSer = item.find("ns:dDesProSer", ns)
                dCantProSer = item.find("ns:dCantProSer", ns)
                dPUniProSer = item.find("ns:gValorItem/ns:dPUniProSer", ns)  # Aquí añadimos el campo dPUniProSer

                codigo = dCodInt.text if dCodInt is not None else "N/A"
                descripcion = dDesProSer.text if dDesProSer is not None else "N/A"
                cantidad = dCantProSer.text if dCantProSer is not None else "N/A"
                precio_unitario = dPUniProSer.text if dPUniProSer is not None else "N/A"  # Valor de dPUniProSer
                detalles.append({
                    "ItemDescription": descripcion,
                    "Quantity": cantidad,
                    "PriceAfterVAT": precio_unitario
                })

        else:
            print("No se encontraron productos.")
        
        req = {
                            #"DocDate": "",#fecha.split(' ')[0],
                            "DocDate": fecha.text.split("T")[0],
                            "CardCode": "PL0009",
                            "FederalTaxID": dRucEm.text,
                            "U_ORIGEN": "DMS",
                            "DocObjectCode" : 18,
                            "GroupNumber": 1,
                            "PaymentGroupCode": 1,
                            "DocType":"S",
                            "DocumentLines": detalles
                        }
        return req



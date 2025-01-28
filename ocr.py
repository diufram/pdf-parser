import pdfplumber

with pdfplumber.open("b.pdf") as pdf:
    page = pdf.pages[0]  # Tomamos la primera página
    table = page.extract_table()  # Extraemos la tabla
    for row in table:
            print(row)
        

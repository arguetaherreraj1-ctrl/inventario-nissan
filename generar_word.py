import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from generar_excel import herramientas_organizadas

def set_cell_background(cell, hex_color):
    """Aplica sombreado de fondo a una celda de forma 100% segura para Word."""
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def crear_documento_word(ruta_destino):
    doc = Document()

    # Configurar márgenes del documento
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Colores corporativos Nissan
    COLOR_ROJO = RGBColor(195, 0, 47)      # #C3002F
    COLOR_GRIS_OSCURO = RGBColor(33, 37, 41)
    COLOR_AZUL = RGBColor(30, 58, 138)
    COLOR_VERDE = RGBColor(22, 101, 52)
    COLOR_AMARILLO = RGBColor(161, 98, 7)

    # ----------------------------------------------------
    # PORTADA / ENCABEZADO PRINCIPAL
    # ----------------------------------------------------
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_before = Pt(0)
    p_header.paragraph_format.space_after = Pt(2)
    
    r_nissan = p_header.add_run("NISSAN TALLER Y REFACCIONES\n")
    r_nissan.font.name = "Arial"
    r_nissan.font.size = Pt(20)
    r_nissan.font.bold = True
    r_nissan.font.color.rgb = COLOR_ROJO

    r_titulo = p_header.add_run("GUÍA DE ORGANIZACIÓN DE ALMACÉN Y ESTANTES\n")
    r_titulo.font.name = "Arial"
    r_titulo.font.size = Pt(15)
    r_titulo.font.bold = True
    r_titulo.font.color.rgb = COLOR_GRIS_OSCURO

    r_sub = p_header.add_run("Distribución Ergonómica de 57 Herramientas Especiales en 3 Estantes (A, B, C) y Zona de Piso (D1)\nMetodología 5S y Control por Códigos QR")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True

    doc.add_paragraph() # Espacio

    # ----------------------------------------------------
    # 1. PRINCIPIOS DE DISTRIBUCIÓN ERGONÓMICA
    # ----------------------------------------------------
    p_intro_titulo = doc.add_paragraph()
    p_intro_titulo.paragraph_format.space_before = Pt(6)
    p_intro_titulo.paragraph_format.space_after = Pt(2)
    r_it = p_intro_titulo.add_run("1. PRINCIPIOS DE DISTRIBUCIÓN ERGONÓMICA")
    r_it.font.name = "Arial"
    r_it.font.size = Pt(12)
    r_it.font.bold = True
    r_it.font.color.rgb = COLOR_ROJO

    p_intro = doc.add_paragraph(
        "Para que cualquier técnico, aprendiz o bodeguero encuentre una herramienta en menos de 10 segundos, "
        "el catálogo físico de 57 herramientas se dividió en 3 estantes balanceados (~19 herramientas cada uno) "
        "agrupados por el sistema del vehículo y organizados en 3 niveles de altura:"
    )
    p_intro.paragraph_format.space_after = Pt(6)
    p_intro.style.font.name = "Arial"
    p_intro.style.font.size = Pt(10)

    # Tabla resumen de alturas (Usando estilo nativo 'Table Grid' 100% compatible con Word)
    tabla_alturas = doc.add_table(rows=4, cols=3)
    tabla_alturas.style = 'Table Grid'
    tabla_alturas.alignment = WD_TABLE_ALIGNMENT.CENTER

    encabezados_alt = ["Nivel de Altura", "Tipo de Herramienta a Colocar", "Criterio de Seguridad"]
    for i, h in enumerate(encabezados_alt):
        cell = tabla_alturas.cell(0, i)
        cell.text = h
        set_cell_background(cell, "2B2D42")
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        if len(p.runs) > 0:
            p.runs[0].font.name = "Arial"
            p.runs[0].font.bold = True
            p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
            p.runs[0].font.size = Pt(9.5)

    datos_alt = [
        ("Nivel 1 (Abajo: 0 - 60 cm)", "Maletines pesados, probadores en estuches grandes y kits maestros.", "Evitar lesiones de columna al agacharse o levantar peso del suelo."),
        ("Nivel 2 (Centro: 60 - 140 cm)", "Herramientas de mano de uso diario, escáneres y kits medianos.", "Zona ergonómica 'dorada': alcance inmediato sin esfuerzo."),
        ("Nivel 3 (Arriba: 140 - 190 cm)", "Equipo de seguridad (EPP), dados especiales, calibradores y piezas ligeras.", "Fácil acceso sin riesgo de que caigan objetos pesados.")
    ]
    for row_idx, data in enumerate(datos_alt, 1):
        bg = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = tabla_alturas.cell(row_idx, col_idx)
            cell.text = text
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            if len(p.runs) > 0:
                p.runs[0].font.name = "Arial"
                p.runs[0].font.size = Pt(9)
                if col_idx == 0:
                    p.runs[0].font.bold = True

    doc.add_paragraph() # Espacio

    # ----------------------------------------------------
    # SECCIONES POR ESTANTE
    # ----------------------------------------------------
    estantes_def = [
        ("ESTANTE A: DIAGNÓSTICO, ELECTRICIDAD Y SEGURIDAD EPP (19 PIEZAS)", "A", "C3002F", COLOR_ROJO, "[ESTANTE A]"),
        ("ESTANTE B: MOTOR, COMBUSTIBLE, ENFRIAMIENTO Y A/C (19 PIEZAS)", "B", "1E3A8A", COLOR_AZUL, "[ESTANTE B]"),
        ("ESTANTE C: TRANSMISIÓN (CVT), FRENOS Y MECÁNICA DE PRECISIÓN (18 PIEZAS)", "C", "166534", COLOR_VERDE, "[ESTANTE C]"),
        ("ZONA D: ÁREA DE MANIOBRAS PESADAS EN PISO (1 PIEZA)", "D", "854D0E", COLOR_AMARILLO, "[ZONA D]")
    ]

    for titulo_estante, prefijo, hex_color, rgb_color, icono in estantes_def:
        # Título de sección
        p_sec = doc.add_paragraph()
        p_sec.paragraph_format.space_before = Pt(14)
        p_sec.paragraph_format.space_after = Pt(4)
        r_sec = p_sec.add_run(f"{icono} {titulo_estante}")
        r_sec.font.name = "Arial"
        r_sec.font.size = Pt(11.5)
        r_sec.font.bold = True
        r_sec.font.color.rgb = rgb_color

        # Filtrar herramientas de este estante
        piezas_estante = [h for h in herramientas_organizadas if h["ubicacion"].startswith(prefijo)]

        # Crear tabla con estilo 'Table Grid' 100% nativo de Word
        tabla = doc.add_table(rows=len(piezas_estante) + 1, cols=5)
        tabla.style = 'Table Grid'
        tabla.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Anchos de columna proporcionales
        anchos = [Inches(0.85), Inches(1.3), Inches(2.2), Inches(2.65), Inches(0.6)]
        for row in tabla.rows:
            for i, w in enumerate(anchos):
                row.cells[i].width = w

        # Encabezado
        encabezados = ["Ubicación", "Clave Nissan", "Nombre de la Herramienta", "Descripción y Función en el Auto", "Cant."]
        for i, enc in enumerate(encabezados):
            cell = tabla.cell(0, i)
            cell.text = enc
            set_cell_background(cell, hex_color)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            if len(p.runs) > 0:
                p.runs[0].font.name = "Arial"
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                p.runs[0].font.size = Pt(9)
            if i in [0, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Rellenar filas
        for row_idx, h in enumerate(piezas_estante, 1):
            bg = "F9FAFB" if row_idx % 2 == 0 else "FFFFFF"
            
            fila_datos = [
                h["ubicacion"],
                h["clave"],
                h["nombre"],
                f"{h['descripcion']}\n• Uso: {h['funcion']}",
                str(h["cantidad"])
            ]

            for col_idx, val in enumerate(fila_datos):
                cell = tabla.cell(row_idx, col_idx)
                cell.text = val
                set_cell_background(cell, bg)
                
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                if len(p.runs) > 0:
                    p.runs[0].font.name = "Arial"
                    p.runs[0].font.size = Pt(8.5)

                    if col_idx == 0:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p.runs[0].font.bold = True
                        p.runs[0].font.color.rgb = rgb_color
                        p.runs[0].font.size = Pt(10)
                    elif col_idx == 1:
                        p.runs[0].font.bold = True
                        p.runs[0].font.name = "Consolas"
                        p.runs[0].font.size = Pt(9)
                    elif col_idx == 2:
                        p.runs[0].font.bold = True
                    elif col_idx == 4:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p.runs[0].font.bold = True

    # ----------------------------------------------------
    # RECOMENDACIONES FINALES DE SEÑALIZACIÓN EN EL TALLER
    # ----------------------------------------------------
    doc.add_page_break()
    p_rec_tit = doc.add_paragraph()
    r_rt = p_rec_tit.add_run("PASOS RECOMENDADOS PARA IDENTIFICACIÓN FÍSICA EN EL TALLER")
    r_rt.font.name = "Arial"
    r_rt.font.size = Pt(13)
    r_rt.font.bold = True
    r_rt.font.color.rgb = COLOR_ROJO

    p_pasos = [
        ("1. Señalización con cinta de color en cada estante:", 
         "• Estante A: Colocar cinta o marco AZUL (Diagnóstico y EPP).\n"
         "• Estante B: Colocar cinta o marco ROJO (Motor y Combustible).\n"
         "• Estante C: Colocar cinta o marco VERDE (Transmisión CVT y Frenos).\n"
         "• Zona D: Pintar cuadro amarillo en el piso para la Grúa de 2 Toneladas."),
        ("2. Identificación de niveles en cada estante:", 
         "Pega una etiqueta visible en cada repisa:\n"
         "• Repisa de abajo: 'NIVEL 1 - EQUIPOS PESADOS'\n"
         "• Repisa del medio: 'NIVEL 2 - HERRAMIENTAS DE MANO Y KITS'\n"
         "• Repisa de arriba: 'NIVEL 3 - EPP Y PIEZAS LIGERAS'"),
        ("3. Impresión de las Hojas Murales con Código QR:", 
         "En el sistema web, presiona el botón 'Hojas de Pared' o 'Descargar PDF QR'. Imprime las hojas en tamaño carta y plastifícalas para pegarlas en el lateral de cada estante."),
        ("4. Uso del Escaneo Rápido Inteligente:", 
         "Cuando un técnico necesite una pieza, solo abre el sistema en su celular, apunta al QR del estante o de la pared, y el sistema registra de inmediato la salida de la herramienta a su nombre, guardándolo en la bitácora para el reporte en Excel.")
    ]

    for paso_tit, paso_desc in p_pasos:
        p_pt = doc.add_paragraph()
        p_pt.paragraph_format.space_before = Pt(8)
        p_pt.paragraph_format.space_after = Pt(2)
        r_p = p_pt.add_run(paso_tit)
        r_p.font.name = "Arial"
        r_p.font.bold = True
        r_p.font.size = Pt(10.5)

        p_pd = doc.add_paragraph(paso_desc)
        p_pd.paragraph_format.space_before = Pt(1)
        p_pd.paragraph_format.space_after = Pt(4)
        p_pd.style.font.name = "Arial"
        p_pd.style.font.size = Pt(9.5)

    doc.save(ruta_destino)
    print(f"[OK] Documento Word generado exitosamente en: {ruta_destino}")

if __name__ == "__main__":
    ruta_doc = "C:/Users/Admin/Documents/Inventario_Nissan/Guia_Organizacion_Almacen_Nissan.docx"
    ruta_scratch = "C:/Users/Admin/.gemini/antigravity/scratch/inventario-nissan/Guia_Organizacion_Almacen_Nissan.docx"
    ruta_brain = "C:/Users/Admin/.gemini/antigravity/brain/74b82f0d-56c2-4e4c-873b-a4c28163990d/Guia_Organizacion_Almacen_Nissan.docx"
    
    try:
        crear_documento_word(ruta_doc)
    except Exception as e:
        print("Aviso al escribir en Documents:", e)

    try:
        crear_documento_word(ruta_scratch)
    except Exception as e:
        print("Aviso al escribir en scratch:", e)

    try:
        crear_documento_word(ruta_brain)
    except Exception as e:
        print("Aviso al escribir en brain:", e)

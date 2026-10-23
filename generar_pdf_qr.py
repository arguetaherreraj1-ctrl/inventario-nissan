import os
import io
import qrcode
from PIL import Image

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from generar_excel import herramientas_organizadas

def generar_qr_imagen(texto):
    """Genera una imagen PIL del código QR en memoria"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=1,
    )
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generar_pdf_completo(ruta_salida):
    # Márgenes de 20 pt para aprovechar toda la hoja Carta
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    # Colores corporativos Nissan
    ROJO_NISSAN = colors.HexColor("#C3002F")
    GRIS_OSCURO = colors.HexColor("#1F2937")

    # Estilos de texto
    style_titulo = ParagraphStyle(
        'TituloNissan',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.white
    )

    style_grupo_tag = ParagraphStyle(
        'GrupoTag',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        alignment=2, # Derecha
        textColor=colors.white
    )

    style_card_clave = ParagraphStyle(
        'CardClave',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=9.5,
        alignment=1, # Centro
        textColor=colors.HexColor("#111827")
    )

    style_card_pos = ParagraphStyle(
        'CardPos',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=8.5,
        alignment=1,
        textColor=ROJO_NISSAN
    )

    style_card_desc = ParagraphStyle(
        'CardDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=7.5,
        alignment=1,
        textColor=colors.HexColor("#374151")
    )

    style_card_stock = ParagraphStyle(
        'CardStock',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6,
        leading=7,
        alignment=1,
        textColor=colors.HexColor("#6B7280")
    )

    elementos = []

    # Secciones por estante
    secciones = [
        ("ESTANTE A", "DIAGNÓSTICO, ELECTRICIDAD Y EPP (19 PIEZAS)", "A", "#1E3A8A"),
        ("ESTANTE B", "MOTOR, COMBUSTIBLE, ENFRIAMIENTO Y A/C (19 PIEZAS)", "B", "#C3002F"),
        ("ESTANTE C", "TRANSMISIÓN (CVT), FRENOS Y MECÁNICA (18 PIEZAS)", "C", "#15803D"),
        ("ZONA D", "ÁREA DE MANIOBRAS PESADAS EN PISO (1 PIEZA)", "D", "#854D0E")
    ]

    ancho_hoja = 572 # Ancho disponible de impresión

    for idx_sec, (nombre_estante, subtitulo_estante, prefijo, color_hex) in enumerate(secciones):
        piezas = [h for h in herramientas_organizadas if h["ubicacion"].startswith(prefijo)]
        if not piezas:
            continue

        color_sec = colors.HexColor(color_hex)

        # -----------------------------
        # BANNER DE ENCABEZADO
        # -----------------------------
        p_izq = Paragraph(
            f"<b>NISSAN TALLER Y REFACCIONES</b><br/><font size=7>CATÁLOGO MURAL PARA PARED - {subtitulo_estante}</font>",
            style_titulo
        )
        p_der = Paragraph(f"<b>{nombre_estante}</b><br/><font size=7>Total: {len(piezas)} piezas</font>", style_grupo_tag)

        tabla_header = Table([[p_izq, p_der]], colWidths=[390, 182])
        tabla_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), color_sec),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabla_header)
        elementos.append(Spacer(1, 6))

        # -----------------------------
        # CUADRÍCULA DE TARJETAS QR
        # -----------------------------
        num_cols = 4 if len(piezas) > 4 else len(piezas)
        ancho_col = ancho_hoja / num_cols

        filas_tabla = []
        fila_actual = []

        for p in piezas:
            qr_buf = generar_qr_imagen(p["clave"])
            qr_size = 56 if len(piezas) > 4 else 120
            img_qr = RLImage(qr_buf, width=qr_size, height=qr_size)

            desc_corta = p["nombre"][:35] + ("..." if len(p["nombre"]) > 35 else "")

            card_cell = [
                Paragraph(f"<b>CLAVE:</b> <font color='#C3002F'><b>{p['ubicacion']}</b></font>", style_card_pos),
                Paragraph(f"<b>{p['clave']}</b>", style_card_clave),
                img_qr,
                Paragraph(desc_corta, style_card_desc),
                Paragraph(f"Stock: {p['cantidad']}/{p['cantidad']}", style_card_stock)
            ]

            tabla_mini = Table([[c] for c in card_cell], colWidths=[ancho_col - 6])
            tabla_mini.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor("#374151")),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
            ]))

            fila_actual.append(tabla_mini)

            if len(fila_actual) == num_cols:
                filas_tabla.append(fila_actual)
                fila_actual = []

        if fila_actual:
            while len(fila_actual) < num_cols:
                fila_actual.append(Paragraph("", style_card_desc))
            filas_tabla.append(fila_actual)

        tabla_grid = Table(filas_tabla, colWidths=[ancho_col] * num_cols)
        tabla_grid.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elementos.append(tabla_grid)

        elementos.append(Spacer(1, 4))
        p_pie = Paragraph(
            f"<font color='#6B7280' size=6.5>• Escanea con tu celular para registrar la toma de la herramienta • <b>{nombre_estante}</b></font>",
            ParagraphStyle('Pie', alignment=1)
        )
        elementos.append(p_pie)

        if idx_sec < len(secciones) - 1:
            elementos.append(PageBreak())

    doc.build(elementos)
    print(f"[OK] Archivo PDF generado exitosamente en: {ruta_salida}")

if __name__ == "__main__":
    ruta_pdf_doc = "C:/Users/Admin/Documents/Inventario_Nissan/Catalogo_Mural_QR_Nissan.pdf"
    ruta_pdf_scratch = "C:/Users/Admin/.gemini/antigravity/scratch/inventario-nissan/Catalogo_Mural_QR_Nissan.pdf"
    ruta_pdf_brain = "C:/Users/Admin/.gemini/antigravity/brain/74b82f0d-56c2-4e4c-873b-a4c28163990d/Catalogo_Mural_QR_Nissan.pdf"

    generar_pdf_completo(ruta_pdf_doc)
    generar_pdf_completo(ruta_pdf_scratch)
    generar_pdf_completo(ruta_pdf_brain)

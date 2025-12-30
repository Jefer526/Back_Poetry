"""
Generación de reportes PDF para Inventario
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime


def generar_pdf_inventario(inventarios, titulo="Reporte de Inventario"):
    """
    Genera un PDF con el reporte de inventarios
    
    Args:
        inventarios: QuerySet de inventarios
        titulo: Título del reporte
    
    Returns:
        BytesIO con el PDF generado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph(titulo, title_style))
    elements.append(Paragraph(
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 0.3*inch))
    
    # Datos de la tabla
    data = [
        ['Código', 'Producto', 'Stock', 'Ubicación', 'Estado']
    ]
    
    for inv in inventarios:
        estado = "OK"
        if inv.cantidad_actual <= 0:
            estado = "SIN STOCK"
        elif inv.cantidad_actual <= inv.producto.stock_minimo:
            estado = "BAJO"
        
        data.append([
            inv.producto.codigo,
            inv.producto.nombre[:30],  # Truncar nombre largo
            str(inv.cantidad_actual),
            inv.ubicacion or '-',
            estado
        ])
    
    # Totales
    total_stock = sum(inv.cantidad_actual for inv in inventarios)
    data.append(['', '', '', 'TOTAL:', str(total_stock)])
    
    # Crear tabla
    table = Table(data, colWidths=[1*inch, 3*inch, 1*inch, 1.5*inch, 1*inch])
    
    # Estilo de la tabla
    table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('GRID', (0, 0), (-1, -2), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0f0f0')]),
        
        # Fila de totales
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_pdf_movimientos(movimientos, titulo="Reporte de Movimientos"):
    """
    Genera un PDF con el reporte de movimientos de inventario
    
    Args:
        movimientos: QuerySet de movimientos
        titulo: Título del reporte
    
    Returns:
        BytesIO con el PDF generado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph(titulo, title_style))
    elements.append(Paragraph(
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 0.3*inch))
    
    # Datos de la tabla
    data = [
        ['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Usuario']
    ]
    
    for mov in movimientos:
        tipo_display = "↑ ENTRADA" if mov.tipo == 'entrada' else "↓ SALIDA"
        usuario = mov.usuario.username if mov.usuario else '-'
        
        data.append([
            mov.fecha.strftime('%d/%m/%Y %H:%M'),
            mov.inventario.producto.codigo,
            tipo_display,
            str(mov.cantidad),
            usuario
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch, 1.5*inch])
    
    # Estilo de la tabla
    table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
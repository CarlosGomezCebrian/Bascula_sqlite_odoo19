#logic_print_folios.py

import sys
from escpos import printer
from pathlib import Path
from typing import Dict, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from db_operations.db_config import get_company_config
from utils.logger_config import app_logger  # ✅ Logger centralizado
import textwrap
import os
import usb.core
import usb.util

# Configuración de la impresora
USB_VENDOR_ID = 0x04B8
USB_PRODUCT_ID = 0x0E03

# Ruta del logotipo
COMPANY_DATA = get_company_config()
if COMPANY_DATA:
    IMAGE_PATH = COMPANY_DATA.get('company_logo_path_print')
    COMPANY_ADDRESS = COMPANY_DATA.get('company_address')
    COMPANY_NAME = COMPANY_DATA.get('company_name').upper()
WIDTH_TITLE = 30
WIDTH_LINE = 60
WIDTH_TEXT = 40

# ✅ Logger específico para impresión
logger = app_logger.getChild('PrintFolios')

def _check_printer_connection():
    """
    Verifica si la impresora está conectada y disponible
    """
    logger.debug("🔍 Verificando conexión de impresora...")
    
    try:
        # Buscar dispositivo USB
        device = usb.core.find(idVendor=USB_VENDOR_ID, idProduct=USB_PRODUCT_ID)
        
        if device is None:
            logger.error("❌ Impresora no encontrada. Verifique:")
            logger.error(f"   - Vendor ID: {hex(USB_VENDOR_ID)}")
            logger.error(f"   - Product ID: {hex(USB_PRODUCT_ID)}")
            logger.error("   - Cable USB conectado")
            logger.error("   - Impresora encendida")
            return False
        
        logger.info("✅ Impresora detectada y conectada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al verificar impresora: {e}")
        return False

def _get_available_usb_printers():
    """
    Lista todas las impresoras USB disponibles para diagnóstico
    """
    logger.debug("🔍 Buscando impresoras USB disponibles...")
    
    try:
        devices = usb.core.find(find_all=True)
        available_printers = []
        
        for device in devices:
            printer_info = {
                'vendor_id': hex(device.idVendor),
                'product_id': hex(device.idProduct),
                'manufacturer': usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else 'N/A',
                'product': usb.util.get_string(device, device.iProduct) if device.iProduct else 'N/A'
            }
            available_printers.append(printer_info)
            
        if available_printers:
            logger.info("📋 Impresoras USB disponibles:")
            for printer in available_printers:
                logger.info(f"   - Vendor: {printer['vendor_id']}, Product: {printer['product_id']}, " 
                           f"Manufacturer: {printer['manufacturer']}, Product: {printer['product']}")
        else:
            logger.warning("⚠️ No se encontraron impresoras USB")
            
        return available_printers
        
    except Exception as e:
        logger.error(f"❌ Error al listar impresoras USB: {e}")
        return []

def print_weighing_ticket(data: Dict[str, Any]) -> bool:
    """
    Imprime dos tickets de pesaje en una impresora térmica ESC/POS.
    Si la impresión falla, genera un PDF como respaldo.
    """
    p = None
    folio_number = data.get('folio_number', 'sin_folio')
    
    try:
        logger.info(f"🖨️ Iniciando impresión de ticket - Folio: {folio_number}")
        
        # Verificar conexión de impresora primero
        if not _check_printer_connection():
            logger.warning("🔄 Impresora no disponible, generando PDF de respaldo...")
            _generate_weighing_ticket_pdf(data)
            return False, "Impresora no conectada - Se generó PDF de respaldo"
        
        # Listar impresoras disponibles para diagnóstico
        _get_available_usb_printers()
        
        logger.debug("🔌 Conectando a impresora USB...")
        p = printer.Usb(
            USB_VENDOR_ID,
            USB_PRODUCT_ID,
            profile="TM-T88IV"
        )
        logger.debug("✅ Conexión a impresora establecida")

        # Repetir dos veces: cliente y archivo interno
        for copia in range(2):
            logger.debug(f"📄 Imprimiendo copia {copia + 1}")
            
            # Verificar logo antes de imprimir
            if not os.path.exists(IMAGE_PATH):
                logger.warning(f"⚠️ Logo no encontrado en: {IMAGE_PATH}")
            
            p.set(align='center')
            
            # Intentar cargar e imprimir logo
            try:
                if os.path.exists(IMAGE_PATH):
                    p.image(IMAGE_PATH)
                    logger.debug("✅ Logo impreso")
                else:
                    logger.warning("⚠️ No se pudo imprimir logo - archivo no encontrado")
            except Exception as logo_error:
                logger.warning(f"⚠️ Error al imprimir logo: {logo_error}")
            
            p.text("\n\n")
            p.set(font='b', align='center', bold=True, double_height=True, double_width=True)
            p.text(f"{_wrap_lines(COMPANY_NAME, WIDTH_TITLE )}\n")
            p.set(font='b', align='center', bold=True, normal_textsize=True)
            p.text(_wrap_lines(COMPANY_ADDRESS, WIDTH_LINE ))
            p.text("_" * 64 + "\n\n")

            # Datos principales
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=1)
            p.text(f"Tipo: {data.get('weighing_type', 'N/A')}\n\n")
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=2)
            p.text(f"Folio: {data.get('folio_number', 'N/A')}\n\n")
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=1)
            p.text(f"Placas: {data.get('plates', 'N/A')}\n")
            p.text(f"Vehículo: {data.get('vehicle_name', 'N/A')}\n")
            p.text(f"Remolque: {data.get('remolque_name', 'N/A')}\n")
            p.text(f"Conductor: {data.get('driver_name', 'N/A')}\n")
            p.text("_" * 32 + "\n")
            p.text(f"Material: {data.get('material_name', 'N/A')}\n")
            p.text(f"Cliente: {data.get('customer_name', 'N/A')}\n\n")

            # Pesos
            gross_weight = int(data.get('gross_weight', 0))
            tare_weight = int(data.get('tare_weight', 0))
            net_weight = int(data.get('net_weight', 0))
            notes = data.get('notes')
            
            p.set(font='a', align='center', bold=True, custom_size=True, width=2, height=2)
            p.text("Mediciones\n")
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=1)
            p.text("_" * 32 + "\n")
            p.text(f"Usuario peso Entrada:\n{data.get('user_name', 'N/A')}\n")
            p.text(f"Fecha/Hr Entrada:\n{data.get('date_start', 'N/A')}\n\n")
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=2)
            p.text(f"P. BRUTO:{_available_spaces(gross_weight)} KG\n")
            p.text(f"P. TARA: {_available_spaces(tare_weight)} KG\n")
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=1)
            p.text(f"--------------------------------\n")
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=2)
            p.text(f"P. NETO: {_available_spaces(net_weight)} KG\n\n")
            p.set(font='b', align='left', bold=True, custom_size=True, width=2, height=1)
            p.text(f"Usuario peso Salida:\n{data.get('user_name_closed', 'N/A')}\n")
            p.text(f"Fecha/Hr Salida:\n{data.get('date_end', 'N/A')}\n\n")
            p.set(font='b', align='left',bold=True, custom_size=True, width=2, height=2)
            p.text("Notas:\n")            
            p.set(font='b', align='center',bold=True, custom_size=True, width=1, height=2)                
            p.text(f"{_set_notes(notes)}")
            p.set(font='b', align='center', normal_textsize=True)

            if copia == 0:
                p.text("\n\nCOPIA: CLIENTE\n")
            else:
                p.text("\n\nCOPIA: ARCHIVO INTERNO\n")
            p.cut()

        logger.info(f"✅ Ticket impreso exitosamente - Folio: {folio_number}")
        return True, ""

    except Exception as e:
        error_msg = f"❌ No se pudo imprimir el ticket {folio_number}: {e}"
        logger.error(error_msg, exc_info=True)
        
        # Diagnóstico adicional
        logger.info("🔧 Ejecutando diagnóstico de impresora...")
        _get_available_usb_printers()
        
        try:
            logger.info("🔄 Generando PDF de respaldo...")
            pdf_path = _generate_weighing_ticket_pdf(data)
            logger.info(f"✅ PDF de respaldo generado: {pdf_path}")
            return False, f"Impresora no disponible - PDF generado: {pdf_path}"
        except Exception as pdf_e:
            logger.error(f"❌ No se pudo generar el PDF de respaldo: {pdf_e}", exc_info=True)
            return False, f"Error: {e} - También falló PDF: {pdf_e}"

    finally:
        if p is not None:
            try:
                p.close()
                logger.debug("🔌 Conexión a impresora cerrada")
            except Exception as close_e:
                logger.warning(f"⚠️ Error al cerrar la conexión USB: {close_e}")

# === FUNCIÓN PARA GENERAR PDF ===
def _generate_weighing_ticket_pdf(data: Dict[str, Any], output_path=None):
    """
    Genera un PDF con el mismo formato del ticket térmico (80 mm de ancho).
    Convierte el logo para evitar fondo negro.
    """
    folio_number = data.get('folio_number', 'sin_folio')
    logger.debug(f"📄 Generando PDF para folio: {folio_number}")
    
    if not output_path:
        download_dir = str(Path.home() / "Downloads")
        filename = f"ticket_{folio_number}.pdf"
        output_path = os.path.join(download_dir, filename)

    try:
        PAGE_WIDTH = 80 * mm
        PAGE_HEIGHT = 210 * mm  # Aumentamos la altura para contenido dinámico
        c = canvas.Canvas(output_path, pagesize=portrait((PAGE_WIDTH, PAGE_HEIGHT)))
        
        # Configuración de márgenes
        MARGIN_LEFT = 5 * mm
        MARGIN_RIGHT = PAGE_WIDTH - 5 * mm
        CONTENT_WIDTH = PAGE_WIDTH - 10 * mm
        
        y = PAGE_HEIGHT - 5 * mm

        # === LOGOTIPO ===
        if os.path.exists(IMAGE_PATH):
            try:
                logo = ImageReader(IMAGE_PATH)
                c.drawImage(logo, (PAGE_WIDTH - 60 * mm) / 2, y - 25 * mm, 
                           width=60 * mm, height=20 * mm, preserveAspectRatio=True)
                y -= 30 * mm
                logger.debug("✅ Logo cargado en PDF")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo cargar el logo en PDF: {e}")
        else:
            logger.warning(f"⚠️ Ruta de logo no encontrada: {IMAGE_PATH}")

        # === ENCABEZADO ===
        # Usar las variables dinámicas de la compañía
        company_name = COMPANY_NAME
        company_address = COMPANY_ADDRESS
        
        c.setFont("Helvetica-Bold", 10)
        
        # Dividir el nombre de la compañía en líneas si es necesario
        company_name_lines = textwrap.wrap(company_name, width=35)
        for line in company_name_lines:
            c.drawCentredString(PAGE_WIDTH / 2, y, line)
            y -= 4 * mm
        
        y -= 1 * mm
        c.setFont("Helvetica", 7)
        
        # Dirección con manejo de texto largo
        address_lines = textwrap.wrap(company_address, width=42)  # Aprox. caracteres para 80mm
        for line in address_lines:
            c.drawCentredString(PAGE_WIDTH / 2, y, line)
            y -= 3 * mm
        
        y -= 2 * mm
        c.line(MARGIN_LEFT, y, MARGIN_RIGHT, y)
        y -= 6 * mm

        # === FUNCIÓN AUXILIAR PARA TEXTO CON SALTO DE LÍNEA ===
        def draw_wrapped_text(text, font="Helvetica", size=8, bold=False, align="left", max_width_chars=35):
            nonlocal y
            if bold:
                c.setFont("Helvetica-Bold", size)
            else:
                c.setFont(font, size)
                
            if not text:
                text = "N/A"
                
            # Dividir el texto en líneas
            wrapped_lines = textwrap.wrap(str(text), width=max_width_chars)
            
            for line in wrapped_lines:
                if align == "center":
                    c.drawCentredString(PAGE_WIDTH / 2, y, line)
                else:
                    c.drawString(MARGIN_LEFT, y, line)
                y -= 4 * mm
                
            return len(wrapped_lines)

        # === DATOS PRINCIPALES ===
        c.setFont("Helvetica-Bold", 9)
        draw_wrapped_text(f"Tipo: {data.get('weighing_type', 'N/A')}", bold=True)
        y -= 1 * mm
        
        c.setFont("Helvetica-Bold", 12)
        draw_wrapped_text(f"Folio: {data.get('folio_number', 'N/A')}", size=12, bold=True)
        y -= 1 * mm
        
        c.setFont("Helvetica-Bold", 9)
        draw_wrapped_text(f"Placas: {data.get('plates', 'N/A')}", bold=True)
        draw_wrapped_text(f"Vehículo: {data.get('vehicle_name', 'N/A')}", bold=True)
        draw_wrapped_text(f"Remolque: {data.get('remolque_name', 'N/A')}", bold=True)
        draw_wrapped_text(f"Conductor: {data.get('driver_name', 'N/A')}", bold=True)
        
        y -= 2 * mm
        c.line(MARGIN_LEFT, y, MARGIN_RIGHT, y)
        y -= 4 * mm
        
        draw_wrapped_text(f"Material: {data.get('material_name', 'N/A')}", bold=True)
        draw_wrapped_text(f"Cliente: {data.get('customer_name', 'N/A')}", bold=True)
        y -= 6 * mm

        # === PESOS ===
        gross_weight = int(data.get('gross_weight', 0))
        tare_weight = int(data.get('tare_weight', 0))
        net_weight = int(data.get('net_weight', 0))

        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(PAGE_WIDTH / 2, y, "Mediciones")
        y -= 4 * mm
        c.line(MARGIN_LEFT, y, MARGIN_RIGHT, y)
        y -= 4 * mm
        
        # Información de entrada
        draw_wrapped_text(f"Usuario peso Entrada: {data.get('user_name', 'N/A')}")
        draw_wrapped_text(f"Fecha/Hr Entrada: {data.get('date_start', 'N/A')}")
        y -= 2 * mm
        
        # Pesos con formato alineado
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN_LEFT, y, f"P. BRUTO: {gross_weight:>8,} KG")
        y -= 4 * mm
        c.drawString(MARGIN_LEFT, y, f"P. TARA:   {tare_weight:>8,} KG")
        y -= 4 * mm
        
        c.line(MARGIN_LEFT, y, MARGIN_RIGHT, y)
        y -= 4 * mm
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN_LEFT, y, f"P. NETO:   {net_weight:>8,} KG")
        y -= 6 * mm
        
        # Información de salida
        c.setFont("Helvetica", 8)
        draw_wrapped_text(f"Usuario peso Salida: {data.get('user_name_closed', 'N/A')}")
        draw_wrapped_text(f"Fecha/Hr Salida: {data.get('date_end', 'N/A')}")
        y -= 4 * mm

        # === RECTÁNGULO DE NOTAS ===
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN_LEFT, y, "Notas:")
        y -= 5 * mm
        
        # Dibujar rectángulo para notas
        notes_rect_height = 25 * mm
        notes_rect_y = y - notes_rect_height
        
        c.rect(MARGIN_LEFT, notes_rect_y, CONTENT_WIDTH, notes_rect_height)
        
        # Texto de notas dentro del rectángulo
        notes = data.get('notes', '')
        notes_y = y - 4 * mm  # Empezar un poco más abajo del borde superior
        
        if notes and notes != "-":
            c.setFont("Helvetica", 8)
            wrapped_notes = textwrap.wrap(str(notes), width=38)  # Ajustar al ancho del rectángulo
            
            for note_line in wrapped_notes:
                if notes_y > notes_rect_y + 4 * mm:  # Dejar margen interno
                    c.drawString(MARGIN_LEFT + 2 * mm, notes_y, note_line)
                    notes_y -= 3 * mm
                else:
                    # Si no cabe más texto, mostrar puntos suspensivos
                    c.drawString(MARGIN_LEFT + 2 * mm, notes_rect_y + 3 * mm, "...")
                    break
        else:
            c.setFont("Helvetica", 8)
            c.drawString(MARGIN_LEFT + 2 * mm, notes_rect_y + notes_rect_height/2, "Sin notas")

        # === COPIA ===
        y = notes_rect_y - 10 * mm
        c.setFont("Helvetica", 8)
        c.drawCentredString(PAGE_WIDTH / 2, y, "COPIA: CLIENTE")

        c.showPage()
        c.save()
        logger.info(f"📄 PDF generado exitosamente: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Error al generar PDF: {e}", exc_info=True)
        raise

def _available_spaces(weight):
    """Calcula espacios disponibles para alinear pesos"""
    str_weight = str(weight)
    spaces_weight = len(str_weight)
    available_spaces = 7 - spaces_weight
    text_spaces = " " * available_spaces + str_weight
    return text_spaces

def _set_notes(notes):
    """Integra las notas al rectángulo de notas"""
    logger.debug("Formateando notas para impresión")
    
    MAX_WIDTH = 60 
    horizontal_line = "─" * MAX_WIDTH
    horizontal_spaced_line = " " * MAX_WIDTH
    first_line = "┌" + horizontal_line + "┐\n"
    separator_line = "│" + horizontal_spaced_line + "│\n"
    end_line = "└" + horizontal_line + "┘\n"
    print_notes = first_line + separator_line + end_line
    insert_compiled_lines = ""
    
    if notes and notes != "-":
        logger.debug(f"Procesando notas: {notes[:50]}...")  # Log parcial por privacidad

        for original_line in notes.splitlines():
            wrapped_lines = textwrap.wrap(original_line, width=MAX_WIDTH)
            for line in wrapped_lines:
                number_of_characters = len(line)
                plus_caracter_line = MAX_WIDTH - number_of_characters
                insert_line = "│" + line + " " * plus_caracter_line + "│\n"
                insert_compiled_lines += insert_line

        print_notes = first_line + separator_line + insert_compiled_lines + separator_line + end_line
        logger.debug("✅ Notas formateadas exitosamente")
        return print_notes
    else:
        print_notes = first_line + separator_line * 3 + end_line
        logger.debug("✅ Notas vacías, usando formato por defecto")
        return print_notes

def _wrap_lines(lines, MAX_WIDTH):
    """Se utiliza para separar líneas"""
    logger.debug(f"Envolviendo texto a {MAX_WIDTH} caracteres")
    
    insert_compiled_lines = ""
     
    wrapped_lines = textwrap.wrap(lines, width=MAX_WIDTH)
    for line in wrapped_lines:
        line_line = line + "\n"
        insert_compiled_lines += line_line

    logger.debug(f"✅ Texto envuelto en {len(wrapped_lines)} líneas")
    return insert_compiled_lines
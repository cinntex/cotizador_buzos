import streamlit as st
from fpdf import FPDF
from datetime import date
import io
import os
from PIL import Image, UnidentifiedImageError
from datetime import datetime
import pandas as pd

# === CONFIGURACIÓN GENERAL ===
CARPETA_UPLOADS = "uploads"
RUTA_HISTORIAL = "historial_cotizaciones.xlsx"

# === FUNCIONES UTILITARIAS ===
def guardar_archivo_local(archivo, tipo="logo"):
    if archivo is None:
        return None
    os.makedirs(CARPETA_UPLOADS, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = os.path.splitext(archivo.name)[-1]
    nombre_archivo = f"{tipo}_{timestamp}{extension}"
    ruta_guardado = os.path.join(CARPETA_UPLOADS, nombre_archivo)
    with open(ruta_guardado, "wb") as f:
        f.write(archivo.read())
    return ruta_guardado

def guardar_historial_excel(datos):
    df_nuevo = pd.DataFrame([datos])
    try:
        if os.path.exists(RUTA_HISTORIAL):
            df_existente = pd.read_excel(RUTA_HISTORIAL)
            df_actualizado = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_actualizado = df_nuevo
    except Exception as e:
        st.warning("⚠️ El archivo de historial estaba dañado y se ha reiniciado automáticamente.")
        try:
            os.remove(RUTA_HISTORIAL)
        except:
            pass
        df_actualizado = df_nuevo

    df_actualizado.to_excel(RUTA_HISTORIAL, index=False)

def guardar_pdf_local(pdf_bytes, nombre_base="cotizacion"):
    ahora = datetime.now()
    año = ahora.strftime("%Y")
    mes = ahora.strftime("%m")
    fecha_hora = ahora.strftime("%Y%m%d_%H%M%S")
    carpeta = os.path.join("pdfs", año, mes)
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = f"{nombre_base}_{fecha_hora}.pdf"
    ruta_completa = os.path.join(carpeta, nombre_archivo)
    with open(ruta_completa, "wb") as f:
        f.write(pdf_bytes.getbuffer())
    return ruta_completa

def obtener_ruta_modelo_seleccionado(nombre_modelo):
    if nombre_modelo.startswith("Buzos"):
        partes = nombre_modelo.split(" - ")
        if len(partes) == 2:
            categoria, nombre = partes
            ruta = os.path.join("images", categoria, f"{nombre}.jpg")
            return ruta if os.path.exists(ruta) else None
    return None

# === CLASE PDF ===
class PDFCotizacion(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Resumen de Cotización - Buzos Deportivos', ln=True, align='C')
        self.ln(5)

    def add_datos_cliente(self, datos):
        self.set_font("Arial", "", 12)
        for etiqueta, valor in datos.items():
            self.multi_cell(0, 10, f"{etiqueta}: {valor}")
            self.ln(1)

def generar_pdf(datos, ruta_logo=None, ruta_disenio=None, ruta_modelo=None):
    pdf = PDFCotizacion()
    pdf.add_page()
    pdf.add_datos_cliente(datos)
    if ruta_modelo and os.path.exists(ruta_modelo):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Imagen del modelo seleccionado:", ln=True)
        pdf.ln(2)
        pdf.image(ruta_modelo, w=90)
        pdf.ln(5)
    if ruta_disenio and os.path.exists(ruta_disenio):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Imagen de referencia o diseño:", ln=True)
        pdf.ln(2)
        pdf.image(ruta_disenio, w=90)
        pdf.ln(5)
    if ruta_logo and os.path.exists(ruta_logo):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Logo para bordado:", ln=True)
        pdf.ln(2)
        pdf.image(ruta_logo, w=60)
        pdf.ln(5)
    contenido = pdf.output(dest='S').encode('latin-1')
    return io.BytesIO(contenido)

# === VALIDACIÓN Y GENERACIÓN DE PDF + BOTONES MEJORADOS ===
if 'cantidad_total' in locals() and 'ruta_modelo_buzo' in locals() and 'fecha_entrega' in locals():
    if cantidad_total > 0 and ruta_modelo_buzo and fecha_entrega:
        pdf_buffer = generar_pdf(datos, ruta_logo_guardado, ruta_disenio_guardado, ruta_modelo_buzo)
        ruta_pdf_local = guardar_pdf_local(pdf_buffer)
        guardar_historial_excel(datos)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_buffer,
                file_name="cotizacion_buzos.pdf",
                mime="application/pdf"
            )

        with col2:
            mensaje_whatsapp = f"Hola, solicito cotización de buzos:\nModelo: {datos['Modelo']}\nTela: {datos['Tipo de tela']}\nTallas: {datos['Cantidad por tallas']}\nFecha deseada: {datos['Fecha deseada']}"
            url_whatsapp = f"https://wa.me/51920076432?text={mensaje_whatsapp.replace(' ', '%20')}"
            st.markdown(f"""
                <a href="{url_whatsapp}" target="_blank">
                    <button style="background-color:#25D366; color:white; padding:8px 16px; border:none; border-radius:5px; font-size:16px; cursor:pointer;">
                        📲 Enviar por WhatsApp
                    </button>
                </a>
            """, unsafe_allow_html=True)

        st.info("🚀 Próximamente: opción para subir automáticamente el PDF a la nube y enviar enlace por WhatsApp.")

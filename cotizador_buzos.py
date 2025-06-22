import streamlit as st
from fpdf import FPDF
from datetime import date
import io
import os
from PIL import Image
from datetime import datetime
import pandas as pd

CARPETA_UPLOADS = "uploads"

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
  
def obtener_ruta_modelo_seleccionado(modelo_nombre):
    if modelo_nombre.startswith("Producto"):
        numero = modelo_nombre.split(" ")[1]
        ruta = os.path.join("images", f"PRODUCTO {numero}.jpg")  # ✅ ruta relativa correcta
        return ruta if os.path.exists(ruta) else None
    return None


# CONFIGURACIÓN
st.set_page_config(page_title="Cotizador Buzos Deportivos", layout="centered")

# === PDF CLASS ===
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

    # Imagen del modelo seleccionado
    if ruta_modelo and os.path.exists(ruta_modelo):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Imagen del modelo seleccionado:", ln=True)
        pdf.ln(2)
        pdf.image(ruta_modelo, w=90)
        pdf.ln(5)

    # Imagen de referencia o diseño
    if ruta_disenio and os.path.exists(ruta_disenio):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Imagen de referencia o diseño:", ln=True)
        pdf.ln(2)
        pdf.image(ruta_disenio, w=90)
        pdf.ln(5)

    # Logo para bordado
    if ruta_logo and os.path.exists(ruta_logo):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Logo para bordado:", ln=True)
        pdf.ln(2)
        pdf.image(ruta_logo, w=60)
        pdf.ln(5)

    contenido = pdf.output(dest='S').encode('latin-1')
    return io.BytesIO(contenido)

RUTA_HISTORIAL = "historial_cotizaciones.xlsx"

def guardar_historial_excel(datos):
    # Convertir el diccionario a DataFrame de una fila
    df_nuevo = pd.DataFrame([datos])

    # Si el archivo no existe, lo crea con encabezado
    if not os.path.exists(RUTA_HISTORIAL):
        df_nuevo.to_excel(RUTA_HISTORIAL, index=False)
    else:
        # Si existe, lo abre y agrega nueva fila
        df_existente = pd.read_excel(RUTA_HISTORIAL)
        df_actualizado = pd.concat([df_existente, df_nuevo], ignore_index=True)
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
  
st.title("🧥 Cotización de Buzos Deportivos Personalizados")
st.markdown("""
Nos especializamos en la **confección personalizada de buzos deportivos** para equipos, empresas, colegios e instituciones.

🧵 Trabajamos 100% a medida con **materiales de calidad** (telas importadas y nacionales), con **acabados profesionales**, ideales para uso institucional.

Por favor, completa este formulario para brindarte una **cotización exacta**:
""")  

# === CATÁLOGO VISUAL ===
RUTA_IMAGENES = "C:/Users/hp/Desktop/Curso de PYTHON/cotizador_buzos/images/"
N_MODELOS = 39
MODELOS_POR_PAGINA = 9

if "modelo_seleccionado" not in st.session_state:
    st.session_state.modelo_seleccionado = "Producto 1"

mostrar_catalogo = st.checkbox("📂 Ver catálogo visual de modelos", value=False)

if mostrar_catalogo:
    st.subheader("📸 Catálogo de modelos de buzos deportivos")
    total_paginas = (N_MODELOS - 1) // MODELOS_POR_PAGINA + 1
    pagina = st.number_input("Página", min_value=1, max_value=total_paginas, value=1, step=1)

    inicio = (pagina - 1) * MODELOS_POR_PAGINA + 1
    fin = min(inicio + MODELOS_POR_PAGINA, N_MODELOS + 1)

    cols = st.columns(3)
    for idx, i in enumerate(range(inicio, fin)):
        ruta_imagen = os.path.join(RUTA_IMAGENES, f"PRODUCTO {i}.jpg")
        try:
            img = Image.open(ruta_imagen)
            with cols[idx % 3]:
                st.image(img, caption=f"Producto {i}", use_container_width=True)
                if st.button(f"Seleccionar Producto {i}", key=f"boton_{i}"):
                    st.session_state.modelo_seleccionado = f"Producto {i}"
                    st.success(f"✅ Modelo seleccionado: Producto {i}")
        except FileNotFoundError:
            st.warning(f"No se encontró la imagen: PRODUCTO {i}.jpg")

st.subheader("📌 ¿Qué modelo te interesa?")

# Lista con opción "Ninguno"
lista_modelos = ["Ninguno"] + [f"Producto {i}" for i in range(1, N_MODELOS + 1)]

# Proteger el índice actual
modelo_actual = st.session_state.get("modelo_seleccionado", "Ninguno")
if modelo_actual in lista_modelos:
    index_seleccionado = lista_modelos.index(modelo_actual)
else:
    index_seleccionado = 0  # Por defecto "Ninguno"

# Mostrar el selectbox
modelo_selectbox = st.selectbox(
    "Selecciona el modelo (o elige uno desde el catálogo visual)",
    lista_modelos,
    index=index_seleccionado
)

# Guardar modelo en el estado global
st.session_state.modelo_seleccionado = modelo_selectbox

st.markdown("¿No encuentras un modelo que se ajuste a tu necesidad?")
archivo_referencia = st.file_uploader("📤 Sube tu modelo o diseño personalizado", type=["jpg", "png", "pdf"])

# === FORMULARIO PRINCIPAL ===
tipo_prenda = st.text_input("1️⃣ ¿Qué deseas confeccionar?")

st.subheader("2️⃣ ¿Cantidad total por tallas?")
cols_tallas = st.columns(5)
cant_xs = cols_tallas[0].number_input("XS", min_value=0, step=1)
cant_s = cols_tallas[1].number_input("S", min_value=0, step=1)
cant_m = cols_tallas[2].number_input("M", min_value=0, step=1)
cant_l = cols_tallas[3].number_input("L", min_value=0, step=1)
cant_xl = cols_tallas[4].number_input("XL", min_value=0, step=1)
cantidad_por_talla = f"XS: {cant_xs}, S: {cant_s}, M: {cant_m}, L: {cant_l}, XL: {cant_xl}"

modelo = st.session_state.modelo_seleccionado

bordado = st.multiselect(
    "4️⃣ ¿Deseas bordado o estampado en alguna zona?",
    ["Pecho Derecho", "Pecho Izquierdo", "Espalda", "Pantalón", "No deseo"]
)
archivo_logo = st.file_uploader("Sube tu logo o diseño", type=["jpg", "png", "pdf", "ai", "eps"])

diseno_existente = st.radio("5️⃣ ¿Tienes un diseño?", ["Sí, lo subiré", "No, quiero que me ayuden"])
archivo_diseno = None
comentario_diseno = ""

if diseno_existente == "Sí, lo subiré":
    archivo_diseno = st.file_uploader("Sube tu diseño o referencia", type=["jpg", "png", "pdf"])
else:
    comentario_diseno = st.text_area("Describe lo que deseas que diseñemos:")

fecha_entrega = st.date_input("6️⃣ ¿Para cuándo lo necesitas?", min_value=date.today())

# === RESUMEN PARA PDF Y WHATSAPP ===
datos = {
    "Prenda": tipo_prenda,
    "Cantidad por tallas": cantidad_por_talla,
    "Modelo": modelo,
    "Bordado/Estampado": ", ".join(bordado),
    "Tiene diseño": diseno_existente,
    "Comentario diseño": comentario_diseno if diseno_existente == "No, quiero que me ayuden" else "Archivo subido",
    "Fecha deseada": fecha_entrega.strftime("%Y-%m-%d")
}

st.markdown("---")
if st.button("📄 Generar y descargar PDF"):
    # Guardar archivos subidos
    ruta_logo_guardado = guardar_archivo_local(archivo_logo, tipo="logo")
    ruta_disenio_guardado = guardar_archivo_local(archivo_diseno or archivo_referencia, tipo="diseno")

    # Obtener la ruta del modelo de buzo
    ruta_modelo_buzo = obtener_ruta_modelo_seleccionado(st.session_state.modelo_seleccionado)
    if st.session_state.modelo_seleccionado == "Ninguno":
        ruta_modelo_buzo = guardar_archivo_local(archivo_referencia, tipo="modelo") if archivo_referencia else None

    # Generar PDF
    pdf_buffer = generar_pdf(datos, ruta_logo_guardado, ruta_disenio_guardado, ruta_modelo_buzo)
    ruta_pdf_local = guardar_pdf_local(pdf_buffer)
    guardar_historial_excel(datos)

    # Botón de descarga
    st.download_button(
        label="📥 Descargar resumen en PDF",
        data=pdf_buffer,
        file_name="cotizacion_buzos.pdf",
        mime="application/pdf"
    )

# === WHATSAPP ===
if st.button("📲 Enviar por WhatsApp"):
    mensaje = f"""
¡Hola! Deseo una cotización:

🧥 Prenda: {tipo_prenda}
📦 Cantidades: {cantidad_por_talla}
🧍 Modelo: {modelo}
🎨 Bordado/Estampado: {', '.join(bordado)}
📅 Fecha deseada: {fecha_entrega}
{"📝 Nota: " + comentario_diseno if diseno_existente == "No, quiero que me ayuden" else ""}

Gracias, espero su respuesta. 🙌
"""
    mensaje_url = mensaje.replace("\n", "%0A").replace(" ", "%20")
    numero = "920076432"
    url_whatsapp = f"https://wa.me/{numero}?text={mensaje_url}"
    st.markdown(f"[👉 Enviar ahora por WhatsApp]({url_whatsapp})", unsafe_allow_html=True)

st.info("✅ Completa toda la información necesaria. Nosotros nos encargamos de darte la mejor cotización.")

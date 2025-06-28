import streamlit as st
from fpdf import FPDF
from datetime import date
import io
import os
from PIL import Image
from datetime import datetime
from PIL import UnidentifiedImageError
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
  
def obtener_ruta_modelo_seleccionado(modelo_nombre):
    if modelo_nombre.startswith("Producto"):
        numero = modelo_nombre.split(" ")[1]
        ruta = os.path.join("images", f"PRODUCTO {numero}.jpg")
        return ruta if os.path.exists(ruta) else None
    return None

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

# === CLASE PDF ===
class PDFCotizacion(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Resumen de Cotizaci\xf3n - Buzos Deportivos', ln=True, align='C')
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
        pdf.cell(0, 10, "Imagen de referencia o dise\xf1o:", ln=True)
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
    
# === INTERFAZ STREAMLIT ===
st.set_page_config(page_title="Cotizador Buzos Deportivos", layout="wide")
st.markdown("""
<div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
<img src="https://mi-servidor.com/logo_cinntex.png" style="width: 120px;">
    <div>
        <h2 style="margin-bottom: 5px;">SportWear Pro</h2>
        <p style="margin-top: 0; font-size: 16px; color: #ccc;">
            Confeccionamos prendas personalizadas de alta calidad para <strong>empresas, colegios y equipos deportivos</strong>.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("\U0001F9E5 Cotizaci\xf3n de Buzos Deportivos Personalizados")

st.markdown("""
Trabajamos prendas personalizadas con acabados profesionales.
Por favor, completa este formulario para brindarte una **cotizaci\xf3n exacta**:
""")

# CATÁLOGO VISUAL
if "modelo_seleccionado" not in st.session_state:
    st.session_state.modelo_seleccionado = "Ninguno"

st.markdown("📂 Ver catálogo visual de modelos")

def mostrar_catalogo(categoria, ruta_carpeta):
    st.subheader(f"📸 Catálogo - {categoria}")
    imagenes = sorted([img for img in os.listdir(ruta_carpeta) if img.endswith(('.jpg', '.png'))])
    cols = st.columns(3)
    for idx, img_nombre in enumerate(imagenes):
        ruta = os.path.join(ruta_carpeta, img_nombre)
        with cols[idx % 3]:
            st.image(ruta, caption=img_nombre.split('.')[0], use_container_width=True)
            if st.button(f"Seleccionar {categoria} - {img_nombre.split('.')[0]}", key=f"{categoria}_{img_nombre}"):
                st.session_state.modelo_seleccionado = f"{categoria} - {img_nombre.split('.')[0]}"

# Mostrar catálogos de ambas categorías
mostrar_catalogo("Buzos Deportivos", "images/Buzos Deportivos")
mostrar_catalogo("Buzos Escolares", "images/Buzos Escolares")

# Subida de imagen personalizada (si no encuentra modelo en el catálogo)
st.markdown("¿No encuentras un modelo que se ajuste a tu necesidad?")
archivo_referencia = st.file_uploader("📤 Sube tu modelo o diseño personalizado", type=["jpg", "png", "pdf"])

# === FORMULARIO PRINCIPAL ===
st.subheader("1. Selecciona el tipo de tela o material")

tipo_tela = st.selectbox("Tipo de tela disponible:", [
    "Microwalon",
    "Microprince",
    "Microsatin",
    "Nova",
    "Gamberra",
    "Sport Licra",
    "Polinan",
    "Interfil"
])

st.subheader("2. Cantidad por tallas")
cols_tallas = st.columns(5)
cantidades = {
    "XS": cols_tallas[0].number_input("XS", min_value=0, step=1),
    "S": cols_tallas[1].number_input("S", min_value=0, step=1),
    "M": cols_tallas[2].number_input("M", min_value=0, step=1),
    "L": cols_tallas[3].number_input("L", min_value=0, step=1),
    "XL": cols_tallas[4].number_input("XL", min_value=0, step=1),
}
cantidad_total = sum(cantidades.values())
st.markdown(f"🧮 **Total de prendas:** {cantidad_total}")
bordado = st.multiselect("3. \xbfDeseas bordado o estampado?", ["Pecho Derecho", "Pecho Izquierdo", "Espalda", "Pantal\xf3n", "No deseo"])
archivo_logo = st.file_uploader("Sube tu logo o dise\xf1o", type=["jpg", "png", "pdf"])

diseno_existente = st.radio("4. \xbfTienes un dise\xf1o?", ["S\xed, lo subir\xe9", "No, quiero que me ayuden"])
archivo_diseno = None
comentario_diseno = ""
if diseno_existente == "S\xed, lo subir\xe9":
    archivo_diseno = st.file_uploader("Sube tu dise\xf1o o referencia", type=["jpg", "png", "pdf"])
else:
    comentario_diseno = st.text_area("Describe lo que deseas que dise\xf1emos:")

fecha_entrega = st.date_input("5. Fecha de entrega", min_value=date.today())

# === DATOS PARA PDF ===
datos = {
    "Tipo de tela": tipo_tela,
    "Cantidad por tallas": str(cantidades),
    "Modelo": st.session_state.modelo_seleccionado,
    "Bordado/Estampado": ", ".join(bordado),
    "Tiene dise\xf1o": diseno_existente,
    "Comentario dise\xf1o": comentario_diseno if diseno_existente == "No, quiero que me ayuden" else "Archivo subido",
    "Fecha deseada": fecha_entrega.strftime("%Y-%m-%d")
}

# === VISTA PREVIA ===
st.markdown("---")
st.subheader("\U0001F4DE Vista previa del pedido")

ruta_logo_guardado = guardar_archivo_local(archivo_logo, tipo="logo")
ruta_disenio_guardado = guardar_archivo_local(archivo_diseno or archivo_referencia, tipo="diseno")
ruta_modelo_buzo = obtener_ruta_modelo_seleccionado(st.session_state.modelo_seleccionado)
if st.session_state.modelo_seleccionado == "Ninguno":
    ruta_modelo_buzo = guardar_archivo_local(archivo_referencia, tipo="modelo") if archivo_referencia else None
    
try:
    if ruta_modelo_buzo and os.path.exists(ruta_modelo_buzo):
        st.image(ruta_modelo_buzo, caption="Modelo seleccionado", width=250)
    elif ruta_disenio_guardado and os.path.exists(ruta_disenio_guardado):
        st.image(ruta_disenio_guardado, caption="Imagen de referencia", width=250)
    elif archivo_referencia is not None:
        st.image(archivo_referencia, caption="Imagen subida", width=250)
    else:
        st.warning("No se ha seleccionado ningún modelo ni imagen de referencia.")
except UnidentifiedImageError:
    st.error("⚠️ No se pudo cargar la imagen. Verifica que el archivo subido sea una imagen válida (JPG, PNG).")

st.write("### Detalles del pedido:")
for k, v in datos.items():
    st.write(f"**{k}:** {v}")

if ruta_logo_guardado and os.path.exists(ruta_logo_guardado):
    st.image(ruta_logo_guardado, caption="Logo subido", width=150)
if ruta_disenio_guardado and os.path.exists(ruta_disenio_guardado):
    st.image(ruta_disenio_guardado, caption="Dise\xf1o / Imagen de referencia", width=150)

st.info("✅ Verifica todos los datos antes de continuar.")

# === VALIDACIÓN Y GENERACIÓN DE PDF + BOTONES MEJORADOS ===
st.markdown("---")
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

    # === WHATSAPP ===
mensaje = f"""
¡Hola! Deseo una cotización:

🧥 Tipo de tela: {tipo_tela}
📦 Cantidades: {cantidad_total}
📌 Modelo: {st.session_state.modelo_seleccionado}
🎯 Bordado/Estampado: {', '.join(bordado)}
📅 Fecha deseada: {fecha_entrega}
{f'📝 Nota: {comentario_diseno}' if diseno_existente == "No, quiero que me ayuden" else ''}
"""
mensaje_url = mensaje.replace("\n", "%0A").replace(" ", "%20")
numero = "920076432"
url_whatsapp = f"https://wa.me/{numero}?text={mensaje_url}"

st.markdown(
    f"""
    <a href="{url_whatsapp}" target="_blank" style="text-decoration: none;">
        <button style="background-color: #25D366; color: white; padding: 10px 20px;
                       border: none; border-radius: 5px; font-size: 16px;">
            📲 Enviar por WhatsApp
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

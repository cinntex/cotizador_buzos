# Asegúrate de tener instalada la librería streamlit
# pip install streamlit fpdf

import streamlit as st
from fpdf import FPDF
import tempfile
import urllib.parse
import os

# --- Configuración de página ---
st.set_page_config(page_title="Cotizador de Buzos Deportivos", page_icon="🧥", layout="wide")

# --- Inicializar estado ---
if "modelo_seleccionado" not in st.session_state:
    st.session_state.modelo_seleccionado = None

# --- Logo y título personalizado ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=200)

st.markdown("""
<div style='text-align: center;'>
    <h1 style='color: #0A6EBD;'>Cotizador de Buzos y Casacas Deportivas</h1>
    <p style='color: #555;'>Confeccionamos prendas personalizadas de alta calidad para empresas, colegios y equipos deportivos</p>
    <hr style='border: 1px solid #ccc;' />
</div>
""", unsafe_allow_html=True)

# --- Datos base ---
precios = {
    "tela": 11.0,
    "forro": 4.5,
    "patronaje": 55.0,
    "confeccion": 18.0,
    "corte": 45.0 / 12,
    "accesorios": 3.0,
    "bordado": 4.0,
    "ponchado": 10.0,
    "utilidad": 17.0
}

# --- Modelos ---
modelos = [
    {"nombre": "Buzo Clásico Recto", "imagen": "buzo_clasico.png", "descripcion": "Modelo cómodo y versátil para uso diario o escolar."},
    {"nombre": "Casaca con Capucha y Cortes", "imagen": "casaca_cortes.png", "descripcion": "Ideal para equipos deportivos, con diseño moderno."},
    {"nombre": "Chaqueta Elegante Cuello Alto", "imagen": "chaqueta_elegante.png", "descripcion": "Perfecta para uso empresarial o representativo."},
    {"nombre": "Casaca Impermeable con Capucha", "imagen": "casaca_impermeable.png", "descripcion": "Resistente al agua, ideal para actividades al aire libre."}
]

# --- Mostrar catálogo ---
cols = st.columns(4)
for i, modelo in enumerate(modelos):
    with cols[i]:
        st.image(modelo["imagen"], use_container_width=True)
        st.subheader(modelo["nombre"])
        st.caption(modelo["descripcion"])
        if st.button("Cotizar", key=f"cotizar_{i}"):
            st.session_state.modelo_seleccionado = modelo["nombre"]

# --- Si se selecciona un modelo ---
if st.session_state.modelo_seleccionado:
    st.markdown("---")
    st.subheader(f"📝 Personalizar pedido para: {st.session_state.modelo_seleccionado}")

    tipo = st.selectbox("Tipo de conjunto:", ["Conjunto completo (casaca + pantalón)", "Solo casaca"])
    col1, col2, col3, col4, col5 = st.columns(5)
    xs = col1.number_input("XS", min_value=0, step=1)
    s = col2.number_input("S", min_value=0, step=1)
    m = col3.number_input("M", min_value=0, step=1)
    l = col4.number_input("L", min_value=0, step=1)
    xl = col5.number_input("XL", min_value=0, step=1)
    total = xs + s + m + l + xl

    if total > 0:
        st.info(f"🧾 Total de prendas seleccionadas: {total}")

    color = st.color_picker("🎨 Selecciona el color principal")
    logo = st.file_uploader("📎 Sube tu logo o escudo", type=["png", "jpg", "jpeg"])
    comentario = st.text_area("🗒 Comentarios adicionales", placeholder="Ej. agregar nombre, colores secundarios...")

    # --- Cálculo de costos ---
    if total > 0:
        metros_tela = total * 2.7
        metros_forro = total * 1.0

        costo_tela = metros_tela * precios["tela"]
        costo_forro = metros_forro * precios["forro"]
        tallas_usadas = sum([1 for t in [xs, s, m, l, xl] if t > 0])
        patronaje = tallas_usadas * precios["patronaje"]
        confeccion = total * precios["confeccion"]
        corte = total * precios["corte"]
        accesorios = total * precios["accesorios"]
        bordado = total * precios["bordado"]
        ponchado = precios["ponchado"] if logo else 0

        costo_total = sum([costo_tela, costo_forro, patronaje, confeccion, corte, accesorios, bordado, ponchado])
        precio_sugerido = (costo_total + (precios["utilidad"] * total)) / total

        st.success(f"💰 Precio sugerido por conjunto: S/ {precio_sugerido:.2f}")
        st.info(f"📦 Costo total estimado: S/ {costo_total:.2f} por {total} prendas")

        # PDF
        def generar_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "Cotización de Conjuntos Deportivos - CINNTEX", ln=True, align='C')
            pdf.set_font("Arial", "", 12)
            pdf.ln(10)
            pdf.cell(200, 8, f"Modelo: {st.session_state.modelo_seleccionado}", ln=True)
            pdf.cell(200, 8, f"Tipo: {tipo}", ln=True)
            pdf.cell(200, 8, f"Tallas: XS({xs}), S({s}), M({m}), L({l}), XL({xl})", ln=True)
            pdf.cell(200, 8, f"Color: {color}", ln=True)
            pdf.cell(200, 8, f"Comentarios: {comentario}", ln=True)
            pdf.ln(10)
            pdf.cell(200, 10, f"Precio sugerido por conjunto: S/ {precio_sugerido:.2f}", ln=True)
            pdf.cell(200, 10, f"Costo total estimado: S/ {costo_total:.2f}", ln=True)
            if logo is not None:
                logo_path = os.path.join(tempfile.gettempdir(), logo.name)
                with open(logo_path, "wb") as f:
                    f.write(logo.read())
                try:
                    pdf.image(logo_path, x=10, y=pdf.get_y() + 10, w=60)
                except:
                    pass
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf.output(temp_path.name)
            return temp_path.name

        ruta_pdf = generar_pdf()
        with open(ruta_pdf, "rb") as f:
            st.download_button("📄 Descargar cotización en PDF", f, file_name="cotizacion_cinntex.pdf")

        # WhatsApp
        numero = "5194611230"
        mensaje = f"Hola, soy un cliente interesado en confección personalizada.\n\n"
        mensaje += f"🧥 Modelo: {st.session_state.modelo_seleccionado}\n"
        mensaje += f"👕 Tipo: {tipo}\n📏 Tallas: XS({xs}), S({s}), M({m}), L({l}), XL({xl})\n"
        mensaje += f"🎨 Color principal: {color}\n"
        mensaje += f"📌 Comentarios: {comentario}\n"
        mensaje += f"💰 Precio estimado por conjunto: S/ {precio_sugerido:.2f}\n"
        mensaje += f"📄 Ya generé mi cotización en PDF desde la app."
        url = f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"
        st.markdown(f"[💬 Enviar este pedido por WhatsApp]({url})", unsafe_allow_html=True)
    else:
        st.warning("Por favor ingresa al menos una prenda para cotizar.")

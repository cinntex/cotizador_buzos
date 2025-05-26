import streamlit as st
from fpdf import FPDF
import tempfile
import urllib.parse

# --- Configuración de página ---
st.set_page_config(
    page_title="Cotizador Cinntex",
    page_icon="🧥",
    layout="centered"
)

# --- Logo centrado ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=200)


st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #0A6EBD;'>Cotizador de Buzos y Casacas</h1>
        <p style='color: #555;'>Confeccionamos prendas personalizadas de alta calidad para empresas, colegios y equipos deportivos</p>
        <hr style='border: 1px solid #ccc;' />
    </div>
""", unsafe_allow_html=True)

# --- Opciones de productos ---
st.header("🧵 Tipo de prenda")
tipo_conjunto = st.selectbox("Selecciona:", [
    "Conjunto completo (casaca + pantalón)", "Solo casaca"
])

modelo = st.selectbox("Modelo base:", [
    "Casaca clásica con cuello alto",
    "Casaca con capucha y cortes laterales",
    "Chaqueta elegante informal cuello alto",
    "Casacas impermeables con capucha",
    "Buzo clásico recto",
    "Buzo con puño y corte lateral"
])

# --- Tallas ---
st.header("📏 Cantidad por talla")
col1, col2, col3, col4, col5 = st.columns(5)
talla_xs = col1.number_input("XS", min_value=0, step=1, value=0)
talla_s = col2.number_input("S", min_value=0, step=1, value=0)
talla_m = col3.number_input("M", min_value=0, step=1, value=0)
talla_l = col4.number_input("L", min_value=0, step=1, value=0)
talla_xl = col5.number_input("XL", min_value=0, step=1, value=0)

# --- Personalizaciones ---
st.header("🎨 Personalización")
color_libre = st.checkbox("Color libre")
bordado_logo = st.checkbox("Logo bordado")
bordado_nombre = st.checkbox("Nombre bordado")

# --- Precios base ---
precio_tela_metro = 11.00
precio_forro_metro = 4.50
patronaje_por_talla = 55.00
confeccion_por_conjunto = 18.00
corte_por_docena = 45.00 / 12
cierres_y_cordones = 3.00
bordado_precio = 4.00
ponchado_logo = 10.00
utilidad_deseada = 17.00

# --- Función para PDF ---
def generar_pdf(datos, precio_unitario, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Cotización de Conjuntos Deportivos - CINNTEX", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    for linea in datos:
        pdf.cell(200, 8, txt=linea, ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, f"Precio sugerido por conjunto: S/ {precio_unitario:.2f}", ln=True)
    pdf.cell(200, 10, f"Costo total estimado: S/ {total:.2f}", ln=True)
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_path.name)
    return temp_path.name

# --- Cálculo ---
total_conjuntos = talla_xs + talla_s + talla_m + talla_l + talla_xl

if total_conjuntos > 0:
    metros_tela = total_conjuntos * 2.7
    metros_forro = total_conjuntos * 1.0

    costo_tela = metros_tela * precio_tela_metro
    costo_forro = metros_forro * precio_forro_metro
    costo_patronaje = len([x for x in [talla_xs, talla_s, talla_m, talla_l, talla_xl] if x > 0]) * patronaje_por_talla
    costo_confeccion = total_conjuntos * confeccion_por_conjunto
    costo_corte = total_conjuntos * corte_por_docena
    costo_accesorios = total_conjuntos * cierres_y_cordones
    costo_bordado = total_conjuntos * bordado_precio if (bordado_logo or bordado_nombre) else 0
    costo_ponchado = ponchado_logo if bordado_logo else 0

    costo_total = (
        costo_tela + costo_forro + costo_patronaje + costo_confeccion +
        costo_corte + costo_accesorios + costo_bordado + costo_ponchado
    )

    precio_sugerido = (costo_total + utilidad_deseada * total_conjuntos) / total_conjuntos

    # --- Mostrar resultados ---
    st.success(f"👉 Total de conjuntos: {int(total_conjuntos)}")
    st.info(f"📦 Costo total estimado: S/ {costo_total:.2f}")
    st.success(f"💵 Precio sugerido por conjunto: S/ {precio_sugerido:.2f}")

    resumen = [
        f"Tipo de conjunto: {tipo_conjunto}",
        f"Modelo: {modelo}",
        f"Tallas: XS({talla_xs}), S({talla_s}), M({talla_m}), L({talla_l}), XL({talla_xl})",
        "Personalización: " + ", ".join([
            opt for opt, checked in {
                "Color libre": color_libre,
                "Logo bordado": bordado_logo,
                "Nombre bordado": bordado_nombre
            }.items() if checked
        ]),
        f"Cantidad total: {int(total_conjuntos)}"
    ]

    ruta_pdf = generar_pdf(resumen, precio_sugerido, costo_total)
    with open(ruta_pdf, "rb") as f:
        st.download_button("📄 Descargar cotización en PDF", f, file_name="cotizacion_cinntex.pdf")

    # --- WhatsApp ---
    st.markdown("### 📲 ¿Deseas recibir esta cotización por WhatsApp?")
    numero_whatsapp = "5194611230"
    mensaje = f"""Hola, estoy interesado en el conjunto deportivo:
- Tipo: {tipo_conjunto}
- Modelo: {modelo}
- Tallas: XS({talla_xs}), S({talla_s}), M({talla_m}), L({talla_l}), XL({talla_xl})
¿Podrías ayudarme con más detalles?"""
    mensaje_url = urllib.parse.quote(mensaje)
    enlace_whatsapp = f"https://wa.me/{numero_whatsapp}?text={mensaje_url}"
    st.markdown(f"[💬 Enviar mensaje por WhatsApp]({enlace_whatsapp})", unsafe_allow_html=True)

else:
    st.warning("Por favor ingresa al menos una prenda para cotizar.")

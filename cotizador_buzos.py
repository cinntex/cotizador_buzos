from fpdf import FPDF
import tempfile
import streamlit as st
import urllib.parse
import csv
from datetime import datetime
import os

# --- Configuración inicial ---
st.set_page_config(page_title="Cotizador de Buzos y Casacas", layout="centered")
st.title("🧥 Cotizador de Buzos y Casacas Deportivas")

# --- Opciones de productos ---
tipo_conjunto = st.selectbox("Tipo de conjunto:", [
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
st.subheader("Cantidad por talla:")
talla_xs = st.number_input("XS", min_value=0, step=1, value=0)
talla_s = st.number_input("S", min_value=0, step=1, value=0)
talla_m = st.number_input("M", min_value=0, step=1, value=0)
talla_l = st.number_input("L", min_value=0, step=1, value=0)
talla_xl = st.number_input("XL", min_value=0, step=1, value=0)

# --- Personalizaciones ---
st.subheader("Personalización:")
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

# --- Función para generar PDF ---
def generar_pdf(datos, precio_unitario, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Cotización de Conjuntos Deportivos", ln=True, align='C')
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

# --- Función para guardar historial ---
def guardar_historial(resumen, precio_unitario, total):
    archivo = "historial_cotizaciones.csv"
    encabezado = ["Fecha", "Tipo", "Modelo", "Tallas", "Personalización", "Cantidad", "Precio Unitario", "Costo Total"]
    datos = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tipo_conjunto,
        modelo,
        f"XS({talla_xs}), S({talla_s}), M({talla_m}), L({talla_l}), XL({talla_xl})",
        f"{'Color libre' if color_libre else ''} {'Logo bordado' if bordado_logo else ''} {'Nombre bordado' if bordado_nombre else ''}",
        int(total_conjuntos),
        f"{precio_unitario:.2f}",
        f"{total:.2f}"
    ]
    existe = os.path.isfile(archivo)
    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(encabezado)
        writer.writerow(datos)

# --- Cálculo ---
total_conjuntos = talla_xs + talla_s + talla_m + talla_l + talla_xl

if total_conjuntos > 0:
    # Cálculos
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

    # Mostrar resultados
    st.success(f"👉 Total de conjuntos: {int(total_conjuntos)}")
    st.info(f"📦 Costo total estimado: S/ {costo_total:.2f}")
    st.success(f"💵 Precio sugerido por conjunto: S/ {precio_sugerido:.2f}")

    # Resumen PDF
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

    # Generar PDF
    ruta_pdf = generar_pdf(resumen, precio_sugerido, costo_total)

    # Botón para descargar PDF
    with open(ruta_pdf, "rb") as f:
        st.download_button("📄 Descargar cotización en PDF", f, file_name="cotizacion.pdf")

    # Guardar historial CSV
    guardar_historial(resumen, precio_sugerido, costo_total)

    # Botón WhatsApp
    st.markdown("### 📲 ¿Deseas recibir esta cotización por WhatsApp?")
    numero_whatsapp = "51946161230"  # <-- Reemplaza por el tuyo
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

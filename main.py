import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from fpdf import FPDF

# Ahora el código buscará la llave en los "Secrets" de la web, no aquí
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)


def leer_pdf(file):
    reader = PdfReader(file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto


def crear_pdf(texto, titulo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=titulo, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)

    # Esta línea es la que arregla el error de internet:
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')

    pdf.multi_cell(0, 10, txt=texto_limpio)

    # Cambiamos esto para que no dé el error de 'bytearray'
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    return pdf_output


# --- DISEÑO THE TEACHER ---
st.set_page_config(page_title="THE TEACHER", page_icon="👨‍🏫", layout="centered")

st.title("👨‍🏫 THE TEACHER")
st.markdown("### El asistente definitivo para tus exámenes")
st.write("---")

# 1. SELECTOR PRINCIPAL (Ahora en el centro y bien visible)
st.write("#### 1️⃣ Elige qué quieres que haga THE TEACHER:")
modo = st.selectbox(
    "Selecciona una opción:",
    ["Resumen Detallado + Preguntas", "Esquema Visual Pro", "Traducción Profesional (MODO PREMIUM)"]
)

if modo == "Traducción Profesional (MODO PREMIUM)":
    st.warning("💎 Esta función suele ser de pago, ¡pruébala gratis en la Beta!")
    idioma = st.text_input("¿A qué idioma quieres traducir? (Ej: Inglés, Alemán, Chino...)", "Inglés")

st.write("---")

# 2. SUBIDA DE ARCHIVO
st.write("#### 2️⃣ Sube tus apuntes:")
archivo = st.file_uploader("", type="pdf")

if archivo is not None:
    if st.button(f"🚀 GENERAR {modo.upper()}"):
        with st.spinner("👨‍🏫 THE TEACHER está trabajando..."):
            try:
                texto_base = leer_pdf(archivo)
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])

                # --- LÓGICA DE PROMPT MEJORADA ---
            if "Resumen" in modo:
                instrucciones = "Haz un resumen detallado, limpio y fácil de leer. Usa negritas y puntos de lista. Al final añade 5 preguntas de examen con respuestas."
            elif "Esquema" in modo:
                instrucciones = "Crea un esquema jerárquico visualmente claro usando puntos de lista y sangrías. Evita códigos raros o flechas complejas. Que sea ideal para estudiar de un vistazo."
                else:
                    instrucciones = f"Traduce fielmente estos apuntes al idioma {idioma} manteniendo el rigor académico."

                prompt = f"Eres THE TEACHER. {instrucciones}. Aquí están los apuntes: {texto_base[:12000]}"

                response = model.generate_content(prompt)
                resultado = response.text

                # --- VISUALIZACIÓN DIRECTA (Sin clics extra) ---
                st.success("✅ ¡Trabajo terminado!")
                st.markdown("---")
                st.markdown(resultado)

                # --- BOTÓN DE DESCARGA ---
                pdf_bytes = crear_pdf(resultado, f"THE TEACHER - {modo}")
                st.download_button(
                    label="📥 DESCARGAR EN PDF",
                    data=pdf_bytes,
                    file_name=f"TheTeacher_{modo.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Se ha producido un error: {e}")

# Pie de página profesional
st.write("---")
st.caption("© 2024 THE TEACHER - No guardamos tus archivos. Privacidad 100% garantizada.")
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURACIÓN DE LA IA ---
# Sacamos la llave de los Secrets de Streamlit
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Nombre del modelo limpio (sin 'models/') para evitar el error 404
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Falta la GOOGLE_API_KEY en los Secrets.")
    st.stop()

# --- FUNCIONES DE APOYO ---
def leer_pdf(file):
    reader = PdfReader(file)
    texto = ""
    for page in reader.pages:
        texto_pag = page.extract_text()
        if texto_pag:
            texto += texto_pag
    return texto

def crear_pdf(texto, titulo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=titulo, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    # Limpieza para evitar errores de caracteres extraños
    texto_limpio = texto.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    return pdf.output(dest='S').encode('latin-1')

# --- DISEÑO DE LA INTERFAZ ---
st.set_page_config(page_title="THE TEACHER", page_icon="👨‍🏫")

st.title("👨‍🏫 THE TEACHER")
st.markdown("### El asistente definitivo para tus exámenes")
st.write("---")

# 1. Selector de modo
st.write("#### 1️⃣ Elige qué quieres que haga THE TEACHER:")
modo = st.selectbox(
    "Selecciona una opción:",
    ["Resumen Detallado + Preguntas", "Esquema Visual Pro", "Traducción Profesional"]
)

idioma = ""
if modo == "Traducción Profesional":
    idioma = st.text_input("¿A qué idioma quieres traducir?", "Inglés")

st.write("---")

# 2. Subida de archivo
st.write("#### 2️⃣ Sube tus apuntes:")
archivo = st.file_uploader("Sube un archivo PDF", type="pdf")

if archivo is not None:
    if st.button(f"🚀 GENERAR {modo.upper()}"):
        with st.spinner("🧠 THE TEACHER está trabajando..."):
            try:
                texto_base = leer_pdf(archivo)
                
                # Definir instrucciones según el modo
                if "Resumen" in modo:
                    instrucciones = "Haz un resumen detallado y añade 5 preguntas de examen con respuestas al final."
                elif "Esquema" in modo:
                    instrucciones = "Crea un esquema jerárquico claro usando puntos de lista y sangrías."
                else:
                    instrucciones = f"Traduce fielmente estos apuntes al idioma {idioma}."

                prompt = f"Actúa como un profesor experto. {instrucciones}. Aquí el texto: {texto_base[:15000]}"

                # Llamada a la IA
                response = model.generate_content(prompt)
                resultado = response.text

                # Mostrar resultado en pantalla
                st.success("✅ ¡Trabajo terminado!")
                st.markdown("### ✨ Resultado:")
                st.write(resultado)

                # Generar y ofrecer descarga
                pdf_bytes = crear_pdf(resultado, f"THE TEACHER - {modo}")
                st.download_button(
                    label="📥 Descargar en PDF",
                    data=pdf_bytes,
                    file_name=f"TheTeacher_{modo.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Hubo un error con la IA: {e}")

# Pie de página
st.write("---")
st.caption("© 2026 THE TEACHER - Privacidad garantizada.")
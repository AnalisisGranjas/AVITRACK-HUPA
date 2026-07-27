import base64
import os
import streamlit as st

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="HUPA | Inducción Técnica",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- FUNCIONALIDAD: CARGAR LOGO Y CONVERTIR A BASE64 ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None


logo_path = os.path.join("DATA", "logo hupa.png")
logo_b64 = get_image_base64(logo_path)

logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}"'
    ' style="height: 65px; margin-right: 20px; border-radius: 8px; object-fit:'
    ' contain;">'
    if logo_b64
    else ""
)

# --- 2. VALIDACIÓN DE SESIÓN ---
if "auth" not in st.session_state or not st.session_state.auth:
    st.switch_page("app.py")
    st.stop()

# --- 3. CSS ADAPTATIVO AGROTECH EXECUTIVE (CLARO / OSCURO) ---
st.markdown(
    """
    <style>
    /* Mantener visible la barra de navegación de Streamlit */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* BANNER CABECERA PRINCIPAL */
    .app-header {
        background: linear-gradient(135deg, #0F5132 0%, #117A65 100%);
        padding: 22px 30px;
        border-radius: 16px;
        color: #FFFFFF !important;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(15, 81, 50, 0.25);
        display: flex;
        align-items: center;
    }
    .app-header-text h1 {
        color: #FFFFFF !important;
        font-size: clamp(1.4rem, 2.5vw, 1.9rem) !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .app-header-text p {
        color: #E8F8F5 !important;
        margin: 4px 0 0 0 !important;
        font-size: clamp(0.85rem, 1.5vw, 1rem) !important;
        opacity: 0.95;
    }

    /* CONTENEDOR FLEXIBLE DE TARJETAS */
    .flex-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        align-items: stretch;
    }

    /* TARJETAS CLÍNICAS PREMIUM */
    .info-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 26px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
        flex: 1 1 45%; 
        min-width: 300px;
        color: var(--text-color);
        display: flex;
        flex-direction: column;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
    }

    .info-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    }

    /* TIRA DE COLOR SUPERIOR POR ÁREA */
    .card-mortalidad::before { content: ""; position: absolute; top:0; left:0; right:0; height: 5px; background: #C0392B; }
    .card-alimento::before { content: ""; position: absolute; top:0; left:0; right:0; height: 5px; background: #D97706; }
    .card-postura::before { content: ""; position: absolute; top:0; left:0; right:0; height: 5px; background: #117A65; }
    .card-bitacora::before { content: ""; position: absolute; top:0; left:0; right:0; height: 5px; background: #2980B9; }

    .info-card h3 {
        color: var(--text-color) !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(128,128,128,0.15);
        padding-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .info-card p, .info-card li {
        font-size: 0.95rem !important;
        line-height: 1.6;
        margin-bottom: 10px;
        opacity: 0.9;
    }

    .highlight-red { color: #C0392B; font-weight: 700; }
    .highlight-amber { color: #D97706; font-weight: 700; }
    .highlight-green { color: #117A65; font-weight: 700; }
    .highlight-blue { color: #2980B9; font-weight: 700; }

    /* BOTÓN DE ACCIÓN GIGANTE AGROTECH */
    div.stButton > button {
        width: 100%;
        height: 65px !important;
        font-size: 1.2rem !important;
        background: linear-gradient(135deg, #0F5132 0%, #117A65 100%) !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        border: none !important;
        margin-top: 25px;
        box-shadow: 0 8px 20px rgba(15, 81, 50, 0.25) !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.03em;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(15, 81, 50, 0.35) !important;
        background: linear-gradient(135deg, #117A65 0%, #16A085 100%) !important;
    }

    /* MEDIA QUERIES */
    @media (max-width: 768px) {
        .app-header {
            flex-direction: column;
            text-align: center;
            padding: 18px;
        }
        .app-header img {
            margin-right: 0 !important;
            margin-bottom: 12px;
        }
        .info-card {
            flex: 1 1 100%;
            padding: 18px;
        }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 4. CONTENIDO TÉCNICO INTEGRAL ---

# BANNER CABECERA DE BIENVENIDA
st.markdown(
    f"""
    <div class="app-header">
        {logo_html}
        <div class="app-header-text">
            <h1>Centro de Inteligencia Clínica HUPA</h1>
            <p>Especialista a cargo: <b>{st.session_state.user}</b></p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="flex-grid">', unsafe_allow_html=True)

# TARJETA 1: MORTALIDAD
st.markdown(
    """
    <div class="info-card card-mortalidad">
        <h3>🔬 Vigilancia Epidemiológica</h3>
        <p>La mortalidad es el indicador final de la salud del lote. Aquí diferenciamos dos tipos de eventos críticos:</p>
        <ul>
            <li><span class="highlight-red">Mortalidad Súbita:</span> Aves que mueren de forma imprevista. Un aumento indica una <b>alerta roja</b> de posibles brotes infecciosos o fallas ambientales.</li>
            <li><span class="highlight-red">Descarte Técnico:</span> Selección activa de aves débiles. Una buena selección previene contagios y optimiza el alimento.</li>
        </ul>
        <p><i><b>Objetivo:</b> Mantener la curva de mortalidad dentro de los estándares genéticos.</i></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# TARJETA 2: ALIMENTO
st.markdown(
    """
    <div class="info-card card-alimento">
        <h3>🧬 Sensor Temprano: El Alimento</h3>
        <p>El <span class="highlight-amber">Consumo (g/ave/día)</span> es el termómetro más rápido. Las aves dejan de comer entre 24 y 48 horas antes de que se caiga la postura o incremente la mortalidad.</p>
        <p>Si detecta una caída en el gramaje, revise inmediatamente la <b>calidad del agua</b>, la temperatura del galpón o posibles inicios de cuadros febriles en el lote.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# TARJETA 3: POSTURA
st.markdown(
    """
    <div class="info-card card-postura">
        <h3>📊 Eficiencia y Edad Biológica</h3>
        <p>El <span class="highlight-green">% de Postura</span> mide la conversión de alimento en huevo. Este dato siempre se analiza bajo la <b>Edad de las Aves (Semanas)</b>.</p>
        <p>Comparamos el rendimiento real contra la "Curva Guía" de la línea genética para verificar si el lote expresa su máximo potencial productivo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# TARJETA 4: BITÁCORA
st.markdown(
    """
    <div class="info-card card-bitacora">
        <h3>📝 Bitácora de Campo</h3>
        <p>Los datos dicen <b>qué</b> pasó; la bitácora dice <b>por qué</b>. Buscamos eventos externos que alteren el comportamiento:</p>
        <ul>
            <li>Ruidos estresantes o presencia de depredadores.</li>
            <li>Fallas en el suministro de agua o energía eléctrica.</li>
            <li>Cambios de manejo por parte del personal de galpón.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# BOTÓN FINAL DE ACCIÓN GIGANTE
if st.button(
    f"🚀 INICIAR DIAGNÓSTICO TÉCNICO PARA {st.session_state.user.upper()}"
):
    st.switch_page("pages/02_Bitacora_Diaria.py")
import streamlit as st

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="HUPA | Inducción Técnica", layout="wide")

# --- 2. VALIDACIÓN DE SESIÓN ---
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("app.py")
    st.stop()

# --- 3. CSS ADAPTATIVO PROFESIONAL (COLOR ÚNICO HUPA) ---
st.markdown(f"""
    <style>
    /* Variables dinámicas de Streamlit */
    .stApp {{
        background-color: var(--background-color);
    }}

    .main-container {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }}

    /* Contenedor flexible para Tablet/Móvil */
    .flex-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        align-items: stretch;
    }}

    /* Tarjetas Clínicas */
    .info-card {{
        background-color: var(--secondary-background-color);
        padding: 30px;
        border-radius: 20px;
        border-top: 6px solid #FFD700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        flex: 1 1 45%; 
        min-width: 320px;
        color: var(--text-color);
        display: flex;
        flex-direction: column;
    }}

    .info-card h3 {{
        color: #FFD700 !important;
        font-size: 24px !important;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(128,128,128,0.2);
        padding-bottom: 10px;
    }}

    .info-card p, .info-card li {{
        font-size: 16px !important;
        line-height: 1.6;
        margin-bottom: 12px;
    }}

    .highlight {{
        color: #FFD700;
        font-weight: bold;
    }}

    /* Botón de Acción Gigante */
    div.stButton > button {{
        width: 100%;
        height: 75px !important;
        font-size: 22px !important;
        background-color: #FFD700 !important;
        color: #000000 !important;
        border-radius: 18px !important;
        font-weight: bold;
        border: none !important;
        margin-top: 25px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONTENIDO TÉCNICO INTEGRAL ---

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>🩺 Centro de Inteligencia Clínica HUPA</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 18px;'>Especialista: <b>{st.session_state.user}</b></p>", unsafe_allow_html=True)

st.markdown('<div class="flex-grid">', unsafe_allow_html=True)

# TARJETA 1: MORTALIDAD
st.markdown(f"""
    <div class="info-card">
        <h3>🔬 Vigilancia Epidemiológica</h3>
        <p>La mortalidad es el indicador final de la salud del lote. Aquí diferenciamos dos tipos de eventos críticos:</p>
        <ul>
            <li><span class="highlight">Mortalidad Súbita:</span> Aves que mueren de forma imprevista. Un aumento aquí indica una <b>alerta roja</b> de posibles brotes infecciosos o fallas ambientales críticas.</li>
            <li><span class="highlight">Descarte Técnico:</span> Es la selección activa de aves débiles. Una buena selección previene contagios y optimiza el uso del alimento.</li>
        </ul>
        <p><i>Objetivo: Mantener la curva de mortalidad dentro de los estándares genéticos.</i></p>
    </div>
    """, unsafe_allow_html=True)

# TARJETA 2: ALIMENTO
st.markdown(f"""
    <div class="info-card">
        <h3>🧬 Sensor Temprano: El Alimento</h3>
        <p>El <span class="highlight">Consumo (gr/ave/día)</span> es el termómetro más rápido. Las aves dejan de comer 24 a 48 horas antes de que se caiga la postura o suba la mortalidad.</p>
        <p>Si detecta una caída en el gramaje, debe revisar inmediatamente la <b>calidad del agua</b>, la temperatura del galpón o posibles inicios de cuadros febriles en el lote.</p>
    </div>
    """, unsafe_allow_html=True)

# TARJETA 3: POSTURA
st.markdown(f"""
    <div class="info-card">
        <h3>📊 Eficiencia y Edad Biológica</h3>
        <p>El <span class="highlight">% de Postura</span> mide la conversión de alimento en huevo. Este dato siempre se analiza bajo la <b>Edad de las Aves (Semanas)</b>.</p>
        <p>Comparamos el rendimiento real contra la "Curva Guía" de la línea genética para saber si el lote está expresando su máximo potencial productivo según su etapa de vida.</p>
    </div>
    """, unsafe_allow_html=True)

# TARJETA 4: BITÁCORA
st.markdown(f"""
    <div class="info-card">
        <h3>📝 Bitácora de Campo</h3>
        <p>Los datos dicen <b>qué</b> pasó; la bitácora dice <b>por qué</b>. Buscamos eventos externos que alteren el comportamiento:</p>
        <ul>
            <li>Ruidos estresantes o presencia de depredadores.</li>
            <li>Fallas en suministros de agua o energía.</li>
            <li>Cambios de manejo por parte del personal de galpón.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Cierre flex-grid

# Botón final
if st.button(f"🚀 INICIAR DIAGNÓSTICO DE {st.session_state.user}"):
    st.switch_page("pages/02_Bitacora_Diaria.py")

st.markdown('</div>', unsafe_allow_html=True) # Cierre main-container
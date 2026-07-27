import base64
import io
import os
import re
import pandas as pd
import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="HUPA | Bitácora Maestra",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- FUNCION PARA ORDENAR GALPONES NUMÉRICAMENTE (1, 2, ..., 10, 11) ---
def orden_num_natural(lista):
    def clave(texto):
        return [
            int(c) if c.isdigit() else str(c).lower()
            for c in re.split(r"(\d+)", str(texto))
        ]

    return sorted(lista, key=clave)


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
    ' style="height: 60px; margin-right: 18px; border-radius: 8px; object-fit:'
    ' contain;">'
    if logo_b64
    else ""
)

# --- 2. ESTILO CSS AGROTECH CLEAN & EXECUTIVE ---
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
        padding: 20px 28px;
        border-radius: 16px;
        color: #FFFFFF !important;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(15, 81, 50, 0.25);
        display: flex;
        align-items: center;
    }
    .app-header-text h1 {
        color: #FFFFFF !important;
        font-size: clamp(1.3rem, 2.5vw, 1.8rem) !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .app-header-text p {
        color: #E8F8F5 !important;
        margin: 4px 0 0 0 !important;
        font-size: clamp(0.75rem, 1.5vw, 0.9rem) !important;
        opacity: 0.9;
    }

    /* PANEL DE FILTROS INTEGRADO */
    .filter-panel {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 16px 20px 6px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    /* TABLA AGROTECH INTERACTIVA COMPACTA PARA MÓVIL */
    .table-container {
        max-height: 420px;
        overflow-y: auto;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        background-color: var(--secondary-background-color);
    }

    .custom-agrotech-table {
        width: 100%;
        border-collapse: collapse;
        font-family: inherit;
        font-size: 0.84rem;
        color: var(--text-color);
    }

    .custom-agrotech-table th {
        position: sticky;
        top: 0;
        background-color: #0F5132 !important;
        color: #FFFFFF !important;
        padding: 10px 8px;
        text-align: center;
        font-weight: 700;
        border-bottom: 2px solid rgba(0,0,0,0.1);
        z-index: 2;
    }

    .custom-agrotech-table td {
        padding: 8px 6px;
        text-align: center;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15);
        white-space: nowrap;
    }

    .custom-agrotech-table tr:hover {
        background-color: rgba(17, 122, 101, 0.08);
    }

    /* PESTAÑAS (TABS) REACCIONALES CORREGIDAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding-bottom: 10px;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 10px 20px !important;
        font-weight: 600;
        color: var(--text-color);
        white-space: nowrap;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F5132 !important;
        color: #FFFFFF !important;
        border-color: #0F5132 !important;
        box-shadow: 0 4px 12px rgba(15, 81, 50, 0.3);
    }
    .stTabs [data-baseweb="tab-border"] {
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #0F5132 !important;
    }

    /* MEDIA QUERIES RESPONSIVAS */
    @media (max-width: 768px) {
        .filter-panel {
            padding: 12px 14px 4px 14px;
        }
        .app-header {
            flex-direction: column;
            text-align: center;
        }
        .app-header img {
            margin-right: 0 !important;
            margin-bottom: 10px;
        }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 3. VALIDACIÓN DE SESIÓN ---
if "auth" not in st.session_state or not st.session_state.auth:
    st.switch_page("app.py")
    st.stop()


# --- 4. CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data
def load_data():
    path = os.path.join("DATA", "REPORTE_AVITRACK_FINAL.xlsx")
    if os.path.exists(path):
        df = pd.read_excel(path)
        df = df.fillna(0)
        df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True).dt.date
        df["Edad Sem + Días"] = (
            df["Edad Sem + Días"].astype(str).str.replace("'", "")
        )

        columnas_filtro = [
            "Nombre de Granja (P) :",
            "Número de Lote :",
            "Galpón",
            "Ubicación",
            "Línea :",
        ]
        for col in columnas_filtro:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()


df_raw = load_data()
df_empresa = df_raw[df_raw["Razon Social"] == st.session_state.user].copy()

# BANNER CABECERA EJECUTIVA
st.markdown(
    f"""
    <div class="app-header">
        {logo_html}
        <div class="app-header-text">
            <h1>Bitácora Maestra de Campo</h1>
            <p>Registro histórico detallado, balances de huevos, consumo y mortalidades</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not df_empresa.empty:
    # --- 5. PANEL DE FILTROS INTEGRADO ---
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    c_granja, c_lote, c_fecha = st.columns([1, 1, 1.5])

    with c_granja:
        granjas_unicas = df_empresa["Nombre de Granja (P) :"].unique()
        lista_granjas = orden_num_natural([
            g
            for g in granjas_unicas
            if g not in [0, "0", "0.0", "None", None]
        ])
        granja_sel = st.selectbox("🏘️ Granja", lista_granjas)

    with c_lote:
        df_f_g = df_empresa[
            df_empresa["Nombre de Granja (P) :"] == granja_sel
        ]
        lote_sel = st.selectbox(
            "🆔 Lote", orden_num_natural(df_f_g["Número de Lote :"].unique())
        )

    df_f_l = df_f_g[df_f_g["Número de Lote :"] == lote_sel].copy()

    min_f = df_f_l["Fecha"].min()
    max_f = df_f_l["Fecha"].max()
    f_cierre = max_f - pd.Timedelta(days=1) if max_f > min_f else max_f

    opciones_looker = [
        "Últimos 7 días",
        "Últimos 15 días",
        "Últimos 30 días",
        "Este mes",
        "Mes pasado",
        "Todo el historial",
        "Personalizado",
    ]

    with c_fecha:
        tipo_periodo = st.selectbox(
            "📅 Período de Tiempo", opciones_looker, index=0
        )

    if tipo_periodo == "Últimos 7 días":
        fecha_ini = max(f_cierre - pd.Timedelta(days=6), min_f)
        rango = (fecha_ini, f_cierre)

    elif tipo_periodo == "Últimos 15 días":
        fecha_ini = max(f_cierre - pd.Timedelta(days=14), min_f)
        rango = (fecha_ini, f_cierre)

    elif tipo_periodo == "Últimos 30 días":
        fecha_ini = max(f_cierre - pd.Timedelta(days=29), min_f)
        rango = (fecha_ini, f_cierre)

    elif tipo_periodo == "Este mes":
        fecha_ini = max(f_cierre.replace(day=1), min_f)
        rango = (fecha_ini, f_cierre)

    elif tipo_periodo == "Mes pasado":
        primer_dia_este_mes = f_cierre.replace(day=1)
        ultimo_dia_mes_pasado = primer_dia_este_mes - pd.Timedelta(days=1)
        primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
        rango = (
            max(primer_dia_mes_pasado, min_f),
            min(ultimo_dia_mes_pasado, max_f),
        )

    elif tipo_periodo == "Todo el historial":
        rango = (min_f, max_f)

    elif tipo_periodo == "Personalizado":
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            f_desde = st.date_input(
                "Desde:",
                value=min_f,
                min_value=min_f,
                max_value=max_f,
                format="DD/MM/YYYY",
            )
        with r_col2:
            f_hasta = st.date_input(
                "Hasta:",
                value=max_f,
                min_value=min_f,
                max_value=max_f,
                format="DD/MM/YYYY",
            )

        if f_desde > f_hasta:
            st.error("⚠️ La fecha 'Desde' no puede ser mayor que 'Hasta'.")
            rango = (min_f, max_f)
        else:
            rango = (f_desde, f_hasta)

    st.markdown("</div>", unsafe_allow_html=True)

    if tipo_periodo != "Personalizado":
        st.caption(
            "📆 **Cierre Aplicado (al ayer):**"
            f" {rango[0].strftime('%d/%m/%Y')} al {rango[1].strftime('%d/%m/%Y')}"
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- 6. INFORMACIÓN CONCEPTUAL DEL LOTE ---
    if not df_f_l.empty:
        info_lote = df_f_l.iloc[0]
        with st.expander("🔍 Información Conceptual del Lote", expanded=False):
            inf1, inf2, inf3, inf4 = st.columns(4)
            inf1.metric(
                "📍 Ubicación",
                info_lote.get("Ubicación Granja (P) :", "N/A"),
            )
            inf2.metric(
                "🧬 Línea Genética",
                info_lote.get("Línea de las Aves :", "N/A"),
            )
            inf3.metric("🐣 Fecha Inicio", min_f.strftime("%d/%m/%Y"))
            inf4.metric("🏠 Total Galpones", len(df_f_l["Galpón"].unique()))

    # --- 7. RENDERIZADO DE TABLA INTERACTIVA ---
    def render_interactive_table(df_table):
        headers = [
            ("Fecha", "Fecha del registro diario en granja"),
            ("Edad", "Edad biológica de las aves (Semanas + Días)"),
            ("Mort.", "Mortalidad acumulada del día (Bajas)"),
            ("Saldo Total", "Aves vivas alojadas al cierre de la jornada"),
            (
                "Consumo Gr.",
                "Gramos de alimento consumido por ave al día (Real)",
            ),
            (
                "Gr. A. D.",
                "Gramos de alimento recomendados según la Guía Técnica",
            ),
            (
                "Dif Gr",
                "Diferencia de alimento (Real - Tabla). Positivo ="
                " Sobreconsumo / Negativo = Ahorro",
            ),
            ("Prod. Huevos", "Total de huevos recolectados en el día"),
            (
                "Dif Huevos Día",
                "Balance de huevos frente a la meta esperada de la tabla",
            ),
            (
                "% Prod.",
                "Porcentaje real de postura diaria (Huevos / Saldo Aves)",
            ),
            (
                "% Dia Tab",
                "Porcentaje teórico de postura esperado según la Guía Genética",
            ),
            (
                "Dif %",
                "Diferencia porcentual de postura frente a la guía (Real -"
                " Tabla)",
            ),
            (
                "Conv. Diaria",
                "Conversión alimenticia en puntos (Gramos de Alimento / Huevo)",
            ),
            (
                "Consumo Calcio",
                "Gramos de calcio/carbonato adicional suplementado por ave",
            ),
            (
                "Consumo Bx40",
                "Bultos de alimento de 40 kg consumidos en el día",
            ),
            (
                "Observaciones",
                "Novedades de manejo, clima, sanidad o bitácora de campo",
            ),
        ]

        html = '<div class="table-container"><table class="custom-agrotech-table"><thead><tr>'
        for title, tooltip in headers:
            html += f'<th title="{tooltip}">{title}</th>'
        html += "</tr></thead><tbody>"

        for _, row in df_table.iterrows():
            obs_raw = str(row.get("Observaciones", ""))
            obs_clean = (
                obs_raw.replace("'", "")
                .replace('"', "")
                .replace("<", "")
                .replace(">", "")
            )
            if obs_clean in ["0", "0.0", "nan", "None"]:
                obs_clean = ""

            dif_g = row["Dif Gr Ave"]
            if dif_g > 1.5:
                style_g = "background-color:#FEF5E7; color:#B9770E; font-weight:bold;"
                tip_g = (
                    f"🟠 +{dif_g:.2f}g de sobreconsumo por encima de la guía 🥣"
                )
            elif dif_g < -1.5:
                style_g = "background-color:#E8F8F5; color:#117A65; font-weight:bold;"
                tip_g = f"🟢 {dif_g:.2f}g de ahorro por debajo de la guía 🌾"
            else:
                style_g = ""
                tip_g = f"⚪ {dif_g:+.2f}g consumo dentro del rango óptimo 👍"

            dif_h = row["Dif Huevos"]
            if dif_h > 0:
                style_h = "background-color:#E8F8F5; color:#117A65; font-weight:bold;"
                tip_h = f"🟢 +{dif_h:,.0f} huevos por encima de lo esperado por tabla 🥳"
            elif dif_h < 0:
                style_h = "background-color:#FDEDEC; color:#A93226; font-weight:bold;"
                tip_h = f"🔴 {abs(dif_h):,.0f} huevos por debajo de lo esperado por tabla ⚠️"
            else:
                style_h = ""
                tip_h = "⚪ En la meta exacta esperada por tabla 🎯"

            dif_p = row["Dif Pdn"]
            if dif_p < -1.0:
                style_p = "background-color:#FDEDEC; color:#A93226; font-weight:bold;"
                tip_p = f"🔴 {dif_p:.2f}% de caída por debajo de la postura esperada 🚨"
            elif dif_p > 1.5:
                style_p = "background-color:#E8F8F5; color:#117A65; font-weight:bold;"
                tip_p = f"🟢 +{dif_p:.2f}% por encima de la postura esperada por tabla 📈"
            else:
                style_p = ""
                tip_p = f"⚪ {dif_p:+.2f}% postura alineada con la guía 🎯"

            fecha_str = (
                row["Fecha"].strftime("%d/%m/%y")
                if hasattr(row["Fecha"], "strftime")
                else str(row["Fecha"])
            )

            html += f"""<tr>
                <td>{fecha_str}</td>
                <td>{row['Edad Sem + Días']}</td>
                <td>{row['Mort.']:,.0f}</td>
                <td>{row['Saldo Aves']:,.0f}</td>
                <td>{row['Consumo Gr. A. D.']:.1f}</td>
                <td>{row['Gr. A. D. Tabla']:.1f}</td>
                <td style="{style_g}" title="{tip_g}">{row['Dif Gr Ave']:+.2f}</td>
                <td>{row['Producción Huevos Día']:,.0f}</td>
                <td style="{style_h}" title="{tip_h}">{row['Dif Huevos']:+,.0f}</td>
                <td>{row['% Diario de Prod.']:.2f}%</td>
                <td>{row['% Dia Prod. Tab']:.2f}%</td>
                <td style="{style_p}" title="{tip_p}">{row['Dif Pdn']:+.2f}%</td>
                <td>{row['Conv Diaria']:.2f}</td>
                <td>{row['Consumo Calcio Gr. A. D.']:.1f}</td>
                <td>{row['Consumo B X 40 K']:,.0f}</td>
                <td style="text-align:left; max-width:200px; overflow:hidden; text-overflow:ellipsis;">{obs_clean}</td>
            </tr>"""

        html += "</tbody></table></div>"
        st.markdown(html, unsafe_allow_html=True)

    # --- 8. PESTAÑAS CON ORDENAMIENTO NUMÉRICO NATURAL ---
    lista_galpones_raw = [
        g for g in df_f_l["Galpón"].unique() if g not in [0, "0", None]
    ]

    lista_galpones = orden_num_natural(lista_galpones_raw)

    if lista_galpones:
        nombres_tabs = ["🌐 Consolidado Lote"] + [
            f"🏠 Galpón {g}" for g in lista_galpones
        ]
        tabs = st.tabs(nombres_tabs)

        def badge_num(valor, texto_fmt, es_inverso=False):
            if valor == 0:
                bg_color = "#EAEDED"
                tx_color = "#5D6D7E"
            elif (valor > 0 and not es_inverso) or (valor < 0 and es_inverso):
                bg_color = "#E8F8F5"
                tx_color = "#117A65"
            else:
                bg_color = "#FDEDEC"
                tx_color = "#A93226"

            return (
                f'<span style="background-color: {bg_color}; color: {tx_color};'
                " padding: 3px 10px; border-radius: 12px; font-weight: bold;"
                f' font-size: 0.82rem;">{texto_fmt}</span>'
            )

        cols = [
            "Fecha",
            "Edad Sem + Días",
            "Mort.",
            "Saldo Aves",
            "Consumo Gr. A. D.",
            "Gr. A. D. Tabla",
            "Dif Gr Ave",
            "Producción Huevos Día",
            "Dif Huevos",
            "% Diario de Prod.",
            "% Dia Prod. Tab",
            "Dif Pdn",
            "Conv Diaria",
            "Consumo Calcio Gr. A. D.",
            "Consumo B X 40 K",
            "Observaciones",
        ]

        # ==========================================
        # TAB 0: CONSOLIDADO GENERAL DEL LOTE
        # ==========================================
        with tabs[0]:
            df_gen_base = df_f_l.copy()
            df_gen_base["Kilos_Alimento_Dia"] = (
                df_gen_base["Consumo Gr. A. D."] * df_gen_base["Saldo Aves"]
            ) / 1000
            df_gen_base["Kilos_Calcio_Dia"] = (
                df_gen_base["Consumo Calcio Gr. A. D."]
                * df_gen_base["Saldo Aves"]
            ) / 1000

            df_gen_group = df_gen_base.groupby("Fecha", as_index=False).agg({
                "Edad Sem + Días": "first",
                "Mort.": "sum",
                "Saldo Aves": "sum",
                "Producción Huevos Día": "sum",
                "Consumo B X 40 K": "sum",
                "Kilos_Alimento_Dia": "sum",
                "Kilos_Calcio_Dia": "sum",
                "% Dia Prod. Tab": "mean",
                "Gr. A. D. Tabla": "mean",
                "Observaciones": lambda x: " | ".join(
                    [
                        str(v)
                        for v in x
                        if str(v) not in ["0", "0.0", "", "nan"]
                    ]
                ),
            })

            df_gen_group["Consumo Gr. A. D."] = (
                df_gen_group["Kilos_Alimento_Dia"] * 1000
            ) / df_gen_group["Saldo Aves"]
            df_gen_group["Consumo Calcio Gr. A. D."] = (
                df_gen_group["Kilos_Calcio_Dia"] * 1000
            ) / df_gen_group["Saldo Aves"]
            df_gen_group["% Diario de Prod."] = (
                df_gen_group["Producción Huevos Día"]
                / df_gen_group["Saldo Aves"]
            ) * 100

            df_gen_group["Dif Gr Ave"] = (
                df_gen_group["Consumo Gr. A. D."]
                - df_gen_group["Gr. A. D. Tabla"]
            )
            df_gen_group["Dif Pdn"] = (
                df_gen_group["% Diario de Prod."]
                - df_gen_group["% Dia Prod. Tab"]
            )
            df_gen_group["Conv Diaria"] = (
                (
                    df_gen_group["Consumo Gr. A. D."]
                    / (df_gen_group["% Diario de Prod."] / 100)
                )
                .replace([float("inf"), -float("inf")], 0)
                .fillna(0)
            )

            df_gen_group["Huevos Tabla"] = (
                df_gen_group["% Dia Prod. Tab"] / 100
            ) * df_gen_group["Saldo Aves"]
            df_gen_group["Dif Huevos"] = (
                df_gen_group["Producción Huevos Día"]
                - df_gen_group["Huevos Tabla"]
            )

            if isinstance(rango, tuple) and len(rango) == 2:
                df_periodo_gen = df_gen_group[
                    (df_gen_group["Fecha"] >= rango[0])
                    & (df_gen_group["Fecha"] <= rango[1])
                ].copy()
            else:
                df_periodo_gen = (
                    df_gen_group[df_gen_group["Fecha"] == rango].copy()
                    if not isinstance(rango, tuple)
                    else df_gen_group.copy()
                )

            df_vista_gen = df_periodo_gen.sort_values(
                by="Fecha", ascending=False
            )

            with st.expander(
                "📄 Ver Registros Diarios (Consolidado)", expanded=False
            ):
                render_interactive_table(df_vista_gen)

            if not df_periodo_gen.empty:
                total_mort_g = df_periodo_gen["Mort."].sum()
                total_huevos_g = df_periodo_gen["Producción Huevos Día"].sum()
                total_huevos_tab_g = df_periodo_gen["Huevos Tabla"].sum()
                dif_huevos_total_g = total_huevos_g - total_huevos_tab_g
                total_bultos_g = df_periodo_gen["Consumo B X 40 K"].sum()

                dias_calcio_g = df_periodo_gen[
                    df_periodo_gen["Consumo Calcio Gr. A. D."] > 0
                ]
                cant_dias_calcio_g = len(dias_calcio_g)
                calcio_prom_g = (
                    dias_calcio_g["Consumo Calcio Gr. A. D."].mean()
                    if cant_dias_calcio_g > 0
                    else 0
                )

                dias_con_datos_g = df_periodo_gen[
                    df_periodo_gen["Consumo Gr. A. D."] > 0
                ]
                if not dias_con_datos_g.empty:
                    p_real_g = dias_con_datos_g["% Diario de Prod."].mean()
                    p_guia_g = dias_con_datos_g["% Dia Prod. Tab"].mean()
                    c_real_g = dias_con_datos_g["Consumo Gr. A. D."].mean()
                    c_guia_g = dias_con_datos_g["Gr. A. D. Tabla"].mean()
                    conv_prom_g = dias_con_datos_g["Conv Diaria"].mean()
                    dif_p_g = p_real_g - p_guia_g
                    dif_c_g = c_real_g - c_guia_g
                else:
                    p_real_g = (
                        p_guia_g
                    ) = (
                        c_real_g
                    ) = c_guia_g = conv_prom_g = dif_p_g = dif_c_g = 0

                badge_dif_h_g = badge_num(
                    dif_huevos_total_g, f"{dif_huevos_total_g:+,.0f} huevos"
                )
                badge_dif_p_g = badge_num(dif_p_g, f"{dif_p_g:+.2f}%")
                badge_dif_c_g = badge_num(
                    dif_c_g, f"{dif_c_g:+.1f}g", es_inverso=True
                )

                tabla_html_g = f"""
                <table style="width:100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.85rem; margin-top: 5px; margin-bottom: 15px;">
                  <thead>
                    <tr style="background-color: var(--secondary-background-color); border-bottom: 2px solid rgba(128,128,128,0.2);">
                      <th style="text-align: left; padding: 8px 12px; color: var(--text-color);">Concepto</th>
                      <th style="text-align: left; padding: 8px 12px; color: var(--text-color);">Valores del Periodo (Consolidado Lote)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">💀 Mortalidad Acumulada Lote</td>
                      <td style="padding: 8px 12px; color: var(--text-color);"><b>{total_mort_g:,.0f}</b> aves</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">🥚 Producción Total (Real | Tabla)</td>
                      <td style="padding: 8px 12px; color: var(--text-color);"><b>{total_huevos_g:,.0f}</b> | <b>{total_huevos_tab_g:,.0f}</b> huevos</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">🎯 Balance de Huevos (Faltante / Sobrante)</td>
                      <td style="padding: 8px 12px;">{badge_dif_h_g}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">🌽 Alimento Consumido Total</td>
                      <td style="padding: 8px 12px; color: var(--text-color);"><b>{total_bultos_g:,.0f}</b> bultos</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">📈 Postura Promedio (Real | Guía | Dif)</td>
                      <td style="padding: 8px 12px; color: var(--text-color);"><b>{p_real_g:.2f}%</b> | <b>{p_guia_g:.2f}%</b> | {badge_dif_p_g}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">🥣 Consumo Promedio (Real | Guía | Dif)</td>
                      <td style="padding: 8px 12px; color: var(--text-color);"><b>{c_real_g:.2f}g</b> | <b>{c_guia_g:.2f}g</b> | {badge_dif_c_g}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">🔄 Conversión Promedio Lote</td>
                      <td style="padding: 8px 12px; color: var(--text-color);"><b>{conv_prom_g:.2f}</b> pts</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                      <td style="padding: 8px 12px; color: var(--text-color);">🦴 Consumo de Calcio (Días Aplic. | Prom. Día)</td>
                      <td style="padding: 8px 12px; color: var(--text-color);"><b>{cant_dias_calcio_g}</b> días | <b>{calcio_prom_g:.2f}</b> g/ave</td>
                    </tr>
                  </tbody>
                </table>
                """

                st.markdown(
                    "##### 📊 Resumen de Totales y Promedios -"
                    " Consolidado de Lote"
                )
                st.markdown(tabla_html_g, unsafe_allow_html=True)

                buffer_g = io.BytesIO()
                with pd.ExcelWriter(buffer_g, engine="xlsxwriter") as writer:
                    df_vista_gen[cols].to_excel(writer, index=False)

                st.download_button(
                    label=f"📥 Descargar Excel Consolidado Lote {lote_sel}",
                    data=buffer_g.getvalue(),
                    file_name=f"Bitacora_Consolidado_Lote_{lote_sel}.xlsx",
                    key="btn_consolidado_lote",
                )

        # ==========================================
        # TABS INDIVIDUALES DE GALPONES
        # ==========================================
        for i, galpon_actual in enumerate(lista_galpones):
            with tabs[i + 1]:
                df_tab_base = df_f_l[df_f_l["Galpón"] == galpon_actual].copy()

                df_tab_base["Dif Gr Ave"] = (
                    df_tab_base["Consumo Gr. A. D."]
                    - df_tab_base["Gr. A. D. Tabla"]
                )
                df_tab_base["Dif Pdn"] = (
                    df_tab_base["% Diario de Prod."]
                    - df_tab_base["% Dia Prod. Tab"]
                )
                df_tab_base["Conv Diaria"] = (
                    (
                        df_tab_base["Consumo Gr. A. D."]
                        / (df_tab_base["% Diario de Prod."] / 100)
                    )
                    .replace([float("inf"), -float("inf")], 0)
                    .fillna(0)
                )

                df_tab_base["Huevos Tabla"] = (
                    df_tab_base["% Dia Prod. Tab"] / 100
                ) * df_tab_base["Saldo Aves"]
                df_tab_base["Dif Huevos"] = (
                    df_tab_base["Producción Huevos Día"]
                    - df_tab_base["Huevos Tabla"]
                )

                if isinstance(rango, tuple) and len(rango) == 2:
                    df_periodo = df_tab_base[
                        (df_tab_base["Fecha"] >= rango[0])
                        & (df_tab_base["Fecha"] <= rango[1])
                    ].copy()
                else:
                    df_periodo = (
                        df_tab_base[df_tab_base["Fecha"] == rango].copy()
                        if not isinstance(rango, tuple)
                        else df_tab_base.copy()
                    )

                df_vista = df_periodo.sort_values(by="Fecha", ascending=False)

                with st.expander(
                    f"📄 Ver Registros Diarios (Galpón {galpon_actual})",
                    expanded=False,
                ):
                    render_interactive_table(df_vista)

                if not df_periodo.empty:
                    total_mort = df_periodo["Mort."].sum()
                    total_huevos = df_periodo["Producción Huevos Día"].sum()
                    total_huevos_tab = df_periodo["Huevos Tabla"].sum()
                    dif_huevos_total = total_huevos - total_huevos_tab
                    total_bultos = df_periodo["Consumo B X 40 K"].sum()

                    dias_calcio = df_periodo[
                        df_periodo["Consumo Calcio Gr. A. D."] > 0
                    ]
                    cant_dias_calcio = len(dias_calcio)
                    calcio_prom = (
                        dias_calcio["Consumo Calcio Gr. A. D."].mean()
                        if cant_dias_calcio > 0
                        else 0
                    )

                    dias_con_datos = df_periodo[
                        df_periodo["Consumo Gr. A. D."] > 0
                    ]
                    if not dias_con_datos.empty:
                        p_real = dias_con_datos["% Diario de Prod."].mean()
                        p_guia = dias_con_datos["% Dia Prod. Tab"].mean()
                        c_real = dias_con_datos["Consumo Gr. A. D."].mean()
                        c_guia = dias_con_datos["Gr. A. D. Tabla"].mean()
                        conv_prom = dias_con_datos["Conv Diaria"].mean()
                        dif_p = p_real - p_guia
                        dif_c = c_real - c_guia
                    else:
                        p_real = (
                            p_guia
                        ) = (
                            c_real
                        ) = c_guia = conv_prom = dif_p = dif_c = 0

                    badge_dif_h = badge_num(
                        dif_huevos_total, f"{dif_huevos_total:+,.0f} huevos"
                    )
                    badge_dif_p = badge_num(dif_p, f"{dif_p:+.2f}%")
                    badge_dif_c = badge_num(
                        dif_c, f"{dif_c:+.1f}g", es_inverso=True
                    )

                    tabla_html = f"""
                    <table style="width:100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.85rem; margin-top: 5px; margin-bottom: 15px;">
                      <thead>
                        <tr style="background-color: var(--secondary-background-color); border-bottom: 2px solid rgba(128,128,128,0.2);">
                          <th style="text-align: left; padding: 8px 12px; color: var(--text-color);">Concepto</th>
                          <th style="text-align: left; padding: 8px 12px; color: var(--text-color);">Valores del Periodo</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">💀 Mortalidad Acumulada</td>
                          <td style="padding: 8px 12px; color: var(--text-color);"><b>{total_mort:,.0f}</b> aves</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">🥚 Producción Total (Real | Tabla)</td>
                          <td style="padding: 8px 12px; color: var(--text-color);"><b>{total_huevos:,.0f}</b> | <b>{total_huevos_tab:,.0f}</b> huevos</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">🎯 Balance de Huevos (Faltante / Sobrante)</td>
                          <td style="padding: 8px 12px;">{badge_dif_h}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">🌽 Alimento Consumido</td>
                          <td style="padding: 8px 12px; color: var(--text-color);"><b>{total_bultos:,.0f}</b> bultos</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">📈 Postura (Real | Guía | Dif)</td>
                          <td style="padding: 8px 12px; color: var(--text-color);"><b>{p_real:.2f}%</b> | <b>{p_guia:.2f}%</b> | {badge_dif_p}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">🥣 Consumo (Real | Guía | Dif)</td>
                          <td style="padding: 8px 12px; color: var(--text-color);"><b>{c_real:.2f}g</b> | <b>{c_guia:.2f}g</b> | {badge_dif_c}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">🔄 Conversión Promedio</td>
                          <td style="padding: 8px 12px; color: var(--text-color);"><b>{conv_prom:.2f}</b> pts</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(128,128,128,0.15);">
                          <td style="padding: 8px 12px; color: var(--text-color);">🦴 Consumo de Calcio (Días Aplic. | Prom. Día)</td>
                          <td style="padding: 8px 12px; color: var(--text-color);"><b>{cant_dias_calcio}</b> días | <b>{calcio_prom:.2f}</b> g/ave</td>
                        </tr>
                      </tbody>
                    </table>
                    """

                    st.markdown(
                        "##### 📊 Resumen de Totales y Promedios -"
                        f" Galpón {galpon_actual}"
                    )
                    st.markdown(tabla_html, unsafe_allow_html=True)

                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                        df_vista[cols].to_excel(writer, index=False)

                    st.download_button(
                        label=f"📥 Descargar Excel G{galpon_actual}",
                        data=buffer.getvalue(),
                        file_name=f"Bitacora_G{galpon_actual}.xlsx",
                        key=f"btn_{galpon_actual}",
                    )
                else:
                    st.warning("No hay datos para el periodo seleccionado.")

else:
    st.error("No se encontraron datos para la empresa actual.")
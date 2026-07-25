import base64
import datetime
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="HUPA | Dashboard Avícola",
    page_icon="🐓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- FUNCION PARA CARGAR LOGO Y CONVERTIR A BASE64 ---
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

# --- 2. DISEÑO AGROTECH CLEAN & EXECUTIVE ---
st.markdown(
    """
    <style>
    /* Mantener visible la barra de navegación superior y menú lateral */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* CABECERA PRINCIPAL CON LOGO INTEGRADAS */
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

    /* PANEL DE FILTROS LIMPIO */
    .filter-panel {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 16px 20px 6px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    /* BADGE DE LÍNEA GENÉTICA DESTACADO */
    .genetics-badge-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, rgba(17, 122, 101, 0.12) 0%, rgba(39, 174, 96, 0.08) 100%);
        border-left: 5px solid #117A65;
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 18px;
    }
    .genetics-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: var(--text-color);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .genetics-tag {
        background-color: #0F5132;
        color: #FFFFFF;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(15, 81, 50, 0.2);
    }

    /* TARJETAS KPI EXECUTIVE CON CURSOR INTERACTIVO */
    .kpi-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 15px;
        cursor: help;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #117A65, #27AE60);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: clamp(0.7rem, 1vw, 0.8rem);
        font-weight: 700;
        color: var(--text-color);
        opacity: 0.75;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: clamp(1.3rem, 2vw, 1.7rem);
        font-weight: 800;
        color: var(--text-color);
        line-height: 1.1;
    }
    .kpi-badge-container {
        margin-top: 8px;
    }
    .kpi-badge-positive {
        display: inline-block;
        background-color: #E8F8F5;
        color: #117A65;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: clamp(0.7rem, 1vw, 0.78rem);
        font-weight: 700;
    }
    .kpi-badge-negative {
        display: inline-block;
        background-color: #FDEDEC;
        color: #A93226;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: clamp(0.7rem, 1vw, 0.78rem);
        font-weight: 700;
    }
    .kpi-badge-neutral {
        display: inline-block;
        background-color: rgba(128, 128, 128, 0.15);
        color: var(--text-color);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: clamp(0.7rem, 1vw, 0.78rem);
        font-weight: 700;
    }

    /* PESTAÑAS (TABS) REACCIONALES */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: transparent;
        padding-bottom: 8px;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 8px 14px;
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

    /* MEDIA QUERIES PARA MÓVIL */
    @media (max-width: 768px) {
        .filter-panel {
            padding: 12px 14px 4px 14px;
        }
        .kpi-card {
            padding: 12px 8px;
        }
        .app-header {
            flex-direction: column;
            text-align: center;
        }
        .app-header img {
            margin-right: 0 !important;
            margin-bottom: 10px;
        }
        .genetics-badge-container {
            flex-direction: column;
            gap: 8px;
            text-align: center;
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
            "Línea de las Aves :",
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
            <h1>Panel Técnico y Agroanalítica</h1>
            <p>Monitoreo en tiempo real de lotes de postura, curvas de nutrición y bioseguridad</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not df_empresa.empty:
    # --- 5. BARRA DE FILTROS INTEGRADA ---
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1.4, 1])

    with c1:
        lista_granjas = sorted(
            [
                g
                for g in df_empresa["Nombre de Granja (P) :"].unique()
                if pd.notna(g) and g not in [0, "0", "None"]
            ]
        )
        granja_sel = st.selectbox("🏘️ Granja", lista_granjas)

    with c2:
        df_f_g = df_empresa[
            df_empresa["Nombre de Granja (P) :"] == granja_sel
        ]
        lista_lotes = sorted(
            [
                l
                for l in df_f_g["Número de Lote :"].unique()
                if pd.notna(l) and l not in [0, "0", "None"]
            ]
        )
        lote_sel = st.selectbox("🆔 Lote", lista_lotes)

    df_f_l = df_f_g[df_f_g["Número de Lote :"] == lote_sel].copy()

    # OBTENER LÍNEA GENÉTICA DEL LOTE
    linea_genetica = "N/A"
    for col_gen in ["Línea de las Aves :", "Línea :", "Línea"]:
        if col_gen in df_f_l.columns:
            val = df_f_l[col_gen].dropna().iloc[0] if not df_f_l.empty else ""
            if str(val).strip() not in ["0", "0.0", "nan", "None", ""]:
                linea_genetica = str(val).strip()
                break

    min_f = df_f_l["Fecha"].min()
    max_f = df_f_l["Fecha"].max()
    hoy_ref = max_f - datetime.timedelta(days=1) if max_f > min_f else max_f

    with c3:
        filtro_rapido = st.selectbox(
            "📅 Período de Tiempo",
            [
                "Últimos 7 días",
                "Últimos 15 días",
                "Últimos 30 días",
                "Ver Todo",
                "Personalizado",
            ],
            index=0,
        )

    with c4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        mostrar_etiquetas = st.toggle("🏷️ Valores en puntos", value=False)

    # Lógica de Fechas
    if filtro_rapido == "Últimos 7 días":
        rango = (max(hoy_ref - datetime.timedelta(days=6), min_f), hoy_ref)
    elif filtro_rapido == "Últimos 15 días":
        rango = (max(hoy_ref - datetime.timedelta(days=14), min_f), hoy_ref)
    elif filtro_rapido == "Últimos 30 días":
        rango = (max(hoy_ref - datetime.timedelta(days=29), min_f), hoy_ref)
    elif filtro_rapido == "Ver Todo":
        rango = (min_f, max_f)
    elif filtro_rapido == "Personalizado":
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            f_ini = st.date_input(
                "Desde",
                value=min_f,
                min_value=min_f,
                max_value=max_f,
                format="DD/MM/YYYY",
            )
        with col_p2:
            f_fin = st.date_input(
                "Hasta",
                value=hoy_ref,
                min_value=min_f,
                max_value=max_f,
                format="DD/MM/YYYY",
            )
        rango = (f_ini, f_fin) if f_ini <= f_fin else (min_f, max_f)

    st.markdown("</div>", unsafe_allow_html=True)

    # BANNER RESALTADO DE LÍNEA GENÉTICA Y RANGO
    st.markdown(
        f"""
        <div class="genetics-badge-container">
            <div class="genetics-title">
                🧬 <b>Línea Genética de las Aves:</b> 
                <span class="genetics-tag">{linea_genetica}</span>
            </div>
            <div style="font-size: 0.85rem; opacity: 0.85;">
                📆 <b>Cierre:</b> {rango[0].strftime('%d/%m/%Y')} al {rango[1].strftime('%d/%m/%Y')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- 6. PALETA DE COLORES FIJA POR GALPÓN ---
    lista_galpones = sorted(
        [g for g in df_f_l["Galpón"].unique() if g not in [0, "0", None]]
    )
    paleta_colores = [
        "#117A65",
        "#2980B9",
        "#D97706",
        "#8E44AD",
        "#27AE60",
        "#D35400",
        "#16A085",
    ]
    color_map = {
        g: paleta_colores[idx % len(paleta_colores)]
        for idx, g in enumerate(lista_galpones)
    }

    modo_grafico = (
        "lines+markers+text" if mostrar_etiquetas else "lines+markers"
    )

    def render_4_charts(df_input, title_suffix, is_compare=False):
        if df_input.empty:
            st.warning("No hay datos en el rango seleccionado.")
            return

        df_input = df_input.copy()

        # --- CÁLCULOS KPI CON MESSAGES FLOTANTES (TOOLTIPS TITLE) ---
        postura_prom = df_input["% Diario de Prod."].mean()
        guia_postura_prom = df_input["% Dia Prod. Tab"].mean()
        dif_postura = postura_prom - guia_postura_prom

        consumo_prom = df_input["Consumo Gr. A. D."].mean()
        guia_consumo_prom = df_input["Gr. A. D. Tabla"].mean()
        dif_consumo = consumo_prom - guia_consumo_prom

        total_bajas = df_input["Mort."].sum()
        total_huevos_real = df_input["Producción Huevos Día"].sum()

        badge_p_cls = (
            "kpi-badge-positive" if dif_postura >= 0 else "kpi-badge-negative"
        )
        badge_c_cls = (
            "kpi-badge-positive" if dif_consumo <= 0 else "kpi-badge-negative"
        )

        tip_postura = f"🥚 Promedio de postura ({postura_prom:.1f}%). Guía técnica {linea_genetica}: {guia_postura_prom:.1f}%."
        tip_consumo = f"🥣 Gramos por ave al día ({consumo_prom:.1f}g). Guía técnica {linea_genetica}: {guia_consumo_prom:.1f}g."
        tip_bajas = f"💀 Mortalidad acumulada ({total_bajas:,.0f} aves) para la línea {linea_genetica} en este período."
        tip_huevos = f"📦 Total de huevos recolectados ({total_huevos_real:,.0f} unidades)."

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown(
                f"""
                <div class="kpi-card" title="{tip_postura}">
                    <div class="kpi-title">🥚 Postura Promedio</div>
                    <div class="kpi-value">{postura_prom:.1f}%</div>
                    <div class="kpi-badge-container">
                        <span class="{badge_p_cls}">{dif_postura:+.1f}% vs Guía</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k2:
            st.markdown(
                f"""
                <div class="kpi-card" title="{tip_consumo}">
                    <div class="kpi-title">🥣 Consumo Ave/Día</div>
                    <div class="kpi-value">{consumo_prom:.1f}g</div>
                    <div class="kpi-badge-container">
                        <span class="{badge_c_cls}">{dif_consumo:+.1f}g vs Guía</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k3:
            st.markdown(
                f"""
                <div class="kpi-card" title="{tip_bajas}">
                    <div class="kpi-title">💀 Bajas Acumuladas</div>
                    <div class="kpi-value">{total_bajas:,.0f}</div>
                    <div class="kpi-badge-container">
                        <span class="kpi-badge-neutral">Mortalidad del período</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k4:
            st.markdown(
                f"""
                <div class="kpi-card" title="{tip_huevos}">
                    <div class="kpi-title">📦 Producción Total</div>
                    <div class="kpi-value">{total_huevos_real:,.0f}</div>
                    <div class="kpi-badge-container">
                        <span class="kpi-badge-neutral">Huevos recolectados</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Preparar Cálculos de Gráficos
        df_input["Ef"] = (
            df_input["Consumo Gr. A. D."]
            / (df_input["% Diario de Prod."] / 100)
        ).replace([float("inf"), -float("inf")], 0)

        df_input["Dif_Pdn"] = (
            df_input["% Diario de Prod."] - df_input["% Dia Prod. Tab"]
        )
        df_input["Dif_Consumo"] = (
            df_input["Consumo Gr. A. D."] - df_input["Gr. A. D. Tabla"]
        )

        df_input["Html_Dif_Pdn"] = df_input["Dif_Pdn"].apply(
            lambda v: (
                f'<span style="background-color:#E8F8F5; color:#117A65;'
                f' padding:1px 6px; border-radius:4px; font-weight:bold;">{v:+.1f}%</span>'
                if v >= 0
                else (
                    f'<span style="background-color:#FDEDEC; color:#A93226;'
                    f' padding:1px 6px; border-radius:4px; font-weight:bold;">{v:+.1f}%</span>'
                )
            )
        )

        df_input["Html_Dif_Consumo"] = df_input["Dif_Consumo"].apply(
            lambda v: (
                f'<span style="background-color:#FEF5E7; color:#B9770E;'
                f' padding:1px 6px; border-radius:4px; font-weight:bold;">{v:+.1f}g</span>'
                if v > 1.5
                else (
                    f'<span style="background-color:#E8F8F5; color:#117A65;'
                    f' padding:1px 6px; border-radius:4px; font-weight:bold;">{v:+.1f}g</span>'
                )
            )
        )

        guia_lote = (
            df_input.groupby("Fecha")[["% Dia Prod. Tab", "Gr. A. D. Tabla"]]
            .mean()
            .reset_index()
            .sort_values("Fecha")
        )

        if is_compare:
            resumen_pdn_map = {}
            resumen_cons_map = {}

            for f_val, sub_df in df_input.groupby("Fecha"):
                txt_pdn = "<b>📋 Todos los Galpones (Postura):</b><br>"
                txt_cons = "<b>📋 Todos los Galpones (Consumo):</b><br>"

                for _, r_item in sub_df.sort_values("Galpón").iterrows():
                    g_num = r_item["Galpón"]
                    p_val = r_item["% Diario de Prod."]
                    p_dif = r_item["Dif_Pdn"]
                    c_val = r_item["Consumo Gr. A. D."]
                    c_dif = r_item["Dif_Consumo"]

                    badge_p = (
                        f'<span style="background-color:#E8F8F5; color:#117A65;'
                        f' padding:0px 4px; border-radius:3px;'
                        f' font-weight:bold;">{p_dif:+.1f}%</span>'
                        if p_dif >= 0
                        else (
                            '<span style="background-color:#FDEDEC;'
                            " color:#A93226; padding:0px 4px; border-radius:3px;"
                            f' font-weight:bold;">{p_dif:+.1f}%</span>'
                        )
                    )

                    badge_c = (
                        f'<span style="background-color:#FEF5E7; color:#B9770E;'
                        f' padding:0px 4px; border-radius:3px;'
                        f' font-weight:bold;">{c_dif:+.1f}g</span>'
                        if c_dif > 1.5
                        else (
                            '<span style="background-color:#E8F8F5;'
                            " color:#117A65; padding:0px 4px; border-radius:3px;"
                            f' font-weight:bold;">{c_dif:+.1f}g</span>'
                        )
                    )

                    txt_pdn += f"• <b>G{g_num}:</b> {p_val:.1f}% ({badge_p})<br>"
                    txt_cons += (
                        f"• <b>G{g_num}:</b> {c_val:.1f}g ({badge_c})<br>"
                    )

                resumen_pdn_map[f_val] = txt_pdn
                resumen_cons_map[f_val] = txt_cons

            guia_lote["Hover_Pdn_Multi"] = guia_lote["Fecha"].map(
                resumen_pdn_map
            )
            guia_lote["Hover_Cons_Multi"] = guia_lote["Fecha"].map(
                resumen_cons_map
            )

        layout_comun = dict(
            height=340,
            margin=dict(l=15, r=15, t=15, b=15),
            hovermode="closest",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(128,128,128,0.15)",
                tickformat="%d/%m",
                linecolor="rgba(128,128,128,0.3)",
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(128,128,128,0.15)",
                linecolor="rgba(128,128,128,0.3)",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        row1_c1, row1_c2 = st.columns(2)
        row2_c1, row2_c2 = st.columns(2)

        # 1. POSTURA
        with row1_c1:
            with st.container(border=True):
                st.markdown(
                    f"##### 🥚 Porcentaje de Postura {title_suffix}",
                    help=(
                        f"Mide postura real vs Guía {linea_genetica}. Caídas"
                        " advierten problemas clínicos o nutricionales."
                    ),
                )
                fig = go.Figure()

                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input["Galpón"] == g].sort_values(
                            "Fecha"
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=d["Fecha"],
                                y=d["% Diario de Prod."],
                                name=f"G{g}",
                                line=dict(color=color_map[g], width=2.5),
                                mode=modo_grafico,
                                text=(
                                    d["% Diario de Prod."].map("{:.1f}%".format)
                                    if mostrar_etiquetas
                                    else None
                                ),
                                textposition="top center",
                                customdata=d[
                                    [
                                        "Edad Sem + Días",
                                        "% Dia Prod. Tab",
                                        "Html_Dif_Pdn",
                                    ]
                                ],
                                hovertemplate=(
                                    "<b>Galpón "
                                    f"{g}</b><br><b>Sem:</b>"
                                    " %{customdata[0]}<br><b>Real:</b>"
                                    " %{y:.1f}%<br><b>Guía:</b>"
                                    " %{customdata[1]:.1f}%<br><b>Dif:</b>"
                                    " %{customdata[2]}<extra></extra>"
                                ),
                            )
                        )
                    fig.add_trace(
                        go.Scatter(
                            x=guia_lote["Fecha"],
                            y=guia_lote["% Dia Prod. Tab"],
                            name=f"Tabla ({linea_genetica})",
                            line=dict(color="#C0392B", dash="dash", width=2.5),
                            customdata=guia_lote[["Hover_Pdn_Multi"]],
                            hovertemplate=(
                                "<b>Guía Tabla Lote:</b>"
                                " %{y:.1f}%<br><br>%{customdata[0]}<extra></extra>"
                            ),
                        )
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=df_input["Fecha"],
                            y=df_input["% Diario de Prod."],
                            name="Real",
                            line=dict(color="#117A65", width=3.5),
                            mode=modo_grafico,
                            text=(
                                df_input["% Diario de Prod."].map(
                                    "{:.1f}%".format
                                )
                                if mostrar_etiquetas
                                else None
                            ),
                            textposition="top center",
                            customdata=df_input[
                                [
                                    "Edad Sem + Días",
                                    "% Dia Prod. Tab",
                                    "Html_Dif_Pdn",
                                ]
                            ],
                            hovertemplate=(
                                "<b>Sem:</b> %{customdata[0]}<br><b>Real:</b>"
                                " %{y:.1f}%<br><b>Guía:</b>"
                                " %{customdata[1]:.1f}%<br><b>Dif:</b>"
                                " %{customdata[2]}<extra></extra>"
                            ),
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df_input["Fecha"],
                            y=df_input["% Dia Prod. Tab"],
                            name=f"Guía ({linea_genetica})",
                            line=dict(color="#C0392B", dash="dash", width=2),
                            hovertemplate="<b>Guía:</b> %{y:.1f}%<extra></extra>",
                        )
                    )

                fig.update_layout(layout_comun)
                fig.update_layout(yaxis=dict(ticksuffix="%"))
                st.plotly_chart(fig, use_container_width=True)

        # 2. CONSUMO DE ALIMENTO
        with row1_c2:
            with st.container(border=True):
                st.markdown(
                    f"##### 🥣 Consumo de Alimento (g/ave/día) {title_suffix}",
                    help=(
                        f"Gramos por ave servidos vs Guía {linea_genetica}. El"
                        " consumo cae antes de un cuadro de estrés o caída de"
                        " postura."
                    ),
                )
                fig = go.Figure()

                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input["Galpón"] == g].sort_values(
                            "Fecha"
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=d["Fecha"],
                                y=d["Consumo Gr. A. D."],
                                name=f"G{g}",
                                line=dict(color=color_map[g], width=2.5),
                                mode=modo_grafico,
                                text=(
                                    d["Consumo Gr. A. D."].map("{:.1f}g".format)
                                    if mostrar_etiquetas
                                    else None
                                ),
                                textposition="top center",
                                customdata=d[
                                    [
                                        "Edad Sem + Días",
                                        "Gr. A. D. Tabla",
                                        "Html_Dif_Consumo",
                                    ]
                                ],
                                hovertemplate=(
                                    "<b>Galpón "
                                    f"{g}</b><br><b>Sem:</b>"
                                    " %{customdata[0]}<br><b>Real:</b>"
                                    " %{y:.1f}g<br><b>Guía:</b>"
                                    " %{customdata[1]:.1f}g<br><b>Dif:</b>"
                                    " %{customdata[2]}<extra></extra>"
                                ),
                            )
                        )
                    fig.add_trace(
                        go.Scatter(
                            x=guia_lote["Fecha"],
                            y=guia_lote["Gr. A. D. Tabla"],
                            name=f"Tabla ({linea_genetica})",
                            line=dict(color="#D97706", dash="dash", width=2.5),
                            customdata=guia_lote[["Hover_Cons_Multi"]],
                            hovertemplate=(
                                "<b>Guía Tabla Lote:</b>"
                                " %{y:.1f}g<br><br>%{customdata[0]}<extra></extra>"
                            ),
                        )
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=df_input["Fecha"],
                            y=df_input["Consumo Gr. A. D."],
                            name="Real",
                            line=dict(color="#2980B9", width=3.5),
                            mode=modo_grafico,
                            text=(
                                df_input["Consumo Gr. A. D."].map(
                                    "{:.1f}g".format
                                )
                                if mostrar_etiquetas
                                else None
                            ),
                            textposition="top center",
                            customdata=df_input[
                                [
                                    "Edad Sem + Días",
                                    "Gr. A. D. Tabla",
                                    "Html_Dif_Consumo",
                                ]
                            ],
                            hovertemplate=(
                                "<b>Sem:</b> %{customdata[0]}<br><b>Real:</b>"
                                " %{y:.1f}g<br><b>Guía:</b>"
                                " %{customdata[1]:.1f}g<br><b>Dif:</b>"
                                " %{customdata[2]}<extra></extra>"
                            ),
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df_input["Fecha"],
                            y=df_input["Gr. A. D. Tabla"],
                            name=f"Guía ({linea_genetica})",
                            line=dict(color="#D97706", dash="dash", width=2),
                            hovertemplate="<b>Guía:</b> %{y:.1f}g<extra></extra>",
                        )
                    )

                fig.update_layout(layout_comun)
                fig.update_layout(yaxis=dict(ticksuffix="g"))
                st.plotly_chart(fig, use_container_width=True)

        # 3. BAJAS / MORTALIDAD
        with row2_c1:
            with st.container(border=True):
                st.markdown(
                    f"##### 💀 Bajas / Mortalidad Día {title_suffix}",
                    help=(
                        "Mortalidad diaria en aves. Picos súbitos indican"
                        " problemas ambientales; aumentos progresivos sugieren"
                        " alerta patológica."
                    ),
                )
                fig = go.Figure()

                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input["Galpón"] == g].sort_values(
                            "Fecha"
                        )
                        fig.add_trace(
                            go.Bar(
                                x=d["Fecha"],
                                y=d["Mort."],
                                name=f"G{g}",
                                marker_color=color_map[g],
                                text=d["Mort."] if mostrar_etiquetas else None,
                                textposition="auto",
                                customdata=d[["Edad Sem + Días"]],
                                hovertemplate=(
                                    "<b>Galpón "
                                    f"{g}</b><br><b>Sem:</b>"
                                    " %{customdata[0]}<br><b>Bajas:</b>"
                                    " %{y:,.0f} aves<extra></extra>"
                                ),
                            )
                        )
                else:
                    fig.add_trace(
                        go.Bar(
                            x=df_input["Fecha"],
                            y=df_input["Mort."],
                            name="Mort.",
                            marker_color="#C0392B",
                            text=(
                                df_input["Mort."] if mostrar_etiquetas else None
                            ),
                            textposition="auto",
                            customdata=df_input[["Edad Sem + Días"]],
                            hovertemplate=(
                                "<b>Sem:</b> %{customdata[0]}<br><b>Bajas:</b>"
                                " %{y:,.0f} aves<extra></extra>"
                            ),
                        )
                    )

                fig.update_layout(layout_comun)
                fig.update_layout(barmode="group" if is_compare else "stack")
                st.plotly_chart(fig, use_container_width=True)

        # 4. CONVERSIÓN DIARIA
        with row2_c2:
            with st.container(border=True):
                st.markdown(
                    f"##### 🔄 Conversión Diario (g Alimento/Huevo) {title_suffix}",
                    help=(
                        "Eficiencia biológica (Gramos Alimento / % Postura)."
                        " Un número menor representa menor consumo para producir"
                        " cada huevo."
                    ),
                )
                fig = go.Figure()

                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input["Galpón"] == g].sort_values(
                            "Fecha"
                        )
                        d["Ef"] = (
                            d["Consumo Gr. A. D."]
                            / (d["% Diario de Prod."] / 100)
                        ).replace([float("inf"), -float("inf")], 0)
                        fig.add_trace(
                            go.Scatter(
                                x=d["Fecha"],
                                y=d["Ef"],
                                name=f"G{g}",
                                line=dict(color=color_map[g], width=2.5),
                                mode=modo_grafico,
                                text=(
                                    d["Ef"].map("{:.1f}".format)
                                    if mostrar_etiquetas
                                    else None
                                ),
                                textposition="top center",
                                customdata=d[["Edad Sem + Días"]],
                                hovertemplate=(
                                    "<b>Galpón "
                                    f"{g}</b><br><b>Sem:</b>"
                                    " %{customdata[0]}<br><b>Conversión:</b>"
                                    " %{y:.1f} pts<extra></extra>"
                                ),
                            )
                        )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=df_input["Fecha"],
                            y=df_input["Ef"],
                            name="Conversión",
                            line=dict(color="#8E44AD", width=3.5),
                            mode=modo_grafico,
                            text=(
                                df_input["Ef"].map("{:.1f}".format)
                                if mostrar_etiquetas
                                else None
                            ),
                            textposition="top center",
                            customdata=df_input[["Edad Sem + Días"]],
                            hovertemplate=(
                                "<b>Sem:</b>"
                                " %{customdata[0]}<br><b>Conversión:</b>"
                                " %{y:.1f} pts<extra></extra>"
                            ),
                        )
                    )

                fig.update_layout(layout_comun)
                st.plotly_chart(fig, use_container_width=True)

    # --- 7. PESTAÑAS Y DISPOSICIÓN FINAL ---
    tabs = st.tabs(
        ["🌐 COMPARATIVO TOTAL"] + [f"🏠 Galpón {g}" for g in lista_galpones]
    )

    # Vista 0: Comparativo de Galpones + Guía Lote
    with tabs[0]:
        df_c = df_f_l[
            (df_f_l["Fecha"] >= rango[0]) & (df_f_l["Fecha"] <= rango[1])
        ].copy()
        render_4_charts(df_c, "(Consolidado)", is_compare=True)

    # Vistas 1 en adelante: Galpones individuales
    for i, g_id in enumerate(lista_galpones):
        with tabs[i + 1]:
            df_i = df_f_l[
                (df_f_l["Galpón"] == g_id)
                & (df_f_l["Fecha"] >= rango[0])
                & (df_f_l["Fecha"] <= rango[1])
            ].sort_values("Fecha")
            render_4_charts(df_i, f"(Galpón {g_id})", is_compare=False)

else:
    st.error("No se encontraron datos para la empresa actual.")
import base64
import io
import os
import pandas as pd
import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="HUPA | Bitácora Maestra",
    page_icon="📋",
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

    /* ESTILOS DE TABLA (DATAFRAME) CENTRADA Y ALTURAS */
    [data-testid="stDataFrame"] div[data-testid="stHeaderCell"] {
        height: 52px !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }
    [data-testid="stDataFrame"] div[data-testid="stHeaderCell"] p {
        text-align: center !important;
        font-weight: bold !important;
        font-size: 0.82rem !important;
        white-space: normal !important;
        line-height: 1.15 !important;
    }
    [data-testid="stDataFrame"] div[role="gridcell"] {
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }
    [data-testid="stDataFrame"] div[role="gridcell"] p {
        text-align: center !important;
        width: 100% !important;
        font-size: 0.85rem !important;
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
        lista_granjas = sorted(
            [
                g
                for g in granjas_unicas
                if g not in [0, "0", "0.0", "None", None]
            ]
        )
        granja_sel = st.selectbox("🏘️ Granja", lista_granjas)

    with c_lote:
        df_f_g = df_empresa[
            df_empresa["Nombre de Granja (P) :"] == granja_sel
        ]
        lote_sel = st.selectbox(
            "🆔 Lote", sorted(df_f_g["Número de Lote :"].unique())
        )

    df_f_l = df_f_g[df_f_g["Número de Lote :"] == lote_sel].copy()

    min_f = df_f_l["Fecha"].min()
    max_f = df_f_l["Fecha"].max()
    f_cierre = max_f - pd.Timedelta(days=1) if max_f > min_f else max_f

    opciones_looker = [
        "Últimos 7 días",
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
        with st.expander("🔍 Información Conceptual del Lote", expanded=True):
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

    # --- 7. PESTAÑAS Y TABLAS ---
    lista_galpones = sorted(
        [g for g in df_f_l["Galpón"].unique() if g not in [0, "0", None]]
    )

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

        def style_dif(row):
            styles = ["text-align: center;"] * len(row)
            idx_g = row.index.get_loc("Dif Gr Ave")
            idx_p = row.index.get_loc("Dif Pdn")
            idx_h = row.index.get_loc("Dif Huevos")

            if row["Dif Gr Ave"] > 1.5:
                styles[idx_g] = (
                    "background-color: #FEF5E7; color: #B9770E; font-weight:"
                    " bold; text-align: center;"
                )
            elif row["Dif Gr Ave"] < -1.5:
                styles[idx_g] = (
                    "background-color: #E8F8F5; color: #117A65; font-weight:"
                    " bold; text-align: center;"
                )

            if row["Dif Pdn"] < -1.0:
                styles[idx_p] = (
                    "background-color: #FDEDEC; color: #A93226; font-weight:"
                    " bold; text-align: center;"
                )
            elif row["Dif Pdn"] > 1.5:
                styles[idx_p] = (
                    "background-color: #E8F8F5; color: #117A65; font-weight:"
                    " bold; text-align: center;"
                )

            if row["Dif Huevos"] > 0:
                styles[idx_h] = (
                    "background-color: #E8F8F5; color: #117A65; font-weight:"
                    " bold; text-align: center;"
                )
            elif row["Dif Huevos"] < 0:
                styles[idx_h] = (
                    "background-color: #FDEDEC; color: #A93226; font-weight:"
                    " bold; text-align: center;"
                )

            return styles

        config_columnas_centradas = {
    "Fecha": st.column_config.DateColumn(
        "Fecha",
        format="DD/MM/YY",
        alignment="center",
        help="Fecha del registro diario en granja",
    ),
    "Edad Sem + Días": st.column_config.TextColumn(
        "Edad Sem + Días",
        alignment="center",
        help="Edad biológica de las aves (Semanas + Días)",
    ),
    "Mort.": st.column_config.NumberColumn(
        "Mort.",
        format="%d",
        alignment="center",
        help="Mortalidad acumulada del día (Bajas)",
    ),
    "Saldo Aves": st.column_config.NumberColumn(
        "Saldo Total",
        format="%d",
        alignment="center",
        help="Aves vivas alojadas al cierre de la jornada",
    ),
    "Consumo Gr. A. D.": st.column_config.NumberColumn(
        "Consumo Gr.",
        format="%.1f",
        alignment="center",
        help="Gramos de alimento consumido por ave al día (Real)",
    ),
    "Gr. A. D. Tabla": st.column_config.NumberColumn(
        "Gr. A. D.",
        format="%.1f",
        alignment="center",
        help="Gramos de alimento recomendados según la Guía Técnica",
    ),
    "Dif Gr Ave": st.column_config.NumberColumn(
        "Dif Gr",
        format="%.2f",
        alignment="center",
        help=(
            "Diferencia de alimento (Real - Tabla). Positivo = Sobreconsumo /"
            " Negativo = Ahorro"
        ),
    ),
    "Producción Huevos Día": st.column_config.NumberColumn(
        "Prod. Huevos",
        format="%d",
        alignment="center",
        help="Total de huevos recolectados en el día",
    ),
    "Dif Huevos": st.column_config.NumberColumn(
        "Dif Huevos Día",
        format="%+d",
        alignment="center",
        help="Balance de huevos frente a la meta esperada de la tabla",
    ),
    "% Diario de Prod.": st.column_config.NumberColumn(
        "% Prod.",
        format="%.2f%%",
        alignment="center",
        help="Porcentaje real de postura diaria (Huevos / Saldo Aves)",
    ),
    "% Dia Prod. Tab": st.column_config.NumberColumn(
        "% Dia Tab",
        format="%.2f%%",
        alignment="center",
        help="Porcentaje teórico de postura esperado según la Guía Genética",
    ),
    "Dif Pdn": st.column_config.NumberColumn(
        "Dif %",
        format="%.2f%%",
        alignment="center",
        help=(
            "Diferencia porcentual de postura frente a la guía (Real - Tabla)"
        ),
    ),
    "Conv Diaria": st.column_config.NumberColumn(
        "Conv. Diaria",
        format="%.2f",
        alignment="center",
        help="Conversión alimenticia en puntos (Gramos de Alimento / Huevo)",
    ),
    "Consumo Calcio Gr. A. D.": st.column_config.NumberColumn(
        "Consumo Calcio",
        format="%.1f",
        alignment="center",
        help="Gramos de calcio/carbonato adicional suplementado por ave",
    ),
    "Consumo B X 40 K": st.column_config.NumberColumn(
        "Consumo Bx40",
        format="%d",
        alignment="center",
        help="Bultos de alimento de 40 kg consumidos en el día",
    ),
    "Observaciones": st.column_config.TextColumn(
        "Observaciones",
        alignment="center",
        help="Novedades de manejo, clima, sanidad o bitácora de campo",
    ),
}

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

            st.dataframe(
                df_vista_gen[cols].style.apply(style_dif, axis=1),
                use_container_width=True,
                hide_index=True,
                column_config=config_columnas_centradas,
            )

            st.markdown("---")
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

                col_izq, col_centro, col_der = st.columns([0.05, 0.90, 0.05])
                with col_centro:
                    st.markdown(
                        "##### 📊 Resumen de Totales y Promedios -"
                        " Consolidado de Lote"
                    )
                    st.markdown(tabla_html_g, unsafe_allow_html=True)

                    buffer_g = io.BytesIO()
                    with pd.ExcelWriter(
                        buffer_g, engine="xlsxwriter"
                    ) as writer:
                        df_vista_gen[cols].to_excel(writer, index=False)

                    st.download_button(
                        label=(
                            "📥 Descargar Excel Consolidado Lote"
                            f" {lote_sel}"
                        ),
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

                st.dataframe(
                    df_vista[cols].style.apply(style_dif, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    column_config=config_columnas_centradas,
                )

                st.markdown("---")
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

                    col_izq, col_centro, col_der = st.columns(
                        [0.05, 0.90, 0.05]
                    )
                    with col_centro:
                        st.markdown(
                            "##### 📊 Resumen de Totales y Promedios -"
                            f" Galpón {galpon_actual}"
                        )
                        st.markdown(tabla_html, unsafe_allow_html=True)

                        buffer = io.BytesIO()
                        with pd.ExcelWriter(
                            buffer, engine="xlsxwriter"
                        ) as writer:
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
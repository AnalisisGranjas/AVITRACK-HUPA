import base64
import io
import os
import re
import pandas as pd
import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="HUPA | Informe de Nómina",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- FUNCIÓN DE ORDENAMIENTO NATURAL ---
def orden_num_natural(lista):
    def clave(texto):
        return [
            int(c) if c.isdigit() else str(c).lower()
            for c in re.split(r"(\d+)", str(texto))
        ]

    return sorted(lista, key=clave)


# --- LOGO EN BASE64 ---
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

# --- 2. ESTILOS CSS AGROTECH CLEAN & EXECUTIVE ---
st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
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
    }
    .app-header-text p {
        color: #E8F8F5 !important;
        margin: 4px 0 0 0 !important;
        font-size: clamp(0.75rem, 1.5vw, 0.9rem) !important;
        opacity: 0.9;
    }
    .filter-panel {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 16px 20px 10px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .table-container {
        max-height: 600px;
        overflow-y: auto;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        background-color: var(--secondary-background-color);
    }
    .nomina-table {
        width: 100%;
        border-collapse: collapse;
        font-family: inherit;
        font-size: 0.88rem;
        color: var(--text-color);
    }
    .nomina-table th {
        position: sticky;
        top: 0;
        background-color: #0F5132 !important;
        color: #FFFFFF !important;
        padding: 10px 12px;
        text-align: center;
        font-weight: 700;
        border-bottom: 2px solid rgba(0,0,0,0.1);
        z-index: 2;
    }
    .nomina-table td {
        padding: 8px 12px;
        text-align: center;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15);
        white-space: nowrap;
    }
    .nomina-table tr:hover {
        background-color: rgba(17, 122, 101, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. VALIDACIÓN DE SESIÓN ---
if "auth" not in st.session_state or not st.session_state.auth:
    st.switch_page("app.py")
    st.stop()


# --- 4. CARGA DE DATOS ---
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

        cols_str = [
            "Nombre de Granja (P) :",
            "Número de Lote :",
            "Galpón",
            "Ubicación",
            "Línea :",
        ]
        for col in cols_str:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()


df_raw = load_data()
df_empresa = df_raw[df_raw["Razon Social"] == st.session_state.user].copy()

# BANNER CABECERA
st.markdown(
    f"""
    <div class="app-header">
        {logo_html}
        <div class="app-header-text">
            <h1>Informe de Nómina por Galpón</h1>
            <p>Consolidado ejecutivo de aves, mortalidad acumulada y balance de producción por rango de fechas</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not df_empresa.empty:
    # --- 5. PANEL DE FILTROS ---
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    c_periodo, c_granja = st.columns([2, 1])

    min_f_global = df_empresa["Fecha"].min()
    max_f_global = df_empresa["Fecha"].max()
    f_cierre_def = (
        max_f_global - pd.Timedelta(days=1)
        if max_f_global > min_f_global
        else max_f_global
    )

    opciones_periodo = [
        "Últimos 7 días",
        "Últimos 15 días",
        "Últimos 30 días",
        "Este mes",
        "Mes pasado",
        "Todo el historial",
        "Personalizado",
    ]

    with c_periodo:
        periodo_sel = st.selectbox(
            "📅 Período de Tiempo", opciones_periodo, index=1
        )

    if periodo_sel == "Últimos 7 días":
        fecha_ini = max(f_cierre_def - pd.Timedelta(days=6), min_f_global)
        rango_fechas = (fecha_ini, f_cierre_def)
    elif periodo_sel == "Últimos 15 días":
        fecha_ini = max(f_cierre_def - pd.Timedelta(days=14), min_f_global)
        rango_fechas = (fecha_ini, f_cierre_def)
    elif periodo_sel == "Últimos 30 días":
        fecha_ini = max(f_cierre_def - pd.Timedelta(days=29), min_f_global)
        rango_fechas = (fecha_ini, f_cierre_def)
    elif periodo_sel == "Este mes":
        fecha_ini = max(f_cierre_def.replace(day=1), min_f_global)
        rango_fechas = (fecha_ini, f_cierre_def)
    elif periodo_sel == "Mes pasado":
        primer_dia_mes = f_cierre_def.replace(day=1)
        ultimo_dia_mes_ant = primer_dia_mes - pd.Timedelta(days=1)
        primer_dia_mes_ant = ultimo_dia_mes_ant.replace(day=1)
        rango_fechas = (
            max(primer_dia_mes_ant, min_f_global),
            min(ultimo_dia_mes_ant, max_f_global),
        )
    elif periodo_sel == "Todo el historial":
        rango_fechas = (min_f_global, max_f_global)
    elif periodo_sel == "Personalizado":
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            d_desde = st.date_input(
                "Desde:",
                value=min_f_global,
                min_value=min_f_global,
                max_value=max_f_global,
                format="DD/MM/YYYY",
            )
        with col_f2:
            d_hasta = st.date_input(
                "Hasta:",
                value=max_f_global,
                min_value=min_f_global,
                max_value=max_f_global,
                format="DD/MM/YYYY",
            )

        if d_desde > d_hasta:
            st.error("⚠️ La fecha 'Desde' no puede ser mayor que 'Hasta'.")
            rango_fechas = (min_f_global, max_f_global)
        else:
            rango_fechas = (d_desde, d_hasta)

    with c_granja:
        granjas_disp = orden_num_natural([
            g
            for g in df_empresa["Nombre de Granja (P) :"].unique()
            if g not in [0, "0", "0.0", "None", None]
        ])
        filtro_granja = st.selectbox(
            "🏘️ Filtrar Granja", ["Todas las Granjas"] + granjas_disp
        )

    st.caption(
        f"📆 **Rango Consultado:** {rango_fechas[0].strftime('%d/%m/%Y')} al"
        f" {rango_fechas[1].strftime('%d/%m/%Y')}"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # --- 6. FILTRADO Y CONSTRUCCIÓN DEL INFORME ---
    df_filtrado = df_empresa[
        (df_empresa["Fecha"] >= rango_fechas[0])
        & (df_empresa["Fecha"] <= rango_fechas[1])
    ].copy()

    if filtro_granja != "Todas las Granjas":
        df_filtrado = df_filtrado[
            df_filtrado["Nombre de Granja (P) :"] == filtro_granja
        ]

    if not df_filtrado.empty:
        filas_nomina = []

        grupos = df_filtrado.groupby(
            ["Nombre de Granja (P) :", "Número de Lote :", "Galpón"],
            sort=False,
        )

        for (granja, lote, galpon), df_g in grupos:
            # 1. Aves en la fecha máxima del periodo en este galpón
            fecha_max_galpon = df_g["Fecha"].max()
            df_max = df_g[df_g["Fecha"] == fecha_max_galpon]
            aves_saldo = (
                df_max["Saldo Aves"].values[0] if not df_max.empty else 0
            )

            # 2. Mortalidad acumulada en el periodo
            mortalidad_total = df_g["Mort."].sum()

            # 3. % Prod Real y % Prod Tabla promedio
            dias_con_datos = df_g[df_g["Saldo Aves"] > 0]
            if not dias_con_datos.empty:
                prod_real_prom = dias_con_datos["% Diario de Prod."].mean()
                prod_tab_prom = dias_con_datos["% Dia Prod. Tab"].mean()
            else:
                prod_real_prom = 0.0
                prod_tab_prom = 0.0

            # 4. Diferencia
            diferencia = prod_real_prom - prod_tab_prom

            filas_nomina.append({
                "Granja": granja,
                "Lote": lote,
                "Galpón": galpon,
                "Aves": aves_saldo,
                "Mortalidad": mortalidad_total,
                "% Prod Real": prod_real_prom,
                "% Prod Tabla": prod_tab_prom,
                "Diferencia": diferencia,
            })

        df_nomina = pd.DataFrame(filas_nomina)

        # Ordenar naturalmente por Granja, Lote y Galpón
        df_nomina["_ord_g"] = df_nomina["Galpón"].apply(
            lambda x: int(re.search(r"\d+", str(x)).group())
            if re.search(r"\d+", str(x))
            else 999
        )
        df_nomina = df_nomina.sort_values(
            by=["Granja", "Lote", "_ord_g"]
        ).drop(columns=["_ord_g"])

        # --- 7. TARJETAS DE TOTALES GLOBALES ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("🐔 Total Aves Activas", f"{df_nomina['Aves'].sum():,.0f}")
        kpi2.metric(
            "💀 Total Mortalidad Periodo",
            f"{df_nomina['Mortalidad'].sum():,.0f}",
        )
        kpi3.metric(
            "📈 % Prod Real Promedio", f"{df_nomina['% Prod Real'].mean():.1f}%"
        )
        dif_global = (
            df_nomina["% Prod Real"].mean() - df_nomina["% Prod Tabla"].mean()
        )
        kpi4.metric(
            "🎯 Diferencia Promedio",
            f"{dif_global:+.1f}%",
            delta=f"{dif_global:+.1f}%",
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # --- 8. RENDERIZAR TABLA HTML CON FORMATO CONDICIONAL ---
        filas_html = []
        for _, row in df_nomina.iterrows():
            dif = row["Diferencia"]
            if dif >= 0:
                dif_style = "color: #117A65; font-weight: bold;"
                dif_str = f"+{dif:.1f}"
            else:
                dif_style = "color: #C0392B; font-weight: bold;"
                dif_str = f"{dif:.1f}"

            filas_html.append(
                f'<tr>'
                f'<td style="text-align: left; font-weight: 600;">{row["Granja"]}</td>'
                f'<td>{row["Lote"]}</td>'
                f'<td>{row["Galpón"]}</td>'
                f'<td style="font-weight: 600;">{row["Aves"]:,.0f}</td>'
                f'<td>{row["Mortalidad"]:,.0f}</td>'
                f'<td>{row["% Prod Real"]:.1f}%</td>'
                f'<td>{row["% Prod Tabla"]:.1f}%</td>'
                f'<td style="{dif_style}">{dif_str}%</td>'
                f'</tr>'
            )

        cuerpo_tabla = "".join(filas_html)

        html_t = (
            '<div class="table-container">'
            '<table class="nomina-table">'
            '<thead><tr>'
            '<th>Granja</th>'
            '<th>Lote</th>'
            '<th>Galpón</th>'
            '<th>Aves</th>'
            '<th>Mortalidad</th>'
            '<th>% Prod Real</th>'
            '<th>% Prod Tabla</th>'
            '<th>Diferencia</th>'
            '</tr></thead>'
            f'<tbody>{cuerpo_tabla}</tbody>'
            '</table>'
            '</div>'
        )

        st.markdown(html_t, unsafe_allow_html=True)

        # --- 9. EXPORTACIÓN A EXCEL CON ESTILOS ---
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine="xlsxwriter") as writer:
            df_export = df_nomina.copy()
            df_export.to_excel(writer, index=False, sheet_name="Informe Nomina")
            workbook = writer.book
            worksheet = writer.sheets["Informe Nomina"]

            fmt_header = workbook.add_format({
                "bold": True,
                "bg_color": "#0F5132",
                "font_color": "#FFFFFF",
                "align": "center",
                "border": 1,
            })
            for col_num, col_val in enumerate(df_export.columns):
                worksheet.write(0, col_num, col_val, fmt_header)
                worksheet.set_column(col_num, col_num, 16)

            fmt_verde = workbook.add_format(
                {"font_color": "#117A65", "bold": True}
            )
            fmt_rojo = workbook.add_format(
                {"font_color": "#C0392B", "bold": True}
            )

            max_row = len(df_export)
            worksheet.conditional_format(
                1,
                7,
                max_row,
                7,
                {
                    "type": "cell",
                    "criteria": ">=",
                    "value": 0,
                    "format": fmt_verde,
                },
            )
            worksheet.conditional_format(
                1,
                7,
                max_row,
                7,
                {
                    "type": "cell",
                    "criteria": "<",
                    "value": 0,
                    "format": fmt_rojo,
                },
            )

        f_ini_str = rango_fechas[0].strftime("%d-%m-%Y")
        f_fin_str = rango_fechas[1].strftime("%d-%m-%Y")

        st.download_button(
            label="📥 Descargar Informe de Nómina (Excel)",
            data=buffer_excel.getvalue(),
            file_name=f"Informe_Nomina_{f_ini_str}_al_{f_fin_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    else:
        st.warning(
            "No se encontraron registros para los filtros y fechas seleccionadas."
        )

else:
    st.error("No se encontraron datos para la empresa actual.")
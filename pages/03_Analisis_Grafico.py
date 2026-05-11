import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="HUPA | Análisis Gráfico", layout="wide")

# --- 2. VALIDACIÓN DE SESIÓN ---
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("app.py")
    st.stop()

# --- 3. CARGA DE DATOS ---
@st.cache_data
def load_data():
    path = os.path.join("DATA", "REPORTE_AVITRACK_FINAL.xlsx")
    if os.path.exists(path):
        df = pd.read_excel(path)
        df = df.fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True).dt.date
        df['Edad Sem + Días'] = df['Edad Sem + Días'].astype(str).str.replace("'", "")
        # Limpieza de nombres de columnas
        columnas_filtro = ['Nombre de Granja (P) :', 'Número de Lote :', 'Galpón']
        for col in columnas_filtro:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_raw = load_data()
df_empresa = df_raw[df_raw['Razon Social'] == st.session_state.user].copy()

st.title("📈 Dashboard de Análisis y Tendencias")

if not df_empresa.empty:
    # --- 4. FILTROS PRINCIPALES ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        lista_granjas = sorted([g for g in df_empresa['Nombre de Granja (P) :'].unique() if pd.notna(g)])
        granja_sel = st.selectbox("🏘️ Granja", lista_granjas)
    with c2:
        df_f_g = df_empresa[df_empresa['Nombre de Granja (P) :'] == granja_sel]
        lista_lotes = sorted([l for l in df_f_g['Número de Lote :'].unique() if pd.notna(l)])
        lote_sel = st.selectbox("🆔 Lote", lista_lotes)
    with c3:
        st.write(" ") # Espaciador
        mostrar_etiquetas = st.toggle("🏷️ Mostrar números en gráficas", value=False)

    # --- 5. FILTROS DE FECHA (REFERENCIA HOY-1) ---
    df_f_l = df_f_g[df_f_g['Número de Lote :'] == lote_sel]
    hoy_ref = datetime.date.today() - datetime.timedelta(days=1)
    min_f = df_f_l['Fecha'].min()

    cf1, cf2 = st.columns([1, 2])
    with cf1:
        filtro_rapido = st.radio("🔎 Rango de visualización:", ["Últimos 7 días", "Últimos 15 días", "Últimos 30 días", "Ver Todo"], horizontal=True)
    with cf2:
        if filtro_rapido == "Últimos 7 días": rango = (max(hoy_ref - datetime.timedelta(days=7), min_f), hoy_ref)
        elif filtro_rapido == "Últimos 15 días": rango = (max(hoy_ref - datetime.timedelta(days=15), min_f), hoy_ref)
        elif filtro_rapido == "Últimos 30 días": rango = (max(hoy_ref - datetime.timedelta(days=30), min_f), hoy_ref)
        else: rango = (min_f, hoy_ref)
        st.info(f"📅 Graficando: {rango[0].strftime('%d/%m/%Y')} al {rango[1].strftime('%d/%m/%Y')}")

    st.divider()

    # --- 6. LÓGICA DE RENDERIZADO DE GRÁFICOS ---
    lista_galpones = sorted([g for g in df_f_l['Galpón'].unique() if g not in [0, "0", None]])
    modo_grafico = "lines+markers+text" if mostrar_etiquetas else "lines+markers"

    def render_4_charts(df_input, title_suffix, is_compare=False):
        # Preparar cálculos
        df_input = df_input.copy()
        df_input['Semana_Anio'] = pd.to_datetime(df_input['Fecha']).dt.isocalendar().week
        df_input['Ef'] = (df_input['Consumo Gr. A. D.'] / (df_input['% Diario de Prod.'] / 100)).replace([float('inf')], 0)
        
        row1_c1, row1_c2 = st.columns(2)
        row2_c1, row2_c2 = st.columns(2)

        # 1. POSTURA
        with row1_c1:
            with st.container(border=True):
                st.markdown(f"#### 🥚 Postura {title_suffix}")
                fig = go.Figure()
                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input['Galpón'] == g].sort_values('Fecha')
                        fig.add_trace(go.Scatter(x=d['Fecha'], y=d['% Diario de Prod.'], name=f"G{g}", mode=modo_grafico, text=d['% Diario de Prod.'].map("{:.1f}".format) if mostrar_etiquetas else None, textposition="top center"))
                else:
                    fig.add_trace(go.Scatter(x=df_input['Fecha'], y=df_input['% Diario de Prod.'], name='Real', line=dict(color='#00CC96', width=4), mode=modo_grafico, text=df_input['% Diario de Prod.'].map("{:.1f}%".format) if mostrar_etiquetas else None, textposition="top center",
                        hovertemplate="<b>EDAD:</b> "+df_input['Edad Sem + Días']+"<br><b>SEM:</b> "+df_input['Semana_Anio'].astype(str)+"<br><b>REAL:</b> %{y:.2f}%<br><b>GUÍA:</b> "+df_input['Pond. % Prod.'].map("{:.2f}%".format)+"<br><b>DIF:</b> "+(df_input['% Diario de Prod.']-df_input['Pond. % Prod.']).map("{:+.2f}%".format)+"<extra></extra>"))
                    fig.add_trace(go.Scatter(x=df_input['Fecha'], y=df_input['Pond. % Prod.'], name='Guía', line=dict(color='red', dash='dash'), hoverinfo="skip"))
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

        # 2. CONSUMO
        with row1_c2:
            with st.container(border=True):
                st.markdown(f"#### 🥣 Consumo {title_suffix}")
                fig = go.Figure()
                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input['Galpón'] == g].sort_values('Fecha')
                        fig.add_trace(go.Scatter(x=d['Fecha'], y=d['Consumo Gr. A. D.'], name=f"G{g}", mode=modo_grafico, text=d['Consumo Gr. A. D.'].map("{:.0f}".format) if mostrar_etiquetas else None, textposition="top center"))
                else:
                    fig.add_trace(go.Scatter(x=df_input['Fecha'], y=df_input['Consumo Gr. A. D.'], name='Real', line=dict(color='#636EFA', width=4), mode=modo_grafico, text=df_input['Consumo Gr. A. D.'].map("{:.1f}".format) if mostrar_etiquetas else None, textposition="top center",
                        hovertemplate="<b>REAL:</b> %{y:.1f}g<br><b>GUÍA:</b> "+df_input['Pond. Gr. Ave Dia'].map("{:.1f}g".format)+"<br><b>DIF:</b> "+(df_input['Consumo Gr. A. D.']-df_input['Pond. Gr. Ave Dia']).map("{:+.1f}g".format)+"<extra></extra>"))
                    fig.add_trace(go.Scatter(x=df_input['Fecha'], y=df_input['Pond. Gr. Ave Dia'], name='Guía', line=dict(color='orange', dash='dash'), hoverinfo="skip"))
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

        # 3. MORTALIDAD
        with row2_c1:
            with st.container(border=True):
                st.markdown(f"#### 💀 Mortalidad {title_suffix}")
                fig = go.Figure()
                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input['Galpón'] == g].sort_values('Fecha')
                        fig.add_trace(go.Bar(x=d['Fecha'], y=d['Mort.'], name=f"G{g}", text=d['Mort.'] if mostrar_etiquetas else None, textposition='auto'))
                else:
                    fig.add_trace(go.Bar(x=df_input['Fecha'], y=df_input['Mort.'], name='Bajas', marker_color='#EF553B', text=df_input['Mort.'] if mostrar_etiquetas else None, textposition='auto'))
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), barmode='stack', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

        # 4. EFICIENCIA
        with row2_c2:
            with st.container(border=True):
                st.markdown(f"#### 📉 Eficiencia {title_suffix}")
                fig = go.Figure()
                if is_compare:
                    for g in lista_galpones:
                        d = df_input[df_input['Galpón'] == g].sort_values('Fecha')
                        d['Ef'] = (d['Consumo Gr. A. D.'] / (d['% Diario de Prod.'] / 100)).replace([float('inf')], 0)
                        fig.add_trace(go.Scatter(x=d['Fecha'], y=d['Ef'], name=f"G{g}", mode=modo_grafico, text=d['Ef'].map("{:.2f}".format) if mostrar_etiquetas else None, textposition="top center"))
                else:
                    fig.add_trace(go.Scatter(x=df_input['Fecha'], y=df_input['Ef'], name='g Alimento/Huevo', line=dict(color='#AB63FA', width=3), mode=modo_grafico, text=df_input['Ef'].map("{:.2f}".format) if mostrar_etiquetas else None, textposition="top center",
                        hovertemplate="<b>EDAD:</b> "+df_input['Edad Sem + Días']+"<br><b>CONV:</b> %{y:.2f} g/huevo<extra></extra>"))
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

    # --- 7. TABS ---
    tabs = st.tabs(["🌍 COMPARATIVO TOTAL"] + [f"🏠 Galpón {g}" for g in lista_galpones])

    with tabs[0]:
        df_c = df_f_l[(df_f_l['Fecha'] >= rango[0]) & (df_f_l['Fecha'] <= rango[1])].copy()
        render_4_charts(df_c, "(Lote)", is_compare=True)

    for i, g_id in enumerate(lista_galpones):
        with tabs[i+1]:
            df_i = df_f_l[(df_f_l['Galpón'] == g_id) & (df_f_l['Fecha'] >= rango[0]) & (df_f_l['Fecha'] <= rango[1])].sort_values('Fecha')
            render_4_charts(df_i, f"(G{g_id})")

else:
    st.error("No se encontraron datos.")
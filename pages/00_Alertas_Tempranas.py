import streamlit as st
import pandas as pd
import os
import datetime

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    path = os.path.join("DATA", "REPORTE_AVITRACK_FINAL.xlsx")
    if os.path.exists(path):
        df = pd.read_excel(path)
        df = df.fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True).dt.date
        for col in ['Nombre de Granja (P) :','Número de Lote :', 'Galpón']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_raw = load_data()
df_empresa = df_raw[df_raw['Razon Social'] == st.session_state.user].copy()

st.title("🚨 Panel de Alertas y Eficiencia")

if not df_empresa.empty:
    # --- 2. LÓGICA DE FECHAS (AYER vs ANTIER) ---
    hoy = datetime.date.today()
    ayer = hoy - datetime.timedelta(days=1)
    antier = hoy - datetime.timedelta(days=2)
    
    # Validación: si no hay datos de ayer, tomamos el último cierre disponible del Excel
    if ayer not in df_empresa['Fecha'].values:
        ayer = df_empresa['Fecha'].max()
        antier = ayer - datetime.timedelta(days=1)

    df_ayer = df_empresa[df_empresa['Fecha'] == ayer]
    df_ant = df_empresa[df_empresa['Fecha'] == antier]

    st.info(f"📊 Análisis de Cierre: **{ayer.strftime('%d/%m/%Y')}** (Ayer) vs **{antier.strftime('%d/%m/%Y')}** (Antier)")

    # --- 3. TABS POR GRANJA ---
    granjas = sorted(df_ayer['Nombre de Granja (P) :'].unique())
    tabs = st.tabs([f"🏘️ {g}" for g in granjas])

    for i, granja in enumerate(granjas):
        with tabs[i]:
            df_g_ayer = df_ayer[df_ayer['Nombre de Granja (P) :'] == granja]
            df_g_ant = df_ant[df_ant['Nombre de Granja (P) :'] == granja]
            
            lotes = sorted(df_g_ayer['Número de Lote :'].unique())

            for lote in lotes:
                st.markdown(f"### 🆔 Lote: {lote}")
                
                l_ayer = df_g_ayer[df_g_ayer['Número de Lote :'] == lote]
                l_ant = df_g_ant[df_g_ant['Número de Lote :'] == lote]

                # --- 4. ALERTAS PRIMERO (EL SEMÁFORO) ---
                alertas = []
                for _, row in l_ayer.iterrows():
                    dif_p = row['% Diario de Prod.'] - row['Pond. % Prod.']
                    if dif_p < -1.5: alertas.append(f"🔴 **G{row['Galpón']}**: Postura baja vs Tabla ({dif_p:.1f}%)")
                    if row['Mort.'] >= 5: alertas.append(f"💀 **G{row['Galpón']}**: Mortalidad alta ({row['Mort.']} aves)")

                if alertas:
                    with st.expander(f"⚠️ Alertas Críticas Detectadas", expanded=True):
                        for a in alertas: st.write(a)

                # --- 5. KPIs TÉCNICOS (AYER vs ANTIER) ---
                # Sincronizamos galpones para que el delta sea real
                g_hoy = set(l_ayer['Galpón'].unique())
                l_ant_c = l_ant[l_ant['Galpón'].isin(g_hoy)]

                # Cálculos Ayer
                saldo_y = l_ayer['Saldo Aves'].sum()
                mort_y = l_ayer['Mort.'].sum()
                p_y = l_ayer['% Diario de Prod.'].mean()
                p_meta = l_ayer['Pond. % Prod.'].mean()
                c_y = l_ayer['Consumo Gr. A. D.'].mean()
                c_meta = l_ayer['Pond. Gr. Ave Dia'].mean()
                # Conversión Ayer (CA = Consumo / (Postura/100))
                ca_y = (c_y / (p_y / 100)) if p_y > 0 else 0
                ca_meta = (c_meta / (p_meta / 100)) if p_meta > 0 else 0

                # Cálculos Antier
                mort_a = l_ant_c['Mort.'].sum()
                p_a = l_ant_c['% Diario de Prod.'].mean()
                c_a = l_ant_c['Consumo Gr. A. D.'].mean()
                ca_a = (c_a / (p_a / 100)) if p_a > 0 else 0

                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns(5)
                    
                    with c1:
                        # Saldo Solito
                        st.metric("Población Viva", f"{saldo_y:,.0f} aves")
                    
                    with c2:
                        # Mortalidad: Sube = Rojo (inverse)
                        st.metric("Mortalidad", f"{mort_y:.0f}", f"{mort_y - mort_a:+.0f} vs antier", delta_color="inverse")
                    
                    with c3:
                        # Postura: Sube = Verde
                        st.metric("Postura %", f"{p_y:.2f}%", f"{p_y - p_a:+.2f}% vs antier")
                        dif_p_t = p_y - p_meta
                        st.markdown(f":{'green' if dif_p_t >= 0 else 'red'}[{dif_p_t:+.2f}% vs Tabla]")
                    
                    with c4:
                        # Consumo: Sube = Rojo (inverse)
                        st.metric("Consumo g", f"{c_y:.1f}g", f"{c_y - c_a:+.1f}g vs antier", delta_color="inverse")
                        dif_c_t = c_y - c_meta
                        st.markdown(f":{'green' if abs(dif_c_t) <= 1.5 else 'orange'}[{dif_c_t:+.1f}g vs Tabla]")

                    with c5:
                        # Conversión: Sube = Rojo (inverse)
                        st.metric("CA (g/h)", f"{ca_y:.2f}", f"{ca_y - ca_a:+.2f} vs antier", delta_color="inverse")
                        dif_ca_t = ca_y - ca_meta
                        st.markdown(f":{'green' if dif_ca_t <= 0 else 'red'}[{dif_ca_t:+.2f} vs Tabla]")

                st.write("") 

else:
    st.error("No se encontraron datos cargados.")
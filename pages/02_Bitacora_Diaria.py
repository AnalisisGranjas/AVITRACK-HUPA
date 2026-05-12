import streamlit as st
import pandas as pd
import os
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="HUPA | Bitácora Maestra", layout="wide")

# --- 2. VALIDACIÓN DE SESIÓN ---
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("app.py")
    st.stop()

# --- 3. CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data
def load_data():
    path = os.path.join("DATA", "REPORTE_AVITRACK_FINAL.xlsx")
    if os.path.exists(path):
        df = pd.read_excel(path)
        df = df.fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True).dt.date
        df['Edad Sem + Días'] = df['Edad Sem + Días'].astype(str).str.replace("'", "")
        
        # Limpieza de nombres de columnas para evitar errores de espacios
        columnas_filtro = ['Nombre de Granja (P) :', 'Número de Lote :', 'Galpón', 'Ubicación', 'Línea :']
        for col in columnas_filtro:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_raw = load_data()
df_empresa = df_raw[df_raw['Razon Social'] == st.session_state.user].copy()

# --- 4. INTERFAZ Y FILTROS ---
st.title("📋 Bitácora Maestra de Campo")

if not df_empresa.empty:
    c1, c2, c3 = st.columns([1, 1, 1.5])
    with c1:
        granjas_unicas = df_empresa['Nombre de Granja (P) :'].unique()
        lista_granjas = [g for g in granjas_unicas if g not in [0, "0", "0.0", "None", None]]
        lista_granjas = sorted(lista_granjas)
        granja_sel = st.selectbox("🏘️ Granja", lista_granjas)
    with c2:
        df_f_g = df_empresa[df_empresa['Nombre de Granja (P) :'] == granja_sel]
        lote_sel = st.selectbox("🆔 Lote", sorted(df_f_g['Número de Lote :'].unique()))
    with c3:
        df_f_l = df_f_g[df_f_g['Número de Lote :'] == lote_sel]

    # --- DEFINICIÓN DE LÍMITES Y RANGO (CORRECCIÓN AQUÍ) ---
    min_f = df_f_l['Fecha'].min()
    max_f = df_f_l['Fecha'].max()
    
    # Inicialización por defecto para evitar NameError
    rango = (min_f, max_f)

    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        filtro_rapido = st.radio(
            "🔎 Vista rápida:",
            ["Últimos 7 días", "Últimos 30 días", "Ver Todo", "Personalizado"],
            horizontal=True,
            index=0 
        )

    with col_f2:
        if filtro_rapido == "Últimos 7 días":
            fecha_fin = max_f - pd.Timedelta(days=1)
            fecha_inicio = fecha_fin - pd.Timedelta(days=7)
            rango = (max(fecha_inicio, min_f), fecha_fin)
            st.info(f"📅 Mostrando cierre: {rango[0].strftime('%d/%m/%Y')} al {rango[1].strftime('%d/%m/%Y')}")

        elif filtro_rapido == "Últimos 30 días":
            fecha_fin = max_f - pd.Timedelta(days=1)
            fecha_inicio = fecha_fin - pd.Timedelta(days=30)
            rango = (max(fecha_inicio, min_f), fecha_fin)
            st.info(f"📅 Mostrando cierre: {rango[0].strftime('%d/%m/%Y')} al {rango[1].strftime('%d/%m/%Y')}")
            
        elif filtro_rapido == "Ver Todo":
            rango = (min_f, max_f)
            st.info("📅 Mostrando historial completo")
            
        else: # Personalizado
            rango = st.date_input("📅 Seleccione Rango:", value=(min_f, max_f), min_value=min_f, max_value=max_f)

    st.divider()

    # --- 5. INFO LOTE ---
    if not df_f_l.empty:
        info_lote = df_f_l.iloc[0]
        with st.expander("🔍 Información Conceptual del Lote", expanded=True):
            inf1, inf2, inf3, inf4 = st.columns(4)
            inf1.metric("📍 Ubicación", info_lote.get('Ubicación Granja (P) :', 'N/A'))
            inf2.metric("🧬 Línea Genética", info_lote.get('Línea de las Aves :', 'N/A'))
            inf3.metric("🐣 Fecha Inicio", min_f.strftime('%d/%m/%Y'))
            inf4.metric("🏠 Total Galpones", len(df_f_l['Galpón'].unique()))

    # --- 6. TABS DE GALPONES ---
    lista_galpones = sorted([g for g in df_f_l['Galpón'].unique() if g not in [0, "0", None]])

    if lista_galpones:
        tabs = st.tabs([f"🏠 Galpón {g}" for g in lista_galpones])

        for i, tab in enumerate(tabs):
            with tab:
                df_tab_base = df_f_l[df_f_l['Galpón'] == lista_galpones[i]].copy()
                
                # Cálculos
                df_tab_base['Dif Gr Ave'] = df_tab_base['Consumo Gr. A. D.'] - df_tab_base['Pond. Gr. Ave Dia']
                df_tab_base['Dif Pdn'] = df_tab_base['% Diario de Prod.'] - df_tab_base['Pond. % Prod.']
                df_tab_base['Conv Diaria'] = (df_tab_base['Consumo Gr. A. D.'] / (df_tab_base['% Diario de Prod.'] / 100)).replace([float('inf'), -float('inf')], 0).fillna(0)
                
                # Aplicar filtro de fecha sobre el galpón
                if isinstance(rango, tuple) and len(rango) == 2:
                    df_periodo = df_tab_base[(df_tab_base['Fecha'] >= rango[0]) & (df_tab_base['Fecha'] <= rango[1])].copy()
                else:
                    df_periodo = df_tab_base[df_tab_base['Fecha'] == rango].copy() if not isinstance(rango, tuple) else df_tab_base.copy()

                df_vista = df_periodo.sort_values(by='Fecha', ascending=False)

                # Estilos
                def style_dif(row):
                    styles = [''] * len(row)
                    idx_g = row.index.get_loc('Dif Gr Ave')
                    idx_p = row.index.get_loc('Dif Pdn')
                    if row['Dif Gr Ave'] > 1.5: styles[idx_g] = 'background-color: #FF6700; color: white;'
                    elif row['Dif Gr Ave'] < -1.5: styles[idx_g] = 'background-color: #2ECC71; color: white;'
                    if row['Dif Pdn'] < -1.0: styles[idx_p] = 'background-color: #FF6700; color: white;'
                    elif row['Dif Pdn'] > 1.5: styles[idx_p] = 'background-color: #2ECC71; color: white;'
                    return styles

                cols = ['Fecha', 'Edad Sem + Días', 'Mort.', 'Otros', 'Selec.', 'Saldo Aves', 
                        'Consumo Gr. A. D.', 'Pond. Gr. Ave Dia', 'Dif Gr Ave',
                        'Producción Huevos Día', '% Diario de Prod.', 'Pond. % Prod.', 'Dif Pdn', 
                        'Conv Diaria', 'Ingreso B X 40 K', 'Consumo B X 40 K', 'Saldo B X 40 K', 'Observaciones']

                # Render de Tabla con tus formatos originales
                st.dataframe(
                    df_vista[cols].style.apply(style_dif, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YY"),
                        "Mort.": st.column_config.NumberColumn("Mort.", format="%d"),
                        "Otros": st.column_config.NumberColumn("Otros", format="%d"),   
                        "Selec.": st.column_config.NumberColumn("Selec.", format="%d"),
                        "Saldo Aves": st.column_config.NumberColumn("Saldo", format="%d"),
                        "Consumo Gr. A. D.": st.column_config.NumberColumn("Consumo Gr.", format="%.1f"),
                        "Pond. Gr. Ave Dia": st.column_config.NumberColumn("Pond. Gr.", format="%.1f"),
                        "Dif Gr Ave": st.column_config.NumberColumn("Δ Gr", format="%.2f"),
                        "Producción Huevos Día": st.column_config.NumberColumn("Prod. Huevos", format="%d"),
                        "% Diario de Prod.": st.column_config.NumberColumn("% Prod.", format="%.2f%%"),
                        "Pond. % Prod.": st.column_config.NumberColumn("Pond. % Prod.", format="%.2f%%"),
                        "Dif Pdn": st.column_config.NumberColumn("Δ %", format="%.2f%%"),
                        "Conv Diaria": st.column_config.NumberColumn("Conv. Diaria", format="%.2f"),
                        "Ingreso B X 40 K": st.column_config.NumberColumn("Ingreso Bx40", format="%d"),
                        "Consumo B X 40 K": st.column_config.NumberColumn("Consumo Bx40", format="%d"),
                        "Saldo B X 40 K": st.column_config.NumberColumn("Saldo Bx40", format="%d"),
                    }
                )
                
# --- TABLA DE RESUMEN / TOTALES ---
                st.markdown("---")
                st.markdown("### 📊 Resumen de Totales y Promedios")

                if not df_periodo.empty:
                    # 1. CÁLCULOS
                    total_mort = df_periodo['Mort.'].sum()
                    total_huevos = df_periodo['Producción Huevos Día'].sum()
                    total_bultos = df_periodo['Consumo B X 40 K'].sum()

                    # Promedios reales (solo días con datos > 0)
                    dias_con_datos = df_periodo[df_periodo['Consumo Gr. A. D.'] > 0]
                    
                    if not dias_con_datos.empty:
                        p_real = dias_con_datos['% Diario de Prod.'].mean()
                        p_guia = dias_con_datos['Pond. % Prod.'].mean()
                        c_real = dias_con_datos['Consumo Gr. A. D.'].mean()
                        c_guia = dias_con_datos['Pond. Gr. Ave Dia'].mean()
                        conv_prom = dias_con_datos['Conv Diaria'].mean()
                        
                        # Diferencias
                        dif_p = p_real - p_guia
                        dif_c = c_real - c_guia
                    else:
                        p_real = p_guia = c_real = c_guia = conv_prom = dif_p = dif_c = 0

                    # 2. ESTRUCTURA DE LA TABLA (REAL | TABLA | DIF)
                    resumen_data = {
                        "Concepto": [
                            "💀 Mortalidad Acumulada", 
                            "🥚 Producción Total", 
                            "🌽 Alimento Consumido", 
                            "📈 Postura (Real | Guía | Dif)", 
                            "🥣 Consumo (Real | Guía | Dif)", 
                            "🔄 Conversión Promedio"
                        ],
                        "Valores del Periodo": [
                            f"{total_mort:,.0f} aves", 
                            f"{total_huevos:,.0f} huevos", 
                            f"{total_bultos:,.0f} bultos",
                            f"{p_real:.2f}% | {p_guia:.2f}% | {dif_p:+.2f}%",
                            f"{c_real:.2f}g | {c_guia:.2f}g | {dif_c:+.1f}g",
                            f"{conv_prom:.2f} pts"
                        ]
                    }

                    # Renderizado de la tabla estática
                    st.table(pd.DataFrame(resumen_data))
                else:
                    st.warning("No hay datos para el periodo seleccionado.")
                # --- EXCEL ---
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_vista[cols].to_excel(writer, index=False)
                st.download_button(label=f"📥 Descargar Excel G{lista_galpones[i]}", data=buffer.getvalue(), 
                                   file_name=f"Bitacora_G{lista_galpones[i]}.xlsx", key=f"btn_{lista_galpones[i]}")

else:
    st.error("No se encontraron datos.")
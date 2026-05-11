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
        # 1. Obtenemos los valores únicos
        granjas_unicas = df_empresa['Nombre de Granja (P) :'].unique()
        
        # 2. Filtramos para quitar el 0, el "0" (texto) y cualquier valor vacío (NaN)
        lista_granjas = [g for g in granjas_unicas if g not in [0, "0", "0.0", "None", None]]
        
        # 3. Lo ordenamos alfabéticamente
        lista_granjas = sorted(lista_granjas)
        
        granja_sel = st.selectbox("🏘️ Granja", lista_granjas)
    with c2:
        df_f_g = df_empresa[df_empresa['Nombre de Granja (P) :'] == granja_sel]
        lote_sel = st.selectbox("🆔 Lote", sorted(df_f_g['Número de Lote :'].unique()))
    with c3:
        df_f_l = df_f_g[df_f_g['Número de Lote :'] == lote_sel]


# --- 4. FILTRADO POR LOTE Y DEFINICIÓN DE LÍMITES (AQUÍ DEFINES MAX Y MIN) ---
    df_f_l = df_f_g[df_f_g['Número de Lote :'] == lote_sel]
    
    # IMPORTANTE: Definir estas dos variables aquí
    min_f = df_f_l['Fecha'].min()
    max_f = df_f_l['Fecha'].max()

    # Ahora sí, el código de los filtros rápidos funcionará:
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        filtro_rapido = st.radio(
            "🔎 Vista rápida:",
            ["Últimos 7 días", "Últimos 30 días", "Ver Todo", "Personalizado"],
            horizontal=True,
            index=0 # Por defecto marcar 'Últimos 7 días'
        )

    with col_f2:
        if filtro_rapido == "Últimos 7 días":
            fecha_inicio = max_f - pd.Timedelta(days=7)
            # Aseguramos que no se salga del rango mínimo del archivo
            fecha_inicio = max(fecha_inicio, min_f) 
            rango = (fecha_inicio, max_f)
            st.info(f"📅 Mostrando: {fecha_inicio.strftime('%d/%m/%Y')} al {max_f.strftime('%d/%m/%Y')}")
            
        elif filtro_rapido == "Últimos 30 días":
            fecha_inicio = max_f - pd.Timedelta(days=30)
            fecha_inicio = max(fecha_inicio, min_f)
            rango = (fecha_inicio, max_f)
            st.info(f"📅 Mostrando: {fecha_inicio.strftime('%d/%m/%Y')} al {max_f.strftime('%d/%m/%Y')}")
            
        elif filtro_rapido == "Ver Todo":
            rango = (min_f, max_f)
            st.info("📅 Mostrando historial completo")
            
        else: # Personalizado
            rango = st.date_input("📅 Seleccione Rango:", value=(min_f, max_f), min_value=min_f, max_value=max_f)

    st.divider()

    # --- 5. INFO LOTE (SOLICITADO EN AMARILLO) ---
    if not df_f_l.empty:
        info_lote = df_f_l.iloc[0]
        with st.expander("🔍 Información Conceptual del Lote", expanded=True):
            inf1, inf2, inf3, inf4 = st.columns(4)
            
            # Extracción segura de los datos solicitados
            ubi = info_lote.get('Ubicación Granja (P) :', 'N/A')
            lin = info_lote.get('Línea de las Aves :', 'N/A') # El nombre exacto del Excel
            f_inicio = df_f_l['Fecha'].min()
            t_galpones = len(df_f_l['Galpón'].unique())

            inf1.metric("📍 Ubicación", ubi)
            inf2.metric("🧬 Línea Genética", lin)
            inf3.metric("🐣 Fecha Inicio", f_inicio.strftime('%d/%m/%Y'))
            inf4.metric("🏠 Total Galpones", t_galpones)

    # --- 6. TABS DE GALPONES ---
    galpones_raw = df_f_l['Galpón'].unique()
    # Así es la forma más limpia de hacerlo:
    lista_galpones = sorted([g for g in df_f_l['Galpón'].unique() if g not in [0, "0", None]])

    if lista_galpones:
        tabs = st.tabs([f"🏠 Galpón {g}" for g in lista_galpones])

        for i, tab in enumerate(tabs):
            with tab:
                # Filtrar galpón actual para la tabla principal
                df_tab = df_f_l[df_f_l['Galpón'] == lista_galpones[i]].copy()
                
                # --- MATEMÁTICA REAL VS POND (HORIZONTAL) ---
                df_tab['Dif Gr Ave'] = df_tab['Consumo Gr. A. D.'] - df_tab['Pond. Gr. Ave Dia']
                df_tab['Dif Pdn'] = df_tab['% Diario de Prod.'] - df_tab['Pond. % Prod.']
                df_tab['Conv Diaria'] = (df_tab['Consumo Gr. A. D.'] / (df_tab['% Diario de Prod.'] / 100)).replace([float('inf'), -float('inf')], 0).fillna(0)
                
                # Aplicar filtro de calendario
                if isinstance(rango, tuple) and len(rango) == 2:
                    df_periodo = df_tab[(df_tab['Fecha'] >= rango[0]) & (df_tab['Fecha'] <= rango[1])]
                else:
                    df_periodo = df_tab.copy()

                # Vista descendente (hoy arriba)
                df_vista = df_periodo.sort_values(by='Fecha', ascending=False)

                # --- ESTILOS DE ALERTAS ---
                def style_dif(row):
                    styles = [''] * len(row)
                    idx_g = row.index.get_loc('Dif Gr Ave')
                    idx_p = row.index.get_loc('Dif Pdn')
                    
                    # Consumo: >1.5g (Zapote), <-1.5g (Verde)
                    if row['Dif Gr Ave'] > 1.5: styles[idx_g] = 'background-color: #FF6700; color: white;'
                    elif row['Dif Gr Ave'] < -1.5: styles[idx_g] = 'background-color: #2ECC71; color: white;'
                    
                    # Postura: <-1.5% (Zapote), >1.5% (Verde)
                    if row['Dif Pdn'] < -1.0: styles[idx_p] = 'background-color: #FF6700; color: white;'
                    elif row['Dif Pdn'] > 1.5: styles[idx_p] = 'background-color: #2ECC71; color: white;'
                    return styles

                cols = [
                    'Fecha', 'Edad Sem + Días', 'Mort.', 'Otros', 'Selec.', 'Saldo Aves', 
                    'Consumo Gr. A. D.', 'Pond. Gr. Ave Dia', 'Dif Gr Ave',
                    'Producción Huevos Día', '% Diario de Prod.', 'Pond. % Prod.', 'Dif Pdn', 'Conv Diaria', 'Ingreso B X 40 K', 'Consumo B X 40 K',
                    'Traslado B X 40 K', 'Saldo B X 40 K', 
                    #'Cons Agua (Lt)', 'ml / ave',
                     'Observaciones'
                ]

                # --- RENDER DE TABLA ---
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
                        #"Cons Agua (Lt)": st.column_config.NumberColumn("Agua L.", format="%d"),
                        #"ml / ave": st.column_config.NumberColumn("ml/ave", format="%.1f"),
                        "Ingreso B X 40 K": st.column_config.NumberColumn("Ingreso Bx40", format="%d"),
                        "Consumo B X 40 K": st.column_config.NumberColumn("Consumo Bx40", format="%d"),
                        "Traslado B X 40 K": st.column_config.NumberColumn("Traslado Bx40", format="%d"),
                        "Saldo B X 40 K": st.column_config.NumberColumn("Saldo Bx40", format="%d"),
                    }
                )
                
                # --- TABLA DE RESUMEN / TOTALES (INSERTAR AQUÍ) ---
                st.markdown("### 📊 Resumen de Totales y Promedios")

                # Calculamos los valores sobre el DataFrame que ya está filtrado por fecha (df_periodo)
                total_mort = df_periodo['Mort.'].sum()
                total_huevos = df_periodo['Producción Huevos Día'].sum()
                total_bultos = df_periodo['Consumo B X 40 K'].sum()

                # Promedios reales: ignoramos los días que están en 0 para no dañar el promedio
                dias_con_datos = df_periodo[df_periodo['Consumo Gr. A. D.'] > 0]
                prom_consumo = dias_con_datos['Consumo Gr. A. D.'].mean() if not dias_con_datos.empty else 0
                prom_postura = dias_con_datos['% Diario de Prod.'].mean() if not dias_con_datos.empty else 0
 
                # Creamos una estructura limpia para mostrar los totales
                resumen_data = {
                "Concepto": ["Mortalidad Acumulada", "Producción Total", "Alimento Consumido", "Rendimiento Promedio", "Conversión Promedio"],
                "Totales del Periodo": [
                    f"{total_mort:,.0f} aves", 
                    f"{total_huevos:,.0f} huevos", 
                    f"{total_bultos:,.0f} bultos",
                    f"{prom_postura:.2f}% Postura | {prom_consumo:.2f}g Cons.",
                    f"{df_periodo['Conv Diaria'].mean():.2f} Conv."
                ]
                }

                # Mostramos la tabla estática (st.table es mejor para resúmenes que st.dataframe)
                st.table(pd.DataFrame(resumen_data))
                # --- EXCEL ---
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_vista[cols].to_excel(writer, index=False)
                st.download_button(label=f"📥 Descargar Excel G{lista_galpones[i]}", data=buffer.getvalue(), 
                                   file_name=f"Bitacora_G{lista_galpones[i]}.xlsx", key=f"btn_{lista_galpones[i]}")

else:
    st.error("No se encontraron datos.")
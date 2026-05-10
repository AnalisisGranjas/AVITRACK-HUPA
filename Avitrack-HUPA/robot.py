import pandas as pd
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE EMPRESAS Y RUTAS ---
CONFIG_RUTAS = {
    r'G:\.shortcut-targets-by-id\1H6coCC4GgCcvOGjxbvwnkh2A1xto5hcc\2026. Granjas\Registros_ Lotes Activos\Grupo Empresarial RRL_ Registros': 'GRUPO EMPRESARIAL RRL',
    r'G:\.shortcut-targets-by-id\1H6coCC4GgCcvOGjxbvwnkh2A1xto5hcc\2026. Granjas\Registros_ Lotes Activos\Agropecuaria Nueva del Oriente_ Registros Lotes Activos\PRODUCCION AGNO': 'AGROPECUARIA NUEVA DEL ORIENTE'
}

ARCHIVO_SALIDA = os.path.join('DATA', 'REPORTE_AVITRACK_FINAL.xlsx')
FECHA_HOY = datetime.now().date() 

def formatear_fecha_estandar(valor):
    try:
        if pd.isna(valor) or str(valor).strip() == "" or valor == 0: return ""
        if isinstance(valor, (int, float)):
            if valor < 1000: return ""
            fecha_obj = (datetime(1899, 12, 30) + timedelta(days=valor)).date()
        elif isinstance(valor, (datetime, pd.Timestamp)):
            fecha_obj = valor.date()
        else:
            limpio = str(valor).split('/')[0:3]
            fecha_obj = pd.to_datetime("/".join(limpio), errors='coerce', dayfirst=True).date()
        return fecha_obj.strftime('%d/%m/%y') if fecha_obj else ""
    except: return str(valor)

def formatear_edad_excel(valor):
    """Cura 1: Añade comilla simple para que Excel no intente reparar la celda"""
    try:
        if pd.isna(valor) or valor == "" or valor == 0: return ""
        if isinstance(valor, str): return f"'{valor}"
        num = float(valor)
        semanas = int(num)
        dias = round((num - semanas) * 7)
        if dias == 0: res = str(semanas)
        elif dias >= 7: res = str(semanas + 1)
        else: res = f"{semanas} + {dias}/7"
        return f"'{res}" # La comilla ' evita el error de reparación
    except: return str(valor)

def extraer_datos_archivo(ruta_archivo, razon_social):
    datos_archivo = []
    try:
        xl = pd.ExcelFile(ruta_archivo)
        df_ini = pd.read_excel(xl, sheet_name='INF-INI', header=None)
        
        def buscar_inf_ini(texto, ocurrencia=1):
            encontrados = []
            for r in range(min(len(df_ini), 60)):
                for c in range(min(len(df_ini.columns), 5)):
                    if texto.lower() in str(df_ini.iloc[r, c]).lower():
                        for offset in range(1, 4):
                            if (c + offset) < len(df_ini.columns):
                                v = df_ini.iloc[r, c + offset]
                                if pd.notna(v) and str(v).strip() != "":
                                    encontrados.append(v); break
            return encontrados[ocurrencia-1] if len(encontrados) >= ocurrencia else ""

        info_maestra = {
            'Razon Social': razon_social,
            'Número de Lote :': str(buscar_inf_ini("Número de Lote")),
            'Línea de las Aves :': buscar_inf_ini("Línea de las Aves"),
            'Fecha de nacimiento :': formatear_fecha_estandar(buscar_inf_ini("Fecha de nacimiento")),
            '# Pollitas :': buscar_inf_ini("# Pollitas"),
            'Orígen del Levante :': buscar_inf_ini("Orígen del Levante"),
            'Nombre de Granja (L) :': buscar_inf_ini("Nombre de Granja :", 1),
            'Ubicación Granja (L) :': buscar_inf_ini("Ubicación Granja :", 1),
            'Fecha corte a Producción :': formatear_fecha_estandar(buscar_inf_ini("Fecha corte a Producción")),
            'Nombre de Granja (P) :': buscar_inf_ini("Nombre de Granja :", 2),
            'Ubicación Granja (P) :': buscar_inf_ini("Ubicación Granja :", 2)
        }

        df_dia = pd.read_excel(xl, sheet_name='DIA-PN', header=None)
        f_tit = 5 
        indices_mort = [i for i, v in enumerate(df_dia.iloc[f_tit]) if str(v).strip().lower() == "mort."]
        galpones_a_procesar = indices_mort[:15]

        for c_mort in galpones_a_procesar:
            nombre_raw = str(df_dia.iloc[0, c_mort]).upper()
            nombre_galpon = nombre_raw.split('-')[-1].replace('GALPÓN', '').replace(':', '').strip()

            try:
                if pd.isna(df_dia.iloc[f_tit - 1, c_mort]) or float(df_dia.iloc[f_tit - 1, c_mort]) <= 0: continue
            except: continue

            c_trasl = c_mort + 3
            fila_inicio = -1
            for r_check in range(f_tit + 1, len(df_dia)):
                val_trasl = df_dia.iloc[r_check, c_trasl]
                if pd.notna(val_trasl) and val_trasl != 0:
                    fila_inicio = r_check; break
            
            if fila_inicio == -1: continue

            for r in range(fila_inicio, len(df_dia)):
                if r >= len(df_dia): break # Cura 2: Evita salir de los límites de la hoja
                
                f_raw = df_dia.iloc[r, 1]
                f_form = formatear_fecha_estandar(f_raw)
                if not f_form or str(f_raw).lower() == "total": break
                
                try:
                    if datetime.strptime(f_form, '%d/%m/%y').date() > FECHA_HOY: break
                except: pass

                # Cura 3: Limpieza de observaciones para evitar caracteres de fórmula
                obs_val = df_dia.iloc[r, c_mort + 16]
                obs_limpia = f"'{str(obs_val)}" if pd.notna(obs_val) else ""

                reg = {**info_maestra}
                reg.update({
                    'Galpón': nombre_galpon,
                    'Fecha': f_form,
                    'Edad Sem + Días': formatear_edad_excel(df_dia.iloc[r, 2]),
                    'Mort.': df_dia.iloc[r, c_mort],
                    'Otros': df_dia.iloc[r, c_mort + 1],
                    'Selec.': df_dia.iloc[r, c_mort + 2],
                    'Trasl Ventas': df_dia.iloc[r, c_mort + 3],
                    'Saldo Aves': df_dia.iloc[r, c_mort + 4],
                    'Cons Agua (Lt)': df_dia.iloc[r, c_mort + 5],
                    'Ingreso B X 40 K': df_dia.iloc[r, c_mort + 6],
                    'Consumo B X 40 K': df_dia.iloc[r, c_mort + 7],
                    'Traslado B X 40 K': df_dia.iloc[r, c_mort + 8],
                    'Saldo B X 40 K': df_dia.iloc[r, c_mort + 9],
                    'Consumo Gr. A. D.': df_dia.iloc[r, c_mort + 10],
                    'Pond. Gr. Ave Dia': df_dia.iloc[r, c_mort + 11],
                    'ml / ave': df_dia.iloc[r, c_mort + 12],
                    'Producción Huevos Día': df_dia.iloc[r, c_mort + 13],
                    '% Diario de Prod.': df_dia.iloc[r, c_mort + 14],
                    'Pond. % Prod.': df_dia.iloc[r, c_mort + 15],
                    'Observaciones': obs_limpia,
                    'Archivo': os.path.basename(ruta_archivo)
                })
                datos_archivo.append(reg)
                    
    except Exception as e:
        print(f"⚠️ Error en {os.path.basename(ruta_archivo)}: {e}")
    return datos_archivo

def ejecutar():
    print("--- 🚀 EXTRACCIÓN TOTAL ANTI-ERRORES ---")
    consolidado_final = []
    
    for ruta, nombre_empresa in CONFIG_RUTAS.items():
        if not os.path.exists(ruta): continue
        for raiz, _, archivos in os.walk(ruta):
            for f in archivos:
                if f.endswith('.xlsx') and not f.startswith('~$'):
                    print(f"   📂 Procesando: {f}")
                    res = extraer_datos_archivo(os.path.join(raiz, f), nombre_empresa)
                    if res: consolidado_final.extend(res)

    if consolidado_final:
        # Usamos el motor openpyxl directamente para mayor estabilidad
        pd.DataFrame(consolidado_final).to_excel(ARCHIVO_SALIDA, index=False, engine='openpyxl')
        print(f"\n✅ ETL COMPLETADA. Archivo generado: {ARCHIVO_SALIDA}")
    else:
        print("\n⚠️ No se encontraron datos.")

if __name__ == "__main__":
    ejecutar()
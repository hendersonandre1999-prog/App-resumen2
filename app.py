import streamlit as st
import pandas as pd
import os

# Configuración principal para que se vea bien en celular
st.set_page_config(page_title="Dashboard Interactivo", page_icon="📱", layout="centered")

# Archivo puente donde se guarda la info para que la vean los visores en tiempo real
ARCHIVO_DATOS = "datos_resumen_compartido.csv"

# --- LÓGICA DE ROLES Y SEGURIDAD (MENÚ LATERAL) ---
st.sidebar.title("🔒 Acceso Administrador")
st.sidebar.write("Solo para actualización de datos.")

# Campos de login (el type="password" oculta los caracteres)
usuario = st.sidebar.text_input("Usuario")
contrasena = st.sidebar.text_input("Contraseña", type="password")

es_admin = (usuario == "henderson.gonzalez" and contrasena == "1234")

if es_admin:
    st.sidebar.success("✅ Hola, Henderson. Sesión iniciada.")
    st.sidebar.write("---")
    
    # Módulo de carga de archivos (solo visible para ti)
    archivo_subido = st.sidebar.file_uploader("Cargar documento Excel", type=["xlsx", "xlsb", "xls"])
    
    if archivo_subido is not None:
        try:
            with st.spinner("Procesando hoja RESUMEN..."):
                # Leer específicamente la pestaña llamada "RESUMEN"
                # Si tu archivo es .xlsb usa engine='pyxlsb', si es .xlsx usa engine='openpyxl'
                if archivo_subido.name.endswith('.xlsb'):
                    df = pd.read_excel(archivo_subido, sheet_name="RESUMEN", engine="pyxlsb")
                else:
                    df = pd.read_excel(archivo_subido, sheet_name="RESUMEN")
                
                # Guardamos los datos procesados en el servidor para los visores
                df.to_csv(ARCHIVO_DATOS, index=False)
                st.sidebar.success("¡Datos actualizados con éxito! Tus usuarios ya pueden ver los cambios.")
        except ValueError:
            st.sidebar.error("❌ No se encontró una hoja llamada 'RESUMEN' en el documento.")
        except Exception as e:
            st.sidebar.error(f"❌ Error al procesar el archivo: {e}")
else:
    if usuario or contrasena:
        st.sidebar.error("Credenciales incorrectas.")
    st.sidebar.info("Modo visor activado. Visualización en tiempo real.")

# --- PANTALLA PRINCIPAL (LO QUE VEN TUS USUARIOS) ---
st.title("📊 Resumen Operativo")
st.write("Información sincronizada y disponible en tiempo real.")

# Botón para que los usuarios fuercen la recarga de datos si lo desean
col1, col2 = st.columns([0.8, 0.2])
with col2:
    if st.button("🔄 Refrescar"):
        st.rerun()

# Mostrar la información si el administrador ya subió un archivo
if os.path.exists(ARCHIVO_DATOS):
    df_publico = pd.read_csv(ARCHIVO_DATOS)
    
    # 1. Tarjetas de métricas (Toma las primeras columnas numéricas automáticamente)
    st.write("### Indicadores Clave")
    cols_numericas = df_publico.select_dtypes(include=['number']).columns
    if len(cols_numericas) >= 2:
        m1, m2 = st.columns(2)
        m1.metric(label=cols_numericas[0], value=round(df_publico[cols_numericas[0]].sum(), 2))
        m2.metric(label=cols_numericas[1], value=round(df_publico[cols_numericas[1]].sum(), 2))
    
    # 2. Tabla interactiva (permite buscar, ordenar y ampliar)
    st.write("### Detalle de Información")
    st.dataframe(
        df_publico, 
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No hay información disponible en este momento. El administrador debe cargar un documento base.")

import streamlit as st
import pandas as pd
import os

# Configuración de pantalla completa para maximizar el espacio de las tablas
st.set_page_config(page_title="Control Oficial SHIIFT", layout="wide")

# Archivos puente para ambas hojas
ARCHIVO_RESUMEN = "datos_RESUMEN.csv"
ARCHIVO_MACRO = "datos_Resumen_Macro.csv"

# --- MENÚ LATERAL (ADMINISTRADOR) ---
with st.sidebar:
    st.markdown("### 🔒 Gestión de Proyecto SHIIFT")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if usuario == "henderson.gonzalez" and contrasena == "1234":
        st.success("✅ Acceso validado.")
        archivo_subido = st.file_uploader("Cargar documento de Control Oficial", type=["xlsx", "xlsb", "xls"])
        
        if archivo_subido is not None:
            with st.spinner("Extrayendo matrices de datos..."):
                try:
                    engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                    
                    # El sistema ahora lee específicamente ambas hojas
                    df_resumen = pd.read_excel(archivo_subido, sheet_name="RESUMEN", engine=engine)
                    df_macro = pd.read_excel(archivo_subido, sheet_name="Resumen Macro", engine=engine)
                    
                    # Se guardan ambos archivos en el servidor para visualización en tiempo real
                    df_resumen.to_csv(ARCHIVO_RESUMEN, index=False)
                    df_macro.to_csv(ARCHIVO_MACRO, index=False)
                    
                    st.success("¡Hojas RESUMEN y RESUMEN MACRO sincronizadas correctamente!")
                except ValueError as ve:
                    st.error("❌ Asegúrate de que el documento contenga exactamente las hojas llamadas 'RESUMEN' y 'Resumen Macro'.")
                except Exception as e:
                    st.error(f"❌ Error en la extracción: {e}")

# --- PANTALLA PRINCIPAL ---
st.title("📋 Matrices de Control Oficial")
st.write("Visualización de datos en formato nativo para consulta y cruce de información.")

if os.path.exists(ARCHIVO_RESUMEN) and os.path.exists(ARCHIVO_MACRO):
    # Cargar las bases de datos guardadas
    df_resumen_publico = pd.read_csv(ARCHIVO_RESUMEN)
    df_macro_publico = pd.read_csv(ARCHIVO_MACRO)
    
    # Crear pestañas de navegación superiores (Tabs)
    tab1, tab2 = st.tabs(["📄 RESUMEN", "📊 Resumen Macro"])
    
    with tab1:
        # Se muestra la tabla expandida a lo ancho de la pantalla y con mayor altura
        st.dataframe(
            df_resumen_publico, 
            use_container_width=True, 
            height=600,
            hide_index=True # Oculta la columna de enumeración inicial para que se vea más limpio
        )
        
    with tab2:
        st.dataframe(
            df_macro_publico, 
            use_container_width=True, 
            height=600,
            hide_index=True
        )
        
else:
    st.info("El sistema está inactivo. Ingresa con tus credenciales en el menú lateral para realizar la carga inicial de las matrices.")

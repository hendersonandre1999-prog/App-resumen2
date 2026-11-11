import streamlit as st
import pandas as pd
import os

# Configuración de pantalla completa
st.set_page_config(page_title="Control Oficial SHIIFT", layout="wide")

ARCHIVO_RESUMEN = "datos_resumen.csv"
ARCHIVO_MACRO = "datos_resumen_macro.csv"

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
                    
                    # Usamos 0 y 1 para que lea la primera y segunda hoja sin importar el nombre exacto
                    df_resumen = pd.read_excel(archivo_subido, sheet_name=0, engine=engine)
                    df_macro = pd.read_excel(archivo_subido, sheet_name=1, engine=engine)
                    
                    df_resumen.to_csv(ARCHIVO_RESUMEN, index=False)
                    df_macro.to_csv(ARCHIVO_MACRO, index=False)
                    
                    st.success("¡Matrices sincronizadas correctamente!")
                except Exception as e:
                    st.error(f"❌ Error en la extracción: {e}")

# --- PANTALLA PRINCIPAL ---
st.title("📋 Matrices de Control Oficial")

if os.path.exists(ARCHIVO_RESUMEN) and os.path.exists(ARCHIVO_MACRO):
    df_resumen = pd.read_csv(ARCHIVO_RESUMEN)
    df_macro = pd.read_csv(ARCHIVO_MACRO)
    
    st.write("---")
    st.markdown("### 🔍 Buscador y Filtros de Validación")
    
    # Obtener la lista de columnas para buscar las de BP y Product Owner
    columnas = df_resumen.columns.tolist()
    
    # Auto-detección de las columnas (busca coincidencias en el texto de las cabeceras)
    posibles_bp = [c for c in columnas if "BP" in str(c).upper()]
    posibles_po = [c for c in columnas if "OWNER" in str(c).upper() or "PRODUCT" in str(c).upper() or "PO" == str(c).upper()]
    
    # Si encuentra las columnas usa esas, si no, usa la 1ra y 2da columna por defecto para que no de error
    col_bp = posibles_bp[0] if posibles_bp else columnas[0]
    col_po = posibles_po[0] if posibles_po else (columnas[1] if len(columnas) > 1 else columnas[0])
    
    # Diseñar los 3 cuadros de filtros en una sola fila
    col1, col2, col3 = st.columns(3)
    
    with col1:
        busqueda_libre = st.text_input("Búsqueda general libre (Palabra clave):", "")
        
    with col2:
        filtro_bp = st.multiselect(f"Filtrar por BP ({col_bp}):", options=df_resumen[col_bp].dropna().unique())
        
    with col3:
        filtro_po = st.multiselect(f"Filtrar por Product Owner ({col_po}):", options=df_resumen[col_po].dropna().unique())

    # --- APLICACIÓN DE LOS FILTROS A LAS TABLAS ---
    df_filtrado_resumen = df_resumen.copy()
    df_filtrado_macro = df_macro.copy()
    
    # 1. Aplicar filtro de búsqueda libre
    if busqueda_libre:
        mask_resumen = df_filtrado_resumen.astype(str).apply(lambda x: x.str.contains(busqueda_libre, case=False, na=False)).any(axis=1)
        df_filtrado_resumen = df_filtrado_resumen[mask_resumen]
        
        mask_macro = df_filtrado_macro.astype(str).apply(lambda x: x.str.contains(busqueda_libre, case=False, na=False)).any(axis=1)
        df_filtrado_macro = df_filtrado_macro[mask_macro]
        
    # 2. Aplicar filtro de BP
    if filtro_bp:
        df_filtrado_resumen = df_filtrado_resumen[df_filtrado_resumen[col_bp].isin(filtro_bp)]
        # Verifica si la columna BP también existe en la hoja Macro para filtrarla
        if col_bp in df_filtrado_macro.columns:
            df_filtrado_macro = df_filtrado_macro[df_filtrado_macro[col_bp].isin(filtro_bp)]
            
    # 3. Aplicar filtro de Product Owner
    if filtro_po:
        df_filtrado_resumen = df_filtrado_resumen[df_filtrado_resumen[col_po].isin(filtro_po)]
        if col_po in df_filtrado_macro.columns:
            df_filtrado_macro = df_filtrado_macro[df_filtrado_macro[col_po].isin(filtro_po)]

    st.write("---")
    
    # --- VISUALIZACIÓN DE RESULTADOS ---
    tab1, tab2 = st.tabs(["📄 MATRIZ RESUMEN", "📊 MATRIZ MACRO"])
    
    with tab1:
        st.markdown(f"**Registros encontrados: {len(df_filtrado_resumen)}**")
        st.dataframe(df_filtrado_resumen, use_container_width=True, height=550, hide_index=True)
        
    with tab2:
        st.markdown(f"**Registros encontrados: {len(df_filtrado_macro)}**")
        st.dataframe(df_filtrado_macro, use_container_width=True, height=550, hide_index=True)
        
else:
    st.info("El sistema está inactivo. Ingresa con tus credenciales en el menú lateral para realizar la carga inicial.")

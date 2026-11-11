import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de pantalla ancha para los gráficos
st.set_page_config(page_title="Control Operativo SHIIFT", page_icon="📊", layout="wide")

ARCHIVO_DATOS = "datos_resumen_compartido.csv"

# --- LÓGICA DE ROLES Y SEGURIDAD ---
st.sidebar.title("🔒 Administrador")
usuario = st.sidebar.text_input("Usuario")
contrasena = st.sidebar.text_input("Contraseña", type="password")
es_admin = (usuario == "henderson.gonzalez" and contrasena == "1234")

if es_admin:
    st.sidebar.success("✅ Sesión iniciada.")
    archivo_subido = st.sidebar.file_uploader("Cargar Control Oficial SHIIFT", type=["xlsx", "xlsb", "xls"])
    
    if archivo_subido is not None:
        with st.spinner("Procesando datos y estructurando tablero..."):
            try:
                engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                df = pd.read_excel(archivo_subido, sheet_name="RESUMEN", engine=engine)
                df.to_csv(ARCHIVO_DATOS, index=False)
                st.sidebar.success("¡Datos actualizados para todo el equipo!")
            except Exception as e:
                st.sidebar.error(f"Error al leer la hoja: {e}")

# --- PANTALLA PRINCIPAL (LO QUE VE EL EQUIPO) ---
st.title("📊 Tablero de Control - Proyecto SHIIFT")

if os.path.exists(ARCHIVO_DATOS):
    df_publico = pd.read_csv(ARCHIVO_DATOS)
    
    # El sistema clasifica automáticamente qué es texto y qué es número
    cols_texto = df_publico.select_dtypes(include=['object', 'string']).columns.tolist()
    cols_numeros = df_publico.select_dtypes(include=['number']).columns.tolist()
    
    if len(cols_texto) > 0 and len(cols_numeros) > 0:
        
        # 1. FILTROS INTERACTIVOS
        st.write("### 🔍 Buscador y Filtros")
        col_filtro1, col_filtro2 = st.columns([1, 2])
        
        with col_filtro1:
            filtro_principal = st.selectbox("¿Qué categoría deseas analizar?", cols_texto)
        with col_filtro2:
            valores_seleccionados = st.multiselect(
                "Selecciona los elementos específicos:", 
                options=df_publico[filtro_principal].unique(), 
                default=df_publico[filtro_principal].unique()
            )
        
        # Aplicar el filtro a la base de datos
        df_filtrado = df_publico[df_publico[filtro_principal].isin(valores_seleccionados)]
        st.write("---")
        
        # 2. TARJETAS DE INDICADORES (KPIs)
        st.write("### 🎯 Totales Globales")
        kpis = st.columns(min(len(cols_numeros), 4))
        
        for i, col in enumerate(cols_numeros[:4]):
            total = df_filtrado[col].sum()
            # Se formatea el número con separador de miles
            kpis[i].metric(label=f"Suma de {col}", value=f"{total:,.2f}")
            
        st.write("---")
        
        # 3. GRÁFICOS VISUALES DINÁMICOS
        st.write("### 📈 Comportamiento de los Datos")
        grafico_izq, grafico_der = st.columns(2)
        
        with grafico_izq:
            # Gráfico de barras de la primera métrica numérica
            fig_barras = px.bar(
                df_filtrado, 
                x=filtro_principal, 
                y=cols_numeros[0], 
                title=f"Volumen de {cols_numeros[0]}",
                color=filtro_principal
            )
            st.plotly_chart(fig_barras, use_container_width=True)
            
        with grafico_der:
            # Gráfico de pastel de la segunda métrica numérica (o repite la primera si solo hay una)
            col_pastel = cols_numeros[1] if len(cols_numeros) > 1 else cols_numeros[0]
            fig_pastel = px.pie(
                df_filtrado, 
                names=filtro_principal, 
                values=col_pastel, 
                title=f"Distribución de {col_pastel}",
                hole=0.4 # Esto lo convierte en un gráfico de anillo moderno
            )
            st.plotly_chart(fig_pastel, use_container_width=True)
            
        st.write("---")
        
        # 4. TABLA DE DETALLE
        st.write("### 📋 Desglose Operativo")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
    else:
        st.warning("Tu Excel necesita tener al menos una columna con texto y una con números para generar gráficos automáticamente.")
        st.dataframe(df_publico, use_container_width=True)
else:
    st.info("El sistema está activo. Ingresa como administrador y carga el documento base para iniciar.")

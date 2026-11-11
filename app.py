import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de página ancha para aprovechar todo el monitor
st.set_page_config(page_title="Dashboard SHIIFT", layout="wide", initial_sidebar_state="expanded")

ARCHIVO_DATOS = "datos_resumen_compartido.csv"

# --- MENÚ LATERAL (SIDEBAR) ---
st.sidebar.title("🔒 Admin")
usuario = st.sidebar.text_input("Usuario")
contrasena = st.sidebar.text_input("Contraseña", type="password")

if usuario == "henderson.gonzalez" and contrasena == "1234":
    st.sidebar.success("✅ Sesión iniciada.")
    archivo_subido = st.sidebar.file_uploader("Cargar archivo Excel", type=["xlsx", "xlsb", "xls"])
    
    if archivo_subido is not None:
        with st.spinner("Procesando y actualizando tablero..."):
            try:
                engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                df = pd.read_excel(archivo_subido, sheet_name="RESUMEN", engine=engine)
                df.to_csv(ARCHIVO_DATOS, index=False)
                st.sidebar.success("¡Datos actualizados!")
            except Exception as e:
                st.sidebar.error(f"Error al leer la hoja: {e}")

# --- PANTALLA PRINCIPAL (VISUALIZACIÓN TIPO MOCKUP) ---
st.title("My Dashboard")

if os.path.exists(ARCHIVO_DATOS):
    df = pd.read_csv(ARCHIVO_DATOS)
    
    # Detección automática de columnas
    cols_texto = df.select_dtypes(include=['object', 'string']).columns.tolist()
    cols_numeros = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(cols_texto) > 0 and len(cols_numeros) > 0:
        cat = cols_texto[0] # Primera columna de texto (Categoría)
        num1 = cols_numeros[0] # Primera métrica numérica
        num2 = cols_numeros[1] if len(cols_numeros) > 1 else num1 # Segunda métrica (o repite la primera)
        
        # Agrupamos los datos para que las gráficas se vean limpias
        df_agrupado = df.groupby(cat, as_index=False).sum()
        
        # --- FILA 1: Gráfico de Pastel (Izquierda) y Área (Derecha) ---
        fila1_col1, fila1_col2 = st.columns([1, 1.5])
        
        with fila1_col1:
            with st.container(border=True): # Crea la tarjeta blanca con borde
                st.write("**Pie chart example**")
                st.caption(f"Distribución de {num1}")
                fig_pie = px.pie(df_agrupado, names=cat, values=num1)
                fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_pie, use_container_width=True)
                st.button("Edit report", key="btn_pie")
                
        with fila1_col2:
            with st.container(border=True):
                st.write("**Area chart example**")
                st.caption(f"Evolución o Volumen de {num2}")
                fig_area = px.area(df_agrupado, x=cat, y=num2)
                fig_area.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_area, use_container_width=True)
                st.button("Edit report", key="btn_area")

        # --- FILA 2: Barras Verticales, Barras Horizontales y Dona ---
        fila2_col1, fila2_col2, fila2_col3 = st.columns(3)
        
        with fila2_col1:
            with st.container(border=True):
                st.write("**Bar chart example**")
                st.caption(f"Comparativa de {num1}")
                fig_bar1 = px.bar(df_agrupado, x=cat, y=num1, color=cat)
                fig_bar1.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
                st.plotly_chart(fig_bar1, use_container_width=True)
                
        with fila2_col2:
            with st.container(border=True):
                st.write("**Bar chart example**")
                st.caption(f"Ranking de {num1}")
                # Gráfico de barras horizontales (orientation='h')
                fig_bar2 = px.bar(df_agrupado, x=num1, y=cat, orientation='h', color=cat)
                fig_bar2.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
                st.plotly_chart(fig_bar2, use_container_width=True)
                
        with fila2_col3:
            with st.container(border=True):
                st.write("**Donut chart example**")
                st.caption(f"Proporción de {num2}")
                fig_donut = px.pie(df_agrupado, names=cat, values=num2, hole=0.65)
                
                # Texto en el centro de la dona
                total_val = df_agrupado[num2].sum()
                fig_donut.add_annotation(text=f"{total_val:,.0f}", x=0.5, y=0.5, font_size=24, showarrow=False)
                
                fig_donut.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
                st.plotly_chart(fig_donut, use_container_width=True)
                
    else:
        st.warning("El archivo Excel necesita tener al menos una columna de texto y una de números en la hoja RESUMEN.")
else:
    st.info("Modo de visualización activo. Inicia sesión en el panel lateral para cargar el documento.")

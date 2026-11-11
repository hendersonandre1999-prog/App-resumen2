import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. Configuración de página ancha y limpia
st.set_page_config(page_title="SHIIFT Finances", layout="wide", initial_sidebar_state="expanded")

ARCHIVO_DATOS = "datos_resumen_compartido.csv"

# --- MENÚ LATERAL (SIMULANDO NAVEGACIÓN) ---
with st.sidebar:
    st.markdown("### | SHIIFT DASHBOARD")
    st.markdown("---")
    st.radio("Navegación", ["Overview", "Expenses", "Reports", "Transfers", "Notifications"], label_visibility="collapsed")
    st.markdown("---")
    
    st.markdown("🔒 **Admin Login**")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if usuario == "henderson.gonzalez" and contrasena == "1234":
        st.success("✅ Acceso concedido")
        archivo_subido = st.file_uploader("Actualizar Excel (RESUMEN)", type=["xlsx", "xlsb", "xls"])
        
        if archivo_subido is not None:
            try:
                engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                df = pd.read_excel(archivo_subido, sheet_name="RESUMEN", engine=engine)
                df.to_csv(ARCHIVO_DATOS, index=False)
                st.success("¡Base de datos actualizada!")
            except Exception as e:
                st.error(f"Error al procesar: {e}")

# --- VALIDACIÓN DE DATOS ---
if os.path.exists(ARCHIVO_DATOS):
    df = pd.read_csv(ARCHIVO_DATOS)
    cols_texto = df.select_dtypes(include=['object', 'string']).columns.tolist()
    cols_numeros = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(cols_texto) > 0 and len(cols_numeros) > 0:
        cat = cols_texto[0]
        num1 = cols_numeros[0]
        num2 = cols_numeros[1] if len(cols_numeros) > 1 else num1
        
        df_agrupado = df.groupby(cat, as_index=False).sum()
        
        # --- DIVISIÓN PRINCIPAL: 70% Gráficos (Centro) | 30% Panel Lateral (Derecha) ---
        col_centro, col_derecha = st.columns([2.5, 1])
        
        with col_centro:
            st.title("Overview")
            
            # FILA 1: 4 Mini Tarjetas (KPIs)
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            total_num1 = df_agrupado[num1].sum()
            promedio_num1 = df_agrupado[num1].mean()
            
            kpi1.metric(label="Total Volumen", value=f"{total_num1:,.0f}", delta="6% vs mes anterior")
            kpi2.metric(label="Promedio", value=f"{promedio_num1:,.0f}", delta="-2% vs mes anterior", delta_color="inverse")
            kpi3.metric(label="Registros", value=len(df), delta="Activo")
            kpi4.metric(label="Categorías", value=len(df_agrupado), delta="Estable")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # FILA 2: Gráfico Combinado (Barras + Línea superpuesta)
            st.write(f"**Evolución de {num1} y {num2}**")
            fig_combo = go.Figure()
            # Añadir Barras
            fig_combo.add_trace(go.Bar(x=df_agrupado[cat], y=df_agrupado[num1], name="Volumen", marker_color='#4f81bd'))
            # Añadir Línea
            fig_combo.add_trace(go.Scatter(x=df_agrupado[cat], y=df_agrupado[num2], name="Tendencia", mode='lines+markers', line=dict(color='#c0504d', width=3)))
            
            fig_combo.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_combo, use_container_width=True)
            
            # FILA 3: Dos gráficos de Dona (Sencillo y Múltiple)
            dona1, dona2 = st.columns(2)
            with dona1:
                st.write("**Distribución Principal**")
                fig_d1 = px.pie(df_agrupado, names=cat, values=num1, hole=0.6)
                fig_d1.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
                st.plotly_chart(fig_d1, use_container_width=True)
                
            with dona2:
                st.write("**Desglose Secundario**")
                fig_d2 = px.pie(df_agrupado, names=cat, values=num2, hole=0.4)
                fig_d2.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_d2, use_container_width=True)

        # --- PANEL DERECHO: Perfil, Tarjeta y Feed ---
        with col_derecha:
            # Perfil
            st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/4140/4140048.png' width='80'></div>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; margin-bottom: 0;'>Henderson González</h4>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Project SHIIFT<br>Edit profile</p>", unsafe_allow_html=True)
            
            # Tarjeta Estilo Crédito
            st.markdown("**Cards**")
            st.markdown("""
            <div style='background: linear-gradient(135deg, #5b73e8, #4458b8); padding: 20px; border-radius: 15px; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h2 style='margin: 0; padding-bottom: 15px;'>$ 12,547.62</h2>
                <p style='margin: 0; font-family: monospace; font-size: 16px; letter-spacing: 2px;'>6698 0236 7899 3301</p>
                <div style='display: flex; justify-content: space-between; margin-top: 15px; font-size: 10px; color: #e0e0e0;'>
                    <span>EXPIRATION DATE<br>22 / 07</span>
                    <span>CVV<br>015</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Actividades Recientes (Últimos registros de la tabla)
            st.markdown("**Recent activities**")
            st.write("Today")
            
            # Tomamos las últimas 4 filas de tu Excel para simular el historial de transacciones
            ultimos_registros = df.tail(4)
            for index, row in ultimos_registros.iterrows():
                # Formato visual imitando la lista de transferencias
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 10px 0;'>
                    <div>
                        <span style='font-weight: bold; font-size: 14px;'>{row[cat]}</span><br>
                        <span style='color: gray; font-size: 11px;'>PROCESADO</span>
                    </div>
                    <div style='font-weight: bold; color: #4458b8;'>{row[num1]:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Tu hoja RESUMEN debe tener al menos una columna de texto y una numérica.")
else:
    st.info("Ingresa en el menú lateral izquierdo para cargar el archivo Control Oficial SHIIFT 2.")

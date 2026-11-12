import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN DE LA APLICACIÓN ---
st.set_page_config(page_title="SHIIFT – Seguimiento de Requerimientos", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

DB_PATH = "shiift_master_db.csv"
COLOR_PALETTE = ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a', '#ff7c43', '#ffa600', '#1f77b4', '#2ca02c']

st.markdown("""
    <style>
    /* Estilos para Dashboard Empresarial */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #2f4b7c;
    }
    .stDataFrame { border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE AUTENTICACIÓN ---
if 'rol' not in st.session_state:
    st.session_state.rol = None

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2219/2219436.png", width=60)
    st.markdown("### SHIIFT")
    st.caption("Seguimiento de Requerimientos")
    st.markdown("---")
    
    if st.session_state.rol is None:
        st.markdown("**🔒 Iniciar Sesión**")
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", use_container_width=True):
            if usuario == "henderson.gonzalez" and password == "1234":
                st.session_state.rol = "Administrador"
                st.rerun()
            elif usuario == "visor" and password == "visor123":
                st.session_state.rol = "Usuario de consulta"
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.stop()
    else:
        st.success(f"👤 Perfil: {st.session_state.rol}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.rol = None
            st.rerun()
        
        st.markdown("---")
        
        # --- 3. EXTRACCIÓN Y CARGA DE DATOS (EXCLUSIÓN DE RESÚMENES) ---
        if st.session_state.rol == "Administrador":
            st.markdown("### ⚙️ Actualización de Datos")
            archivo_subido = st.file_uploader("CARGAR EXCEL", type=["xlsb", "xlsx"])
            
            if st.button("🔄 PROCESAR ARCHIVO", type="primary", use_container_width=True):
                if archivo_subido:
                    with st.spinner("Procesando hojas de detalle..."):
                        try:
                            engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                            xl = pd.ExcelFile(archivo_subido, engine=engine)
                            
                            # REGLA OBLIGATORIA: Excluir RESUMEN y RESUMEN MACRO
                            hojas_validas = [h for h in xl.sheet_names if "RESUMEN" not in h.upper() and "PIVOT" not in h.upper()]
                            
                            if not hojas_validas:
                                st.error("No se encontraron hojas individuales válidas.")
                            else:
                                df_master = pd.DataFrame()
                                for hoja in hojas_validas:
                                    # header=2 asumiendo que los títulos están en la fila 3 como se validó anteriormente
                                    df_temp = pd.read_excel(archivo_subido, sheet_name=hoja, engine=engine, header=2)
                                    df_temp['FUENTE_MÓDULO'] = hoja
                                    df_master = pd.concat([df_master, df_temp], ignore_index=True)
                                
                                df_master.columns = df_master.columns.astype(str).str.strip().str.upper()
                                
                                # Consolidar duplicados por ID WRICEF
                                id_col = next((c for c in df_master.columns if "WRICEF" in c or "ID" == c or "ID " in c), None)
                                if id_col:
                                    df_master = df_master.drop_duplicates(subset=[id_col], keep='last')
                                
                                df_master = df_master.fillna("Sin Asignar")
                                df_master.to_csv(DB_PATH, index=False)
                                st.success(f"Éxito: {len(df_master)} requerimientos únicos cargados.")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error estructural en el Excel: {e}")
                else:
                    st.warning("Adjunta un documento primero.")

# --- 4. LECTURA Y MAPEO DE COLUMNAS INTELIGENTE ---
if not os.path.exists(DB_PATH):
    st.info("Plataforma inactiva. El Administrador debe cargar el archivo Excel base utilizando el panel lateral.")
    st.stop()

df = pd.read_csv(DB_PATH)

def mapear_col(palabras, default):
    for col in df.columns:
        if any(p in col for p in palabras): return col
    return default

col_id = mapear_col(["WRICEF", "ID"], "ID")
col_req = mapear_col(["NOMBRE", "REQUERIMIENTO", "DESCRIP"], "REQUERIMIENTO")
col_mod = mapear_col(["MODULO", "MÓDULO", "FUENTE_MÓDULO"], "FUENTE_MÓDULO")
col_est = mapear_col(["ESTADO", "STATUS"], "ESTADO")
col_res = mapear_col(["RESPONSABLE", "BP", "OWNER"], "RESPONSABLE")
col_spr = mapear_col(["SPRINT"], "SPRINT")
col_fab = mapear_col(["FABRICA", "FÁBRICA", "DESARROLLO"], "FABRICA")
col_tip = mapear_col(["TIPO"], "TIPO")
col_pri = mapear_col(["PRIORIDAD", "PRIORIZACION"], "PRIORIDAD")
col_fec = mapear_col(["FECHA", "ESTIMADA"], "FECHA")

# --- 5. MOTOR DE FILTROS DINÁMICOS Y DEPENDIENTES ---
st.markdown("### 🔍 Buscador y Filtros Dinámicos")
st.caption("Los filtros están conectados. Al seleccionar una opción, los demás filtros se ajustarán a los datos disponibles.")

df_filt = df.copy()

# Fila 1 de Filtros
f1, f2, f3, f4 = st.columns(4)
with f1:
    mod_opts = sorted(df_filt[col_mod].unique())
    sel_mod = st.multiselect("1. Módulo", mod_opts)
    if sel_mod: df_filt = df_filt[df_filt[col_mod].isin(sel_mod)]

with f2:
    res_opts = sorted(df_filt[col_res].unique())
    sel_res = st.multiselect("2. Responsable", res_opts)
    if sel_res: df_filt = df_filt[df_filt[col_res].isin(sel_res)]

with f3:
    spr_opts = sorted(df_filt[col_spr].unique())
    sel_spr = st.multiselect("3. Sprint", spr_opts)
    if sel_spr: df_filt = df_filt[df_filt[col_spr].isin(sel_spr)]

with f4:
    est_opts = sorted(df_filt[col_est].unique())
    sel_est = st.multiselect("4. Estado", est_opts)
    if sel_est: df_filt = df_filt[df_filt[col_est].isin(sel_est)]

# Fila 2 de Filtros
f5, f6, f7, f8 = st.columns(4)
with f5:
    fab_opts = sorted(df_filt[col_fab].unique())
    sel_fab = st.multiselect("5. Fábrica de Desarrollo", fab_opts)
    if sel_fab: df_filt = df_filt[df_filt[col_fab].isin(sel_fab)]

with f6:
    pri_opts = sorted(df_filt.get(col_pri, pd.Series(["N/A"])).unique())
    sel_pri = st.multiselect("6. Prioridad", pri_opts)
    if sel_pri and col_pri in df_filt.columns: df_filt = df_filt[df_filt[col_pri].isin(sel_pri)]

with f7:
    tip_opts = sorted(df_filt.get(col_tip, pd.Series(["N/A"])).unique())
    sel_tip = st.multiselect("7. Tipo", tip_opts)
    if sel_tip and col_tip in df_filt.columns: df_filt = df_filt[df_filt[col_tip].isin(sel_tip)]

with f8:
    fec_opts = sorted(df_filt.get(col_fec, pd.Series(["N/A"])).unique())
    sel_fec = st.multiselect("8. Fecha Estimada", fec_opts)
    if sel_fec and col_fec in df_filt.columns: df_filt = df_filt[df_filt[col_fec].isin(sel_fec)]

if st.button("🧹 Limpiar todos los filtros", use_container_width=False):
    st.rerun()

st.markdown("---")

# --- 6. CÁLCULO DE INDICADORES (KPIs) ---
est_str = df_filt[col_est].astype(str).str.upper()
completados = len(df_filt[est_str.str.contains("360|CARGADO|COMPLETADO|TERMINADO|FINALIZADO|APROBADO", regex=True)])
desestimados = len(df_filt[est_str.str.contains("DESESTIMADO|CANCELADO|RECHAZADO", regex=True)])
pendientes = len(df_filt[est_str.str.contains("PENDIENTE|SIN INICIAR|BACKLOG", regex=True)])
en_proceso = len(df_filt) - completados - desestimados - pendientes

total_req = len(df_filt)
avance_pct = (completados / (total_req - desestimados) * 100) if (total_req - desestimados) > 0 else 0

st.markdown(f"### Resultados de Búsqueda: {total_req} Requerimientos")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Requerimientos", total_req)
k2.metric("✅ Completados", completados)
k3.metric("⏳ Pendientes", pendientes)
k4.metric("⚙️ En Proceso", en_proceso)
k5.metric("🚫 Desestimados", desestimados)
k6.metric("🚀 Avance General", f"{avance_pct:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. GRÁFICAS INTERACTIVAS (ADAPTADAS A LOS FILTROS) ---
if total_req > 0:
    t1, t2 = st.tabs(["📊 Visor de Gráficos", "📋 Detalle de Requerimientos"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**1. Distribución por Estado**")
            fig1 = px.pie(df_filt, names=col_est, hole=0.4, color_discrete_sequence=COLOR_PALETTE)
            fig1.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            st.markdown("**2. Requerimientos por Módulo**")
            df_m = df_filt.groupby(col_mod).size().reset_index(name='Total').sort_values('Total', ascending=True)
            fig2 = px.bar(df_m, x='Total', y=col_mod, orientation='h', color=col_mod, color_discrete_sequence=COLOR_PALETTE)
            fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**3. Avance por Módulo**")
            def calc_adv(g):
                t = len(g)
                d = len(g[g[col_est].astype(str).str.upper().str.contains("DESESTIMADO|CANCELADO", regex=True)])
                c = len(g[g[col_est].astype(str).str.upper().str.contains("360|CARGADO|COMPLETADO|TERMINADO|FINALIZADO|APROBADO", regex=True)])
                return (c / (t - d) * 100) if (t - d) > 0 else 0
                
            df_adv = df_filt.groupby(col_mod).apply(calc_adv).reset_index(name='Avance (%)')
            fig3 = px.bar(df_adv, x=col_mod, y='Avance (%)', color='Avance (%)', color_continuous_scale="Teal")
            fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig3, use_container_width=True)
            
        with c4:
            st.markdown("**4. Distribución por Sprint**")
            df_s = df_filt.groupby(col_spr).size().reset_index(name='Total')
            fig4 = px.bar(df_s, x=col_spr, y='Total', color_discrete_sequence=['#d45087'])
            fig4.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig4, use_container_width=True)

        c5, c6 = st.columns(2)
        with c5:
            st.markdown("**5. Requerimientos por Responsable**")
            df_r = df_filt.groupby(col_res).size().reset_index(name='Total').sort_values('Total', ascending=False)
            fig5 = px.bar(df_r, x=col_res, y='Total', color=col_res, color_discrete_sequence=COLOR_PALETTE)
            fig5.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig5, use_container_width=True)
            
        with c6:
            st.markdown("**6. Estados por Fábrica de Desarrollo**")
            df_f = df_filt.groupby([col_fab, col_est]).size().reset_index(name='Total')
            fig6 = px.bar(df_f, x=col_fab, y='Total', color=col_est, barmode='stack', color_discrete_sequence=COLOR_PALETTE)
            fig6.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig6, use_container_width=True)

        c7, c8 = st.columns(2)
        with c7:
            st.markdown("**7. Priorización**")
            if col_pri in df_filt.columns:
                fig7 = px.pie(df_filt, names=col_pri, hole=0.3, color_discrete_sequence=['#ff7c43', '#ffa600', '#2f4b7c'])
                fig7.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig7, use_container_width=True)
                
        with c8:
            st.markdown("**8. Comparativo General**")
            df_gen = pd.DataFrame({"Fase": ["Completados", "En Proceso", "Pendientes"], "Cantidad": [completados, en_proceso, pendientes]})
            fig8 = px.funnel(df_gen, x='Cantidad', y='Fase', color_discrete_sequence=['#1f77b4'])
            fig8.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig8, use_container_width=True)

    # --- 8. TABLA DE CONSULTA DETALLADA ---
    with t2:
        st.markdown(f"**Registros Encontrados: {total_req}**")
        
        busqueda_txt = st.text_input("Buscar palabra clave en los resultados actuales (ID, Nombre, Observaciones):")
        df_tabla = df_filt.copy()
        
        if busqueda_txt:
            mask = df_tabla.astype(str).apply(lambda x: x.str.contains(busqueda_txt, case=False, na=False)).any(axis=1)
            df_tabla = df_tabla[mask]
        
        def color_estado(val):
            v = str(val).upper()
            if any(x in v for x in ["360", "CARGADO", "COMPLETADO", "TERMINADO"]): return 'background-color: #d4edda; color: #155724;'
            if any(x in v for x in ["DESESTIMADO", "CANCELADO"]): return 'background-color: #f8d7da; color: #721c24;'
            if any(x in v for x in ["PENDIENTE", "SIN INICIAR"]): return 'background-color: #fff3cd; color: #856404;'
            return 'background-color: #cce5ff; color: #004085;'
            
        st.dataframe(df_tabla.style.map(color_estado, subset=[col_est]), use_container_width=True, height=600)
        
        # Consultar detalle individual
        st.markdown("### 🔍 Consultar Detalle Individual")
        req_seleccionado = st.selectbox("Selecciona un ID WRICEF para abrir el registro completo:", [""] + df_tabla[col_id].astype(str).tolist())
        
        if req_seleccionado:
            detalle = df_tabla[df_tabla[col_id].astype(str) == req_seleccionado].iloc[0]
            st.json(detalle.to_dict())
            
        if st.session_state.rol in ["Administrador", "Usuario de consulta"]:
            st.download_button("📥 Exportar Resultados a CSV", df_tabla.to_csv(index=False).encode('utf-8'), "Busqueda_SHIIFT.csv", "text/csv")

else:
    st.warning("No se encontraron registros que coincidan con la combinación de filtros seleccionada.")

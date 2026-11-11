import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN UX/UI ---
st.set_page_config(page_title="SHIIFT – Seguimiento de Requerimientos", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

DB_PATH = "shiift_master_details.csv"
COLOR_PALETTE = ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a', '#ff7c43', '#ffa600']

st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        border-left: 5px solid #2f4b7c;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. AUTENTICACIÓN Y ROLES ---
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
            if usuario == "admin" and password == "admin123":
                st.session_state.rol = "Administrador"
                st.rerun()
            elif usuario == "visor" and password == "visor123":
                st.session_state.rol = "Usuario de consulta"
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.stop()
    else:
        st.success(f"👤 {st.session_state.rol}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.rol = None
            st.rerun()
            
        st.markdown("---")
        menu = st.radio("Navegación", ["📊 Dashboard General", "🧩 Sección de Módulos", "📋 Consulta de Requerimientos"])
        st.markdown("---")
        
        # --- LÓGICA DE EXTRACCIÓN (REGLA PRINCIPAL) ---
        if st.session_state.rol == "Administrador":
            st.markdown("### ⚙️ Carga de Datos")
            archivo_subido = st.file_uploader("CARGAR / ACTUALIZAR EXCEL", type=["xlsb", "xlsx"])
            if st.button("🔄 PROCESAR ARCHIVO", type="primary", use_container_width=True):
                if archivo_subido:
                    with st.spinner("Leyendo hojas individuales y excluyendo resúmenes..."):
                        try:
                            engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                            xl = pd.ExcelFile(archivo_subido, engine=engine)
                            
                            # EXCLUSIÓN ESTRICTA DE HOJAS DE RESUMEN
                            hojas_detalle = [h for h in xl.sheet_names if "RESUMEN" not in h.upper() and "PIVOT" not in h.upper()]
                            
                            if not hojas_detalle:
                                st.error("No se encontraron hojas de detalle válidas.")
                            else:
                                df_master = pd.DataFrame()
                                for hoja in hojas_detalle:
                                    df_temp = pd.read_excel(archivo_subido, sheet_name=hoja, engine=engine)
                                    df_temp['FUENTE_HOJA'] = hoja
                                    df_master = pd.concat([df_master, df_temp], ignore_index=True)
                                
                                df_master.columns = df_master.columns.astype(str).str.strip().str.upper()
                                
                                # Auto-detectar ID para eliminar duplicados reales
                                id_col_temp = next((col for col in df_master.columns if "WRICEF" in col or "ID" == col or "ID " in col), None)
                                
                                if id_col_temp:
                                    registros_previos = len(df_master)
                                    # Se elimina duplicidad manteniendo el último registro actualizado
                                    df_master = df_master.drop_duplicates(subset=[id_col_temp], keep='last')
                                    st.info(f"Se eliminaron {registros_previos - len(df_master)} registros duplicados entre hojas.")
                                
                                df_master = df_master.fillna("Sin Asignar")
                                df_master.to_csv(DB_PATH, index=False)
                                st.success(f"Base actualizada. {len(df_master)} requerimientos únicos consolidados.")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error de estructura: {e}")
                else:
                    st.warning("Adjunta un documento primero.")

# --- 3. PREPARACIÓN DE DATOS Y MAPEO ---
if not os.path.exists(DB_PATH):
    st.info("La plataforma está vacía. El administrador debe cargar el archivo Excel base, asegurando que contenga las hojas de detalle.")
    st.stop()

df = pd.read_csv(DB_PATH)

def buscar_col(palabras, default):
    for col in df.columns:
        if any(p in col for p in palabras):
            return col
    return default

col_id = buscar_col(["WRICEF", "ID"], "ID")
col_req = buscar_col(["NOMBRE", "REQUERIMIENTO", "DESCRIP"], "REQUERIMIENTO")
col_mod = buscar_col(["MODULO", "MÓDULO"], "FUENTE_HOJA")
col_est = buscar_col(["ESTADO", "STATUS"], "ESTADO")
col_res = buscar_col(["RESPONSABLE", "BP", "OWNER"], "RESPONSABLE")
col_spr = buscar_col(["SPRINT"], "SPRINT")
col_fab = buscar_col(["FABRICA", "FÁBRICA", "DESARROLLO"], "FABRICA")
col_tip = buscar_col(["TIPO"], "TIPO")
col_pri = buscar_col(["PRIORIDAD", "PRIORIZACION"], "PRIORIDAD")
col_fec = buscar_col(["FECHA"], "FECHA")

# --- 4. FILTROS GLOBALES ---
with st.expander("🔍 FILTROS DINÁMICOS DE INFORMACIÓN", expanded=False):
    f1, f2, f3, f4 = st.columns(4)
    with f1: 
        sel_mod = st.multiselect("Módulo", sorted(df[col_mod].unique()))
        sel_fab = st.multiselect("Fábrica", sorted(df[col_fab].unique()))
    with f2: 
        sel_est = st.multiselect("Estado", sorted(df[col_est].unique()))
        sel_tip = st.multiselect("Tipo", sorted(df.get(col_tip, pd.Series(["N/A"])).unique()))
    with f3: 
        sel_res = st.multiselect("Responsable", sorted(df[col_res].unique()))
        sel_pri = st.multiselect("Prioridad", sorted(df.get(col_pri, pd.Series(["N/A"])).unique()))
    with f4: 
        sel_spr = st.multiselect("Sprint", sorted(df[col_spr].unique()))
        if st.button("🧹 Limpiar todos los filtros", use_container_width=True):
            st.rerun()

df_filt = df.copy()
if sel_mod: df_filt = df_filt[df_filt[col_mod].isin(sel_mod)]
if sel_est: df_filt = df_filt[df_filt[col_est].isin(sel_est)]
if sel_res: df_filt = df_filt[df_filt[col_res].isin(sel_res)]
if sel_spr: df_filt = df_filt[df_filt[col_spr].isin(sel_spr)]
if sel_fab: df_filt = df_filt[df_filt[col_fab].isin(sel_fab)]
if sel_tip and col_tip in df_filt.columns: df_filt = df_filt[df_filt[col_tip].isin(sel_tip)]
if sel_pri and col_pri in df_filt.columns: df_filt = df_filt[df_filt[col_pri].isin(sel_pri)]

# --- LÓGICA DE ESTADOS ---
est_str = df_filt[col_est].astype(str).str.upper()
df_comp = df_filt[est_str.str.contains("360|CARGADO|COMPLETADO|TERMINADO|FINALIZADO|APROBADO", regex=True)]
df_des  = df_filt[est_str.str.contains("DESESTIMADO|CANCELADO|RECHAZADO", regex=True)]
df_pend = df_filt[est_str.str.contains("PENDIENTE|SIN INICIAR|BACKLOG", regex=True)]
df_proc = df_filt[~df_filt.index.isin(df_comp.index.union(df_des.index).union(df_pend.index))]

# --- 5. DASHBOARD GENERAL ---
if menu == "📊 Dashboard General":
    st.markdown("## Resumen Ejecutivo del Proyecto")
    
    total = len(df_filt)
    comp = len(df_comp)
    pend = len(df_pend)
    proc = len(df_proc)
    des = len(df_des)
    pct_avance = (comp / (total - des) * 100) if (total - des) > 0 else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Requerimientos", f"{total}")
    k2.metric("✅ Completados", f"{comp}")
    k3.metric("⏳ Pendientes", f"{pend}")
    k4.metric("⚙️ En Proceso", f"{proc}")
    k5.metric("🚫 Desestimados", f"{des}")
    k6.metric("🚀 Avance General", f"{pct_avance:.1f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Requerimientos por estado**")
        fig1 = px.pie(df_filt, names=col_est, hole=0.5, color_discrete_sequence=COLOR_PALETTE)
        fig1.update_layout(margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)
    
    with c2:
        st.markdown("**2. Requerimientos por módulo**")
        df_m = df_filt.groupby(col_mod).size().reset_index(name='Total').sort_values('Total', ascending=True)
        fig2 = px.bar(df_m, x='Total', y=col_mod, orientation='h', color_discrete_sequence=['#2f4b7c'])
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**3. Avance por módulo (%)**")
        # Cálculo de avance por módulo
        def calc_avance(g):
            t = len(g)
            d = len(g[g[col_est].astype(str).str.upper().str.contains("DESESTIMADO|CANCELADO|RECHAZADO", regex=True)])
            c = len(g[g[col_est].astype(str).str.upper().str.contains("360|CARGADO|COMPLETADO|TERMINADO|FINALIZADO|APROBADO", regex=True)])
            return (c / (t - d) * 100) if (t - d) > 0 else 0
            
        df_adv = df_filt.groupby(col_mod).apply(calc_avance).reset_index(name='Avance')
        fig3 = px.bar(df_adv, x=col_mod, y='Avance', color='Avance', color_continuous_scale="Blues")
        fig3.update_layout(margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)
        
    with c4:
        st.markdown("**4. Requerimientos por Sprint**")
        df_s = df_filt.groupby(col_spr).size().reset_index(name='Total')
        fig4 = px.bar(df_s, x=col_spr, y='Total', color_discrete_sequence=['#ff7c43'])
        fig4.update_layout(margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig4, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown("**5. Requerimientos por responsable**")
        df_r = df_filt.groupby(col_res).size().reset_index(name='Total').sort_values('Total', ascending=False)
        fig5 = px.bar(df_r, x=col_res, y='Total', color=col_res, color_discrete_sequence=COLOR_PALETTE)
        fig5.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig5, use_container_width=True)
        
    with c6:
        st.markdown("**6. Estados por fábrica de desarrollo**")
        df_f = df_filt.groupby([col_fab, col_est]).size().reset_index(name='Total')
        fig6 = px.bar(df_f, x=col_fab, y='Total', color=col_est, barmode='stack', color_discrete_sequence=COLOR_PALETTE)
        fig6.update_layout(margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig6, use_container_width=True)

    c7, c8 = st.columns(2)
    with c7:
        st.markdown("**7. Priorización**")
        if col_pri in df_filt.columns:
            fig7 = px.pie(df_filt, names=col_pri, hole=0.3, color_discrete_sequence=['#d45087', '#a05195', '#665191'])
            fig7.update_layout(margin=dict(l=0, r=0, t=10, b=10))
            st.plotly_chart(fig7, use_container_width=True)
        else:
            st.info("Columna de priorización no encontrada en el detalle.")
            
    with c8:
        st.markdown("**8. Comparativo de Avance General**")
        df_gen = pd.DataFrame({
            "Fase": ["Completados", "En Proceso", "Pendientes"],
            "Cantidad": [comp, proc, pend]
        })
        fig8 = px.funnel(df_gen, x='Cantidad', y='Fase', color_discrete_sequence=['#2f4b7c'])
        fig8.update_layout(margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig8, use_container_width=True)

# --- 6. SECCIÓN DE MÓDULOS ---
elif menu == "🧩 Sección de Módulos":
    st.markdown("## Auditoría Detallada por Módulo")
    
    modulos_list = sorted(df_filt[col_mod].unique())
    if not modulos_list:
        st.warning("No hay módulos disponibles con los filtros actuales.")
    else:
        for modulo in modulos_list:
            df_m = df_filt[df_filt[col_mod] == modulo]
            
            m_comp = len(df_m[df_m[col_est].astype(str).str.upper().str.contains("360|CARGADO|COMPLETADO|TERMINADO|FINALIZADO|APROBADO", regex=True)])
            m_des = len(df_m[df_m[col_est].astype(str).str.upper().str.contains("DESESTIMADO|CANCELADO|RECHAZADO", regex=True)])
            m_pend = len(df_m[df_m[col_est].astype(str).str.upper().str.contains("PENDIENTE|SIN INICIAR|BACKLOG", regex=True)])
            m_proc = len(df_m) - m_comp - m_des - m_pend
            m_avance = (m_comp / (len(df_m) - m_des) * 100) if (len(df_m) - m_des) > 0 else 0
            
            with st.expander(f"📦 MÓDULO: {modulo} — {len(df_m)} GAPs ({m_avance:.1f}% Avance)", expanded=False):
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Total", len(df_m))
                m2.metric("Completados", m_comp)
                m3.metric("En Proceso", m_proc)
                m4.metric("Pendientes", m_pend)
                m5.metric("Avance", f"{m_avance:.1f}%")
                
                st.dataframe(df_m[[col_id, col_req, col_est, col_res, col_spr]], use_container_width=True, hide_index=True)

# --- 7. CONSULTA DE REQUERIMIENTOS ---
elif menu == "📋 Consulta de Requerimientos":
    st.markdown("## Base Maestra de Requerimientos (Detalle)")
    
    col_buscar, _ = st.columns([2, 1])
    with col_buscar:
        texto_busqueda = st.text_input("🔍 Buscar por ID WRICEF o Nombre del Requerimiento:")
        
    df_tabla = df_filt.copy()
    if texto_busqueda:
        mask = df_tabla[col_req].astype(str).str.contains(texto_busqueda, case=False) | df_tabla[col_id].astype(str).str.contains(texto_busqueda, case=False)
        df_tabla = df_tabla[mask]
        
    st.caption(f"Se encontraron {len(df_tabla)} registros válidos.")
    
    def color_estado(val):
        v = str(val).upper()
        if any(x in v for x in ["360", "CARGADO", "COMPLETADO"]): return 'background-color: #d4edda; color: #155724;'
        if any(x in v for x in ["DESESTIMADO", "CANCELADO"]): return 'background-color: #f8d7da; color: #721c24;'
        if any(x in v for x in ["PENDIENTE", "SIN INICIAR"]): return 'background-color: #fff3cd; color: #856404;'
        return 'background-color: #cce5ff; color: #004085;'
        
    st.dataframe(df_tabla.style.map(color_estado, subset=[col_est]), use_container_width=True, height=500)
    
    if st.session_state.rol in ["Administrador", "Usuario de consulta"]:
        csv = df_tabla.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Exportar Resultados a Excel (CSV)", data=csv, file_name="Requerimientos_SHIIFT.csv", mime="text/csv")

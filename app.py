import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Control SHIIFT", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Colores corporativos (Limpio y profesional)
COLOR_PALETTE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
DB_PATH = "shiift_database.csv"

# CSS para mejorar el diseño de las tarjetas KPI y ocultar menús por defecto
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE USUARIOS Y ROLES ---
if 'rol' not in st.session_state:
    st.session_state.rol = None

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2219/2219436.png", width=70)
    st.markdown("## Control SHIIFT")
    st.caption("Plataforma Ejecutiva de Seguimiento")
    st.markdown("---")
    
    if st.session_state.rol is None:
        st.markdown("### Acceso al Sistema")
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
        # Menú de Navegación
        seccion = st.radio("Navegación", [
            "📈 Resumen General", 
            "🔍 Consulta de Información", 
            "🧩 Sección de Módulos"
        ])
        st.markdown("---")
        
        # Opción exclusiva de Administrador: Cargar/Actualizar Excel
        if st.session_state.rol == "Administrador":
            st.markdown("### ⚙️ Administración")
            archivo_subido = st.file_uploader("Cargar / Actualizar Excel", type=["xlsb", "xlsx"])
            if st.button("🔄 ACTUALIZAR INFORMACIÓN", type="primary", use_container_width=True):
                if archivo_subido:
                    with st.spinner("Procesando y validando hojas de detalle..."):
                        try:
                            engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                            xl = pd.ExcelFile(archivo_subido, engine=engine)
                            
                            # Ignorar hojas de resumen para evitar duplicados
                            hojas_validas = [h for h in xl.sheet_names if "RESUMEN" not in h.upper() and "PIVOT" not in h.upper()]
                            
                            df_master = pd.DataFrame()
                            for hoja in hojas_validas:
                                df_temp = pd.read_excel(archivo_subido, sheet_name=hoja, engine=engine)
                                df_temp['HOJA_ORIGEN'] = hoja # Para trazabilidad
                                df_master = pd.concat([df_master, df_temp], ignore_index=True)
                            
                            df_master.columns = df_master.columns.astype(str).str.strip().str.upper()
                            df_master = df_master.fillna("Sin asignar")
                            
                            # Guardar en base de datos local persistente
                            df_master.to_csv(DB_PATH, index=False)
                            st.success(f"¡Actualización exitosa! Se procesaron {len(df_master)} requerimientos.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al leer el archivo: {e}")
                else:
                    st.warning("Selecciona un archivo Excel primero.")

# --- 3. LECTURA Y AUTODETECCIÓN DE COLUMNAS ---
if not os.path.exists(DB_PATH):
    st.info("👋 Bienvenido a SHIIFT. El sistema está vacío. Inicia sesión como administrador para cargar el archivo Excel base.")
    st.stop()

df = pd.read_csv(DB_PATH)

# Función inteligente para encontrar nombres de columnas en el Excel
def buscar_columna(palabras_clave, default):
    for col in df.columns:
        if any(palabra in col for palabra in palabras_clave):
            return col
    return default

col_id = buscar_columna(["WRICEF", "ID"], "ID")
col_req = buscar_columna(["NOMBRE", "REQUERIMIENTO", "DESCRIPCI"], "REQUERIMIENTO")
col_mod = buscar_columna(["MODULO", "MÓDULO"], "HOJA_ORIGEN")
col_est = buscar_columna(["ESTADO", "STATUS"], "ESTADO")
col_res = buscar_columna(["RESPONSABLE", "BP", "OWNER"], "RESPONSABLE")
col_spr = buscar_columna(["SPRINT"], "SPRINT")
col_fab = buscar_columna(["FABRICA", "FÁBRICA", "DESARROLLO"], "FABRICA")
col_tip = buscar_columna(["TIPO"], "TIPO")
col_pri = buscar_columna(["PRIORIDAD", "PRIORIZACION"], "PRIORIDAD")

# --- 4. FILTROS GLOBALES INTERACTIVOS ---
st.markdown("### 🎛️ Filtros Globales")
f1, f2, f3, f4, f5, f6, f7 = st.columns(7)
with f1: sel_mod = st.multiselect("Módulo", sorted(df[col_mod].unique()))
with f2: sel_est = st.multiselect("Estado", sorted(df[col_est].unique()))
with f3: sel_res = st.multiselect("Responsable", sorted(df[col_res].unique()))
with f4: sel_spr = st.multiselect("Sprint", sorted(df[col_spr].unique()))
with f5: sel_fab = st.multiselect("Fábrica", sorted(df[col_fab].unique()))
with f6: sel_tip = st.multiselect("Tipo", sorted(df.get(col_tip, pd.Series(["N/A"])).unique()))
with f7: sel_pri = st.multiselect("Prioridad", sorted(df.get(col_pri, pd.Series(["N/A"])).unique()))

# Botón para limpiar filtros
if st.button("🧹 Limpiar Filtros"):
    st.rerun()

# Aplicar filtros al DataFrame
df_filt = df.copy()
if sel_mod: df_filt = df_filt[df_filt[col_mod].isin(sel_mod)]
if sel_est: df_filt = df_filt[df_filt[col_est].isin(sel_est)]
if sel_res: df_filt = df_filt[df_filt[col_res].isin(sel_res)]
if sel_spr: df_filt = df_filt[df_filt[col_spr].isin(sel_spr)]
if sel_fab: df_filt = df_filt[df_filt[col_fab].isin(sel_fab)]
if sel_tip and col_tip in df_filt.columns: df_filt = df_filt[df_filt[col_tip].isin(sel_tip)]
if sel_pri and col_pri in df_filt.columns: df_filt = df_filt[df_filt[col_pri].isin(sel_pri)]

st.markdown("---")

# Categorización de Estados (Lógica de negocio)
estados_str = df_filt[col_est].astype(str).str.upper()
completados = df_filt[estados_str.str.contains("360|CARGADO|COMPLETADO|TERMINADO|FINALIZADO|APROBADO", regex=True)]
desestimados = df_filt[estados_str.str.contains("DESESTIMADO|CANCELADO|RECHAZADO", regex=True)]
pendientes = df_filt[estados_str.str.contains("PENDIENTE|SIN INICIAR|BACKLOG", regex=True)]
# En proceso es todo lo que no está en los otros 3
en_proceso = df_filt[~df_filt.index.isin(completados.index.union(desestimados.index).union(pendientes.index))]

# --- 5. VISTAS DE LA APLICACIÓN ---

if seccion == "📈 Resumen General":
    # TARJETAS DE INDICADORES (KPIs)
    total_req = len(df_filt)
    val_comp = len(completados)
    val_pend = len(pendientes)
    val_proc = len(en_proceso)
    val_des = len(desestimados)
    
    # Porcentaje de Avance (Completados / (Total - Desestimados))
    base_avance = total_req - val_des
    pct_avance = (val_comp / base_avance * 100) if base_avance > 0 else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📋 Total Requerimientos", f"{total_req}")
    k2.metric("✅ Completados", f"{val_comp}")
    k3.metric("⏳ Pendientes", f"{val_pend}")
    k4.metric("⚙️ En Proceso", f"{val_proc}")
    k5.metric("🚫 Desestimados", f"{val_des}")
    k6.metric("🚀 Avance General", f"{pct_avance:.1f}%")
    
    st.write("<br>", unsafe_allow_html=True)
    
    # GRÁFICOS INTERACTIVOS
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Cantidad de Requerimientos por Estado**")
        fig1 = px.pie(df_filt, names=col_est, hole=0.4, color_discrete_sequence=COLOR_PALETTE)
        fig1.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig1, use_container_width=True)
        
    with c2:
        st.markdown("**Cantidad de Requerimientos por Módulo**")
        df_mod_chart = df_filt.groupby(col_mod).size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=False)
        fig2 = px.bar(df_mod_chart, x=col_mod, y='Cantidad', color=col_mod, color_discrete_sequence=COLOR_PALETTE)
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Cantidad de Requerimientos por Sprint**")
        df_spr_chart = df_filt.groupby(col_spr).size().reset_index(name='Cantidad')
        fig3 = px.bar(df_spr_chart, x=col_spr, y='Cantidad', color_discrete_sequence=['#ff7f0e'])
        fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig3, use_container_width=True)
        
    with c4:
        st.markdown("**Distribución por Fábrica de Desarrollo**")
        fig4 = px.pie(df_filt, names=col_fab, color_discrete_sequence=COLOR_PALETTE)
        fig4.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("**Cantidad de Requerimientos por Responsable (Top 15)**")
    df_res_chart = df_filt.groupby(col_res).size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=True).tail(15)
    fig5 = px.bar(df_res_chart, x='Cantidad', y=col_res, orientation='h', color_discrete_sequence=['#2ca02c'])
    fig5.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig5, use_container_width=True)

elif seccion == "🔍 Consulta de Información":
    st.markdown("### Base de Datos Completa")
    
    col_busqueda, col_vacia = st.columns([2, 1])
    with col_busqueda:
        busqueda = st.text_input("🔍 Buscar requerimiento por ID o Nombre:")
    
    df_tabla = df_filt.copy()
    if busqueda:
        mask = df_tabla[col_req].astype(str).str.contains(busqueda, case=False) | df_tabla[col_id].astype(str).str.contains(busqueda, case=False)
        df_tabla = df_tabla[mask]
        
    st.caption(f"Mostrando {len(df_tabla)} registros en pantalla.")
    st.dataframe(df_tabla, use_container_width=True, height=500)
    
    st.markdown("### 📑 Detalles del Requerimiento")
    lista_ids = df_tabla[col_id].astype(str).unique().tolist()
    
    if lista_ids and lista_ids[0] != "Sin asignar":
        req_seleccionado = st.selectbox("Selecciona un ID WRICEF para ver su información detallada:", lista_ids)
        if req_seleccionado:
            detalle = df_tabla[df_tabla[col_id].astype(str) == req_seleccionado].iloc[0]
            
            d1, d2, d3 = st.columns(3)
            with d1:
                st.info(f"**Módulo:** {detalle.get(col_mod, 'N/A')}")
                st.info(f"**Responsable:** {detalle.get(col_res, 'N/A')}")
                st.info(f"**Estado:** {detalle.get(col_est, 'N/A')}")
            with d2:
                st.info(f"**Fábrica:** {detalle.get(col_fab, 'N/A')}")
                st.info(f"**Sprint:** {detalle.get(col_spr, 'N/A')}")
                st.info(f"**Prioridad:** {detalle.get(col_pri, 'N/A')}")
            with d3:
                st.info(f"**Tipo:** {detalle.get(col_tip, 'N/A')}")
                
            st.write("**Nombre / Descripción:**")
            st.warning(detalle.get(col_req, 'Sin descripción'))
            
            # Mostrar cualquier otra columna extra que exista
            with st.expander("Ver todos los campos técnicos originales"):
                st.json(detalle.to_dict())

elif seccion == "🧩 Sección de Módulos":
    st.markdown("### Seguimiento Detallado por Módulos")
    
    lista_modulos = sorted(df_filt[col_mod].unique())
    modulo_seleccionado = st.selectbox("Selecciona un Módulo para auditar:", lista_modulos)
    
    if modulo_seleccionado:
        df_m = df_filt[df_filt[col_mod] == modulo_seleccionado]
        
        # Cálculos específicos del módulo
        m_est_str = df_m[col_est].astype(str).str.upper()
        m_comp = len(df_m[m_est_str.str.contains("360|CARGADO|COMPLETADO|TERMINADO|FINALIZADO|APROBADO", regex=True)])
        m_des = len(df_m[m_est_str.str.contains("DESESTIMADO|CANCELADO|RECHAZADO", regex=True)])
        m_pend = len(df_m) - m_comp - m_des
        m_base = len(df_m) - m_des
        m_avance = (m_comp / m_base * 100) if m_base > 0 else 0
        
        st.markdown(f"#### Estado del módulo: {modulo_seleccionado}")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Total Requerimientos", len(df_m))
        mc2.metric("Completados", m_comp)
        mc3.metric("Pendientes / En Proceso", m_pend)
        mc4.metric("Porcentaje de Avance", f"{m_avance:.1f}%")
        
        st.markdown("#### Desglose de Requerimientos")
        st.dataframe(df_m[[col_id, col_req, col_est, col_res, col_spr, col_fab]], use_container_width=True, hide_index=True)

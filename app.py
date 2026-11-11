import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN UX/UI Y ESTILOS ---
st.set_page_config(page_title="SHIIFT | Control Ejecutivo", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")

# Colores corporativos para consistencia gráfica
COLORS = ['#2E86C1', '#17A589', '#F39C12', '#8E44AD', '#D35400', '#273746']
DB_PATH = "shiift_master_db.csv"

# Ocultar menú default de Streamlit para aspecto profesional
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Estilo para las tarjetas métricas */
            div[data-testid="metric-container"] {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                padding: 5% 5% 5% 10%;
                border-radius: 5px;
                color: #273746;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. SISTEMA DE AUTENTICACIÓN Y ROLES ---
if 'rol' not in st.session_state:
    st.session_state.rol = None

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2855/2855364.png", width=60)
    st.markdown("### SHIIFT")
    st.caption("Control Ejecutivo de Requerimientos")
    st.markdown("---")
    
    if st.session_state.rol is None:
        st.markdown("**Acceso al Sistema**")
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Iniciar Sesión", use_container_width=True):
            if usuario == "admin" and password == "12345":
                st.session_state.rol = "Administrador"
                st.rerun()
            elif usuario == "visor" and password == "12345":
                st.session_state.rol = "Consulta"
                st.rerun()
            else:
                st.error("Credenciales inválidas")
        st.stop() # Detiene la app hasta que haya login
    
    else:
        st.success(f"Perfil: {st.session_state.rol}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.rol = None
            st.rerun()
            
        st.markdown("---")
        # Navegación principal del Módulo
        menu = st.radio("Navegación", [
            "📊 M1: Dashboard Ejecutivo", 
            "📈 M2: Gráficos de Análisis", 
            "📋 M3: Consulta de Requerimientos",
            "🧩 M4: Seguimiento por Módulos",
            "🏃 M5: Análisis de Sprints",
            "👥 M6: Responsables y Recursos",
            "🏭 M7: Fábricas de Desarrollo"
        ])
        
        st.markdown("---")
        # Función exclusiva de Administrador
        if st.session_state.rol == "Administrador":
            st.markdown("**⚙️ Administración**")
            archivo_subido = st.file_uploader("Actualizar Excel (SHIIFT)", type=["xlsb", "xlsx"])
            if st.button("ACTUALIZAR INFORMACIÓN", type="primary", use_container_width=True):
                if archivo_subido:
                    with st.spinner("Integrando y validando módulos..."):
                        try:
                            engine = "pyxlsb" if archivo_subido.name.endswith('.xlsb') else "openpyxl"
                            
                            # Lógica ETL: En lugar de leer el resumen, leer todas las hojas de detalle y consolidarlas
                            xl = pd.ExcelFile(archivo_subido, engine=engine)
                            hojas = xl.sheet_names
                            
                            # Excluir las hojas que son explícitamente resúmenes para evitar duplicados
                            hojas_detalle = [h for h in hojas if "RESUMEN" not in h.upper() and "PIVOT" not in h.upper()]
                            
                            df_master = pd.DataFrame()
                            for hoja in hojas_detalle:
                                df_temp = pd.read_excel(archivo_subido, sheet_name=hoja, engine=engine)
                                df_temp['Módulo_Origen'] = hoja # Trazabilidad
                                df_master = pd.concat([df_master, df_temp], ignore_index=True)
                            
                            # Limpieza estándar
                            df_master.columns = df_master.columns.astype(str).str.strip().str.upper()
                            df_master = df_master.fillna("Sin Asignar")
                            
                            # Guardar en base persistente local
                            df_master.to_csv(DB_PATH, index=False)
                            st.success(f"Base actualizada. {len(df_master)} registros válidos procesados.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error de integridad: {e}")
                else:
                    st.warning("Cargue un archivo antes de actualizar.")

# --- 3. EXTRACCIÓN Y FILTROS GLOBALES ---
if not os.path.exists(DB_PATH):
    st.info("Plataforma sin datos inicializados. El Administrador debe cargar el archivo base.")
    st.stop()

df = pd.read_csv(DB_PATH)

# Asegurar nombres de columnas clave basados en el prompt (adaptándose a variaciones del Excel)
def obtener_col(palabras_clave):
    for col in df.columns:
        if any(palabra in col for palabra in palabras_clave):
            return col
    return "Módulo_Origen" # Retorno de seguridad

col_id = obtener_col(["WRICEF", "ID"])
col_req = obtener_col(["NOMBRE", "REQUERIMIENTO", "DESCRIPCI"])
col_modulo = obtener_col(["MODULO", "MÓDULO"])
col_resp = obtener_col(["RESPONSABLE", "BP", "OWNER"])
col_estado = obtener_col(["ESTADO", "STATUS"])
col_sprint = obtener_col(["SPRINT"])
col_fabrica = obtener_col(["FABRICA", "FÁBRICA", "DESARROLLO"])
col_prioridad = obtener_col(["PRIORIDAD", "PRIORIZACION"])

# Filtros Dinámicos Superiores (Expander)
with st.expander("🔍 Filtros Interactivos Globales", expanded=False):
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1: sel_mod = st.multiselect("Módulo", sorted(df[col_modulo].unique()))
    with f2: sel_est = st.multiselect("Estado", sorted(df[col_estado].unique()))
    with f3: sel_res = st.multiselect("Responsable", sorted(df[col_resp].unique()))
    with f4: sel_spr = st.multiselect("Sprint", sorted(df[col_sprint].unique()))
    with f5: sel_fab = st.multiselect("Fábrica", sorted(df[col_fabrica].unique()))
    
    if st.button("Limpiar Filtros"):
        st.rerun()

# Aplicar filtros
df_filt = df.copy()
if sel_mod: df_filt = df_filt[df_filt[col_modulo].isin(sel_mod)]
if sel_est: df_filt = df_filt[df_filt[col_estado].isin(sel_est)]
if sel_res: df_filt = df_filt[df_filt[col_resp].isin(sel_res)]
if sel_spr: df_filt = df_filt[df_filt[col_sprint].isin(sel_spr)]
if sel_fab: df_filt = df_filt[df_filt[col_fabrica].isin(sel_fab)]


# --- 4. CONTROLADOR DE VISTAS (ENRUTAMIENTO) ---

if "M1" in menu:
    st.markdown("## Dashboard Ejecutivo")
    
    # KPIs solicitados
    total_req = len(df_filt)
    req_sin_iniciar = len(df_filt[df_filt[col_estado].astype(str).str.contains("Sin iniciar|Pendiente", case=False)])
    req_ent = len(df_filt[df_filt[col_estado].astype(str).str.contains("Entendimiento", case=False)])
    req_const = len(df_filt[df_filt[col_estado].astype(str).str.contains("Construcción|Desarrollo", case=False)])
    req_ref = len(df_filt[df_filt[col_estado].astype(str).str.contains("Refinamiento", case=False)])
    req_360 = len(df_filt[df_filt[col_estado].astype(str).str.contains("360|Cargado", case=False)])
    req_des = len(df_filt[df_filt[col_estado].astype(str).str.contains("Desestimado|Cancelado", case=False)])
    
    # Calcular % de avance teórico (Registros terminados/en 360 vs totales activos)
    avance = (req_360 / (total_req - req_des)) * 100 if (total_req - req_des) > 0 else 0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📌 GAPs Totales", f"{total_req}")
    k2.metric("🛑 Sin Iniciar", f"{req_sin_iniciar}", f"{(req_sin_iniciar/total_req*100):.1f}%" if total_req>0 else "0%", delta_color="inverse")
    k3.metric("🏗️ En Construcción", f"{req_const}")
    k4.metric("✅ Avance General", f"{avance:.1f}%")
    
    st.write("<br>", unsafe_allow_html=True)
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("🧠 Entendimiento", f"{req_ent}")
    k6.metric("⚖️ Refinamiento", f"{req_ref}")
    k7.metric("📦 Cargados 360", f"{req_360}")
    k8.metric("🚫 Desestimados", f"{req_des}")


elif "M2" in menu:
    st.markdown("## Análisis Gráfico de Requerimientos")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Gráfico 1: Distribución por Estado**")
        fig1 = px.pie(df_filt, names=col_estado, hole=0.5, color_discrete_sequence=COLORS)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
        
    with c2:
        st.write("**Gráfico 2: Requerimientos por Módulo**")
        df_mod = df_filt.groupby(col_modulo).size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=False)
        fig2 = px.bar(df_mod, x=col_modulo, y='Cantidad', color=col_modulo, color_discrete_sequence=COLORS)
        st.plotly_chart(fig2, use_container_width=True)
        
    c3, c4 = st.columns(2)
    with c3:
        st.write("**Gráfico 4: Distribución por Sprint**")
        df_spr = df_filt.groupby(col_sprint).size().reset_index(name='Cantidad')
        fig4 = px.bar(df_spr, x=col_sprint, y='Cantidad', color_discrete_sequence=['#17A589'])
        st.plotly_chart(fig4, use_container_width=True)
        
    with c4:
        st.write("**Gráfico 5: Carga por Responsable**")
        df_resp = df_filt.groupby(col_resp).size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=True)
        fig5 = px.bar(df_resp, x='Cantidad', y=col_resp, orientation='h', color_discrete_sequence=['#2E86C1'])
        st.plotly_chart(fig5, use_container_width=True)


elif "M3" in menu:
    st.markdown("## Base de Datos y Consulta")
    b1, b2 = st.columns([3, 1])
    with b1:
        busqueda = st.text_input("🔍 Buscar por ID o Nombre del requerimiento:")
    
    df_tabla = df_filt.copy()
    if busqueda:
        mask = df_tabla[col_req].astype(str).str.contains(busqueda, case=False) | df_tabla[col_id].astype(str).str.contains(busqueda, case=False)
        df_tabla = df_tabla[mask]
        
    st.caption(f"Mostrando {len(df_tabla)} registros válidos.")
    st.dataframe(df_tabla, use_container_width=True, height=600)
    
    # Exportar a Excel
    if st.session_state.rol in ["Administrador", "Consulta"]:
        st.download_button("📥 Exportar Tabla Filtrada", df_tabla.to_csv(index=False).encode('utf-8'), "shiift_export.csv", "text/csv")


elif "M4" in menu:
    st.markdown("## Seguimiento por Módulos")
    modulos = sorted(df_filt[col_modulo].unique())
    tabs = st.tabs([str(m)[:15] for m in modulos]) # Nombres cortos para las pestañas
    
    for i, mod in enumerate(modulos):
        with tabs[i]:
            df_m = df_filt[df_filt[col_modulo] == mod]
            st.subheader(f"Módulo: {mod}")
            
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Total Requerimientos", len(df_m))
            mc2.metric("Responsables Involucrados", df_m[col_resp].nunique())
            mc3.metric("Fábricas Involucradas", df_m[col_fabrica].nunique())
            
            st.markdown("#### Detalle Operativo")
            st.dataframe(df_m[[col_id, col_req, col_estado, col_resp, col_sprint]], use_container_width=True, hide_index=True)


elif "M5" in menu:
    st.markdown("## Tablero de Sprints")
    sprints = sorted(df_filt[col_sprint].unique())
    sel_sprint_detalle = st.selectbox("Seleccione el Sprint a analizar:", sprints)
    
    df_s = df_filt[df_filt[col_sprint] == sel_sprint_detalle]
    st.write(f"**Registros en el {sel_sprint_detalle}: {len(df_s)}**")
    
    fig_s = px.sunburst(df_s, path=[col_modulo, col_estado, col_resp], color_discrete_sequence=COLORS)
    st.plotly_chart(fig_s, use_container_width=True)
    st.dataframe(df_s[[col_req, col_modulo, col_estado, col_resp]], use_container_width=True)


elif "M6" in menu:
    st.markdown("## Análisis de Recursos y Responsables")
    sel_recurso = st.selectbox("Seleccionar BP / Owner:", sorted(df_filt[col_resp].unique()))
    df_r = df_filt[df_filt[col_resp] == sel_recurso]
    
    rc1, rc2 = st.columns(2)
    with rc1:
        st.write("Carga por Estado")
        st.plotly_chart(px.histogram(df_r, x=col_estado, color=col_estado), use_container_width=True)
    with rc2:
        st.write("Carga por Sprint")
        st.plotly_chart(px.histogram(df_r, x=col_sprint, color=col_modulo), use_container_width=True)


elif "M7" in menu:
    st.markdown("## Fábricas de Desarrollo")
    sel_fabrica = st.selectbox("Auditoría de Fábrica:", sorted(df_filt[col_fabrica].unique()))
    df_f = df_filt[df_filt[col_fabrica] == sel_fabrica]
    
    st.write(f"**Volumen Asignado a {sel_fabrica}: {len(df_f)} GAPs**")
    
    fc1, fc2 = st.columns([1, 2])
    with fc1:
        st.plotly_chart(px.pie(df_f, names=col_estado, title="Estatus de Entregas"), use_container_width=True)
    with fc2:
        st.dataframe(df_f[[col_id, col_req, col_modulo, col_sprint, col_estado]], use_container_width=True)

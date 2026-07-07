import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Riesgo Morosidad", layout="wide")

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Logo_de_la_Universidad_C%C3%A9sar_Vallejo.svg/512px-Logo_de_la_Universidad_C%C3%A9sar_Vallejo.svg.png", width=150)
st.sidebar.title("Configuración")
st.sidebar.markdown("**Autor / Código:** 7002869402")
st.sidebar.divider()

# Cargar el dataset generado
@st.cache_data
def cargar_datos():
    return pd.read_csv('dataset_personal.csv')

try:
    df_original = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo 'dataset_personal.csv'. Asegúrate de que esté en la misma carpeta.")
    st.stop()

# Filtros Generales
st.sidebar.subheader("Filtros Generales")
opciones_perfil = df_original['Perfil_Historico'].unique()
filtro_perfil = st.sidebar.multiselect("Selecciona Perfil Histórico:", options=opciones_perfil, default=opciones_perfil)

opciones_plazo = sorted(df_original['Plazo_Meses'].unique())
filtro_plazo = st.sidebar.multiselect("Selecciona Plazo (Meses):", options=opciones_plazo, default=opciones_plazo)

# Aplicar los filtros a los datos para los gráficos
df = df_original[(df_original['Perfil_Historico'].isin(filtro_perfil)) & (df_original['Plazo_Meses'].isin(filtro_plazo))]

# --- TÍTULO PRINCIPAL ---
st.title("📊 Dashboard Analítico: Riesgo de Morosidad Bancaria")
st.markdown("### Laboratorio 14: Inteligencia de Negocios y Big Data")
st.divider()

# --- NUEVA SECCIÓN: TABLA Y FILTRO POR ID (CÓDIGO DE ESTUDIANTE) ---
st.subheader("🔍 Búsqueda y Detalle de Clientes (ID Estudiante)")
st.write("Utiliza el buscador para filtrar la tabla por el ID único del cliente, el cual contiene tu código de estudiante.")

# Buscador de texto
busqueda_id = st.text_input("Ingresa el ID o código a buscar (Ej. 7002869402-0015):", "")

# Lógica de filtrado para la tabla
if busqueda_id:
    # Filtra si la columna ID_Cliente contiene el texto ingresado
    df_busqueda = df_original[df_original['ID_Cliente'].astype(str).str.contains(busqueda_id, case=False, na=False)]
    st.write(f"**Resultados encontrados:** {len(df_busqueda)}")
    st.dataframe(df_busqueda, use_container_width=True)
else:
    st.write("**Mostrando los primeros 5 registros de la base de datos:**")
    st.dataframe(df_original.head(), use_container_width=True)

st.divider()

# --- VISUALIZACIÓN 1: Indicador KPI ---
st.subheader("1. Indicadores Clave de Rendimiento (KPIs)")
col1, col2, col3 = st.columns(3)

total_clientes = len(df)
if total_clientes > 0:
    tasa_morosidad = (df['Morosidad'].sum() / total_clientes) * 100
    promedio_credito = df['Monto_Credito'].mean()
else:
    tasa_morosidad = 0
    promedio_credito = 0

with col1:
    st.metric(label="Total de Clientes (Gráficos)", value=f"{total_clientes:,}")
with col2:
    st.metric(label="Tasa de Morosidad Global", value=f"{tasa_morosidad:.2f}%")
with col3:
    st.metric(label="Monto de Crédito Promedio", value=f"S/ {promedio_credito:,.2f}")

st.divider()

# --- VISUALIZACIONES 2 y 3 ---
if total_clientes > 0:
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("2. Morosidad por Perfil Histórico")
        df_perfil = df.groupby(['Perfil_Historico', 'Morosidad']).size().reset_index(name='Cantidad')
        df_perfil['Estado'] = df_perfil['Morosidad'].map({0: 'Al Día', 1: 'En Mora'})
        
        fig_barras = px.bar(df_perfil, x='Perfil_Historico', y='Cantidad', color='Estado',
                            barmode='group', color_discrete_sequence=['#28a745', '#dc3545'])
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_graf2:
        st.subheader("3. Distribución del Endeudamiento")
        df['Estado_Mora'] = df['Morosidad'].map({0: 'Al Día', 1: 'En Mora'})
        
        fig_box = px.box(df, x='Estado_Mora', y='Ratio_Deuda_Ingreso', color='Estado_Mora',
                         color_discrete_sequence=['#28a745', '#dc3545'],
                         title="Ratio Deuda/Ingreso vs Estado de Mora")
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # --- VISUALIZACIÓN 4 ---
    st.subheader("4. Relación Ingreso vs Monto de Crédito")
    fig_scatter = px.scatter(df, x='Ingreso_Mensual', y='Monto_Credito', color='Estado_Mora',
                             opacity=0.6, color_discrete_sequence=['#28a745', '#dc3545'],
                             hover_data=['Edad', 'Plazo_Meses'])
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# --- STORYTELLING DE DATOS ---
st.subheader("💡 Conclusiones y Decisiones Estratégicas")

col_hallazgos, col_recom = st.columns(2)

with col_hallazgos:
    st.markdown("#### Hallazgos Principales")
    st.info("""
    1. **Impacto del Historial:** Existe una correlación directa y crítica entre tener más de 1 atraso previo (Perfil Riesgoso) y caer en morosidad.
    2. **Umbral de Endeudamiento:** Los clientes que comprometen una alta proporción de su ingreso mensual en la cuota (Ratio Deuda/Ingreso alto) presentan mayor variabilidad y concentración de impagos.
    3. **Distribución del Crédito:** Los créditos de mayor monto no son necesariamente los más morosos, siempre que estén respaldados por un nivel de ingreso proporcional al solicitante.
    """)

with col_recom:
    st.markdown("#### Recomendaciones")
    st.success("""
    1. **Ajuste de Políticas:** Implementar un límite estricto en la aprobación de créditos para solicitantes cuyo Ratio Deuda/Ingreso supere el umbral crítico identificado.
    2. **Filtro Preventivo:** Denegar automáticamente o solicitar garantías adicionales a aquellos prospectos clasificados en el perfil histórico "Riesgoso".
    3. **Estrategia de Tasas:** Ofrecer tasas de interés preferenciales a los clientes con probabilidad nula de mora, asegurando una cartera de clientes sana.
    """)

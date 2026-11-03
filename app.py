import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración general
st.set_page_config(
    page_title="Comercial Maule SpA | Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual corporativo
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f4f8fc 0%, #ffffff 38%);
    }
    [data-testid="stHeader"] {
        background: rgba(255,255,255,0.75);
    }
    [data-testid="stSidebar"] {
        background: #102a43;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #102a43 !important;
    }
    .main-title {
        background: linear-gradient(90deg, #102a43, #176b87);
        padding: 26px 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 8px;
        box-shadow: 0 8px 24px rgba(16,42,67,0.12);
    }
    .main-title h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    .main-title p {
        color: #d9edf7;
        margin: 6px 0 0 0;
        font-size: 1rem;
    }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e1eaf2;
        padding: 18px 20px;
        border-radius: 15px;
        box-shadow: 0 4px 16px rgba(16,42,67,0.06);
    }
    [data-testid="stMetricLabel"] {
        color: #526779;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: #102a43;
    }
    h2, h3 {
        color: #102a43;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #e1eaf2;
        border-radius: 12px;
        overflow: hidden;
    }
    .section-note {
        color: #627d98;
        font-size: 0.92rem;
        margin-top: -8px;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("""
<div class="main-title">
    <h1>📊 Comercial Maule SpA</h1>
    <p>Panel de control · Análisis y seguimiento de ventas</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# Carga de datos
@st.cache_data
def cargar_datos():
    return pd.read_excel("ventas_comercial_maule.xlsx")

try:
    datos = cargar_datos()
except Exception:
    st.error("No se pudo cargar ventas_comercial_maule.xlsx. Comprueba que esté en la carpeta principal del repositorio.")
    st.stop()

datos["Fecha"] = pd.to_datetime(datos["Fecha"], errors="coerce")
datos["Total Venta"] = pd.to_numeric(datos["Total Venta"], errors="coerce").fillna(0)
datos = datos.dropna(subset=["Fecha"])

if datos.empty:
    st.warning("El archivo no contiene registros de ventas válidos.")
    st.stop()

# Filtros laterales
st.sidebar.markdown("## ⚙️ Filtros")
st.sidebar.caption("Personaliza los datos que deseas analizar.")
regiones = sorted(datos["Región"].dropna().astype(str).unique())
regiones_sel = st.sidebar.multiselect("📍 Región", regiones, default=regiones)
fecha_min = datos["Fecha"].min().date()
fecha_max = datos["Fecha"].max().date()
rango = st.sidebar.date_input(
    "📅 Período de análisis",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)
st.sidebar.markdown("---")
st.sidebar.caption("Comercial Maule SpA · Dashboard de ventas")

# Aplicación de filtros
filtrados = datos[datos["Región"].astype(str).isin(regiones_sel)]
if isinstance(rango, (tuple, list)) and len(rango) == 2:
    inicio, fin = rango
    filtrados = filtrados[
        (filtrados["Fecha"].dt.date >= inicio) &
        (filtrados["Fecha"].dt.date <= fin)
    ]

if filtrados.empty:
    st.warning("No hay ventas para los filtros seleccionados. Prueba con otra región o período.")
    st.stop()

def pesos(valor):
    return "$" + f"{valor:,.0f}".replace(",", ".")

# Indicadores principales
st.subheader("Resumen de resultados")
st.markdown('<p class="section-note">Indicadores calculados según los filtros seleccionados.</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("💰 Ventas totales", pesos(filtrados["Total Venta"].sum()))
c2.metric("🧾 Número de ventas", f"{len(filtrados):,}".replace(",", "."))
c3.metric("📈 Promedio por venta", pesos(filtrados["Total Venta"].mean()))

# Paleta corporativa para gráficos
azul = ["#102A43", "#176B87", "#2A9D8F", "#57A0D3", "#8CC6D7", "#B8DDE5"]
tema = "plotly_white"

# Gráficos por categoría y región
st.write("")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ventas por producto")
    producto = (
        filtrados.groupby("Producto", as_index=False)["Total Venta"]
        .sum()
        .sort_values("Total Venta", ascending=False)
    )
    fig_producto = px.bar(
        producto,
        x="Producto",
        y="Total Venta",
        color="Producto",
        color_discrete_sequence=azul,
        labels={"Total Venta": "Ventas ($)", "Producto": "Producto"},
        template=tema
    )
    fig_producto.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    fig_producto.update_traces(marker_line_width=0, hovertemplate="%{x}<br>Ventas: $%{y:,.0f}<extra></extra>")
    st.plotly_chart(fig_producto, use_container_width=True)

with col2:
    st.subheader("Distribución por región")
    region = filtrados.groupby("Región", as_index=False)["Total Venta"].sum()
    fig_region = px.pie(
        region,
        names="Región",
        values="Total Venta",
        hole=0.58,
        color_discrete_sequence=azul,
        template=tema
    )
    fig_region.update_layout(
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Región"
    )
    fig_region.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>Ventas: $%{value:,.0f}<extra></extra>")
    st.plotly_chart(fig_region, use_container_width=True)

# Evolución temporal
st.write("")
st.subheader("Evolución de ventas")
st.markdown('<p class="section-note">Comportamiento de las ventas durante el período seleccionado.</p>', unsafe_allow_html=True)

por_fecha = (
    filtrados.assign(Día=filtrados["Fecha"].dt.date)
    .groupby("Día", as_index=False)["Total Venta"]
    .sum()
)
fig_fecha = px.line(
    por_fecha,
    x="Día",
    y="Total Venta",
    markers=True,
    labels={"Día": "Fecha", "Total Venta": "Ventas ($)"},
    template=tema
)
fig_fecha.update_traces(
    line=dict(color="#176B87", width=3),
    marker=dict(size=7, color="#2A9D8F"),
    hovertemplate="%{x}<br>Ventas: $%{y:,.0f}<extra></extra>"
)
fig_fecha.update_layout(
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig_fecha, use_container_width=True)

# Tabla y descarga
st.write("")
st.subheader("Detalle de ventas")
st.markdown('<p class="section-note">Registros incluidos en el análisis.</p>', unsafe_allow_html=True)
st.dataframe(
    filtrados.sort_values("Fecha", ascending=False),
    use_container_width=True,
    hide_index=True
)

csv = filtrados.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Descargar datos filtrados (CSV)",
    csv,
    "ventas_filtradas.csv",
    "text/csv",
    use_container_width=False
)

st.markdown("---")
st.caption("Comercial Maule SpA · Dashboard desarrollado en Python con Streamlit y Plotly.")

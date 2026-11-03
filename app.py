import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Comercial Maule SpA", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Ventas")
st.subheader("Comercial Maule SpA")
st.caption("Panel interactivo para explorar las ventas de la empresa.")

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

st.sidebar.header("Filtros")
regiones = sorted(datos["Región"].dropna().astype(str).unique())
regiones_sel = st.sidebar.multiselect("Región", regiones, default=regiones)
fecha_min, fecha_max = datos["Fecha"].min().date(), datos["Fecha"].max().date()
rango = st.sidebar.date_input("Período", value=(fecha_min, fecha_max), min_value=fecha_min, max_value=fecha_max)

filtrados = datos[datos["Región"].astype(str).isin(regiones_sel)]
if isinstance(rango, (tuple, list)) and len(rango) == 2:
    inicio, fin = rango
    filtrados = filtrados[(filtrados["Fecha"].dt.date >= inicio) & (filtrados["Fecha"].dt.date <= fin)]

if filtrados.empty:
    st.warning("No hay ventas para los filtros seleccionados.")
    st.stop()

def pesos(valor):
    return "$" + f"{valor:,.0f}".replace(",", ".")

c1, c2, c3 = st.columns(3)
c1.metric("Ventas totales", pesos(filtrados["Total Venta"].sum()))
c2.metric("Número de ventas", f"{len(filtrados):,}".replace(",", "."))
c3.metric("Promedio por venta", pesos(filtrados["Total Venta"].mean()))

col1, col2 = st.columns(2)
with col1:
    st.subheader("Ventas por producto")
    producto = filtrados.groupby("Producto", as_index=False)["Total Venta"].sum().sort_values("Total Venta", ascending=False)
    st.plotly_chart(px.bar(producto, x="Producto", y="Total Venta", labels={"Total Venta": "Ventas ($)"}), use_container_width=True)
with col2:
    st.subheader("Ventas por región")
    region = filtrados.groupby("Región", as_index=False)["Total Venta"].sum()
    st.plotly_chart(px.pie(region, names="Región", values="Total Venta", hole=0.35), use_container_width=True)

st.subheader("Evolución de ventas")
por_fecha = filtrados.assign(Día=filtrados["Fecha"].dt.date).groupby("Día", as_index=False)["Total Venta"].sum()
st.plotly_chart(px.line(por_fecha, x="Día", y="Total Venta", markers=True, labels={"Día": "Fecha", "Total Venta": "Ventas ($)"}), use_container_width=True)

st.subheader("Detalle de ventas")
st.dataframe(filtrados.sort_values("Fecha", ascending=False), use_container_width=True)
st.download_button("Descargar datos filtrados en CSV", filtrados.to_csv(index=False).encode("utf-8-sig"), "ventas_filtradas.csv", "text/csv")

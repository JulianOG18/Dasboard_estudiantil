import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración básica de la página en Streamlit
st.set_page_config(
    page_title="Dashboard Estudiantil",  # Título del navegador
    page_icon="📊"                       # Ícono de la pestaña
)

# =============================================
# ✅ FUNCIÓN PARA CARGAR Y LIMPIAR LOS DATOS
# =============================================
@st.cache_data
def load_data():
    # Cargar el archivo Excel
    df = pd.read_excel("ListadoDeEstudiantesGrupo_050.xlsx")

    # Eliminar filas incompletas
    df = df.dropna()

    # Normalización de texto en columnas categóricas
    df["Barrio_Residencia"] = df["Barrio_Residencia"].str.lower().str.strip().str.title()
    df["Color_Cabello"] = df["Color_Cabello"].str.lower().str.strip().str.title()
    df["RH"] = df["RH"].str.upper()

    # Conversión de fecha y cálculo de edad
    df["Fecha_Nacimiento"] = pd.to_datetime(df["Fecha_Nacimiento"], errors='coerce')
    hoy = pd.Timestamp.today()
    df["Edad"] = (hoy - df["Fecha_Nacimiento"]).dt.days // 365

    # Conversión de estatura a cm y metros
    df["Estatura_cm"] = df["Estatura"] * 100
    df["Estatura_m"] = df["Estatura"] / 100

    # Calcular Índice de Masa Corporal
    df["IMC"] = df["Peso"] / (df["Estatura_m"] ** 2)

    # Identificar integrantes del grupo mediante código
    COLUMNA_CODIGO = "Código"
    codigos_grupo = [
        "202310254018",
        "202410029018",
        "202410166018",
        "202320065018"
    ]

    df[COLUMNA_CODIGO] = df[COLUMNA_CODIGO].astype(str).str.strip()
    df["Integrante_Grupo"] = df[COLUMNA_CODIGO].isin(codigos_grupo)

    # Clasificación del IMC según estándares médicos
    def clasificacion(imc):
        if imc < 18.5: return "Bajo Peso"
        elif imc < 25: return "Normal"
        elif imc < 30: return "Sobrepeso"
        else: return "Obesidad"

    df["Clasificación_IMC"] = df["IMC"].apply(clasificacion)

    return df

# Cargar datos
df = load_data()

# Título principal del dashboard
st.title("Dashboard Estudiantil – Grupo 050")

# Mostrar tabla original
st.subheader("Datos del Archivo Excel")
st.dataframe(df)

# =============================================
# ✅ FILTROS MULTISELECT
# =============================================
st.subheader("Filtros")

col1, col2, col3 = st.columns(3)

# Filtros categóricos
f_rh = col1.multiselect("Tipo de Sangre (RH)", df["RH"].unique())
f_cabello = col2.multiselect("Color de Cabello", df["Color_Cabello"].unique())
f_barrio = col3.multiselect("Barrio de Residencia", df["Barrio_Residencia"].unique())

# Copiamos el dataframe para aplicar filtros
df_filtro = df.copy()

# Aplicar filtros seleccionados
if f_rh:
    df_filtro = df_filtro[df_filtro["RH"].isin(f_rh)]
if f_cabello:
    df_filtro = df_filtro[df_filtro["Color_Cabello"].isin(f_cabello)]
if f_barrio:
    df_filtro = df_filtro[df_filtro["Barrio_Residencia"].isin(f_barrio)]

# Checkbox para mostrar solo estudiantes del grupo
solo_grupo = st.checkbox("Integrantes de nuestro grupo")

if solo_grupo:
    df_filtro = df_filtro[df_filtro["Integrante_Grupo"] == True]

# Mostrar resultados filtrados
st.subheader("Datos filtrados")
st.dataframe(df_filtro)


# ✅ SLIDERS DE RANGO (Edad y Estatura)

st.subheader("Filtros de Rango")

# Si la tabla queda vacía, se detiene el programa
if df_filtro.empty:
    st.warning("No existen estudiantes después de aplicar los filtros.")
    st.stop()

# ---- EDAD ----
if df_filtro["Edad"].dropna().empty:
    st.warning("No hay edades válidas con los filtros aplicados.")
    edad_min, edad_max = 0, 1
else:
    edad_min = int(df_filtro["Edad"].dropna().min())
    edad_max = int(df_filtro["Edad"].dropna().max())

if edad_min == edad_max:
    rango_edad = (edad_min, edad_max)
    st.info(f"Todos los estudiantes tienen {edad_min} años.")
else:
    rango_edad = st.slider("Rango de Edad", edad_min, edad_max, (edad_min, edad_max))

# ---- ESTATURA ----
if df_filtro["Estatura_cm"].dropna().empty:
    st.warning("No hay estaturas válidas con los filtros aplicados.")
    est_min, est_max = 0, 1
else:
    est_min = int(df_filtro["Estatura_cm"].dropna().min())
    est_max = int(df_filtro["Estatura_cm"].dropna().max())

if est_min == est_max:
    rango_est = (est_min, est_max)
    st.info(f"Todos los estudiantes tienen {est_min} cm de estatura.")
else:
    rango_est = st.slider("Rango de Estatura (cm)", est_min, est_max, (est_min, est_max))

# Aplicar filtros de rango
df_filtro = df_filtro[(df_filtro["Edad"] >= rango_edad[0]) & (df_filtro["Edad"] <= rango_edad[1])]
df_filtro = df_filtro[(df_filtro["Estatura_cm"] >= rango_est[0]) & (df_filtro["Estatura_cm"] <= rango_est[1])]


# MÉTRICAS GENERALES

st.subheader("Resumen General")
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Estudiantes", df_filtro.shape[0])
c2.metric("Edad Promedio", round(df_filtro["Edad"].mean(), 2))
c3.metric("Estatura Promedio (cm)", round(df_filtro["Estatura_cm"].mean(), 2))
c4.metric("Peso Promedio (kg)", round(df_filtro["Peso"].mean(), 2))
c5.metric("IMC Promedio", round(df_filtro["IMC"].mean(), 2))

#GRÁFICOS ESTADÍSTICOS

st.subheader("Distribuciones Gráficas")

# 1. Histograma de edades
fig1, ax1 = plt.subplots()
ax1.hist(df_filtro["Edad"])
ax1.set_title("Distribución de Edades")
st.pyplot(fig1)

# 2. Pie chart de tipo de sangre
fig2, ax2 = plt.subplots()
df_filtro["RH"].value_counts().plot.pie(autopct="%1.1f%%", ax=ax2)
ax2.set_title("Distribución Tipo de Sangre")
st.pyplot(fig2)

# 3. Dispersión Estatura vs Peso
fig3, ax3 = plt.subplots()
ax3.scatter(df_filtro["Estatura_cm"], df_filtro["Peso"])
ax3.set_xlabel("Estatura (cm)")
ax3.set_ylabel("Peso (kg)")
ax3.set_title("Estatura vs Peso")
st.pyplot(fig3)

# 4. Barras por color de cabello
fig4, ax4 = plt.subplots()
df_filtro["Color_Cabello"].value_counts().plot.bar(ax=ax4)
ax4.set_title("Distribución por Color de Cabello")
st.pyplot(fig4)

# 5. Línea de tallas de zapatos
fig5, ax5 = plt.subplots()
df_filtro["Talla_Zapato"].value_counts().sort_index().plot(ax=ax5)
ax5.set_title("Distribución Tallas de Zapato")
st.pyplot(fig5)

# 6. Top 10 Barrios
fig6, ax6 = plt.subplots()
df_filtro["Barrio_Residencia"].value_counts().head(10).plot.bar(ax=ax6)
ax6.set_title("Top 10 Barrios de Residencia")
st.pyplot(fig6)


# TOP 5

top_est = df.nlargest(5, "Estatura_cm")
top_peso = df.nlargest(5, "Peso")

top_est.to_excel("Top5_Estatura.xlsx", index=False)
top_peso.to_excel("Top5_Peso.xlsx", index=False)

st.success("✅ Archivos generados: Top5_Estatura.xlsx y Top5_Peso.xlsx")


#  TABLA RESUMEN ESTADÍSTICO

st.subheader("Resumen Estadístico (Estatura, Peso, IMC)")
cA, cB, cC = st.columns(3)

cA.write(df_filtro["Estatura_cm"].describe())
cB.write(df_filtro["Peso"].describe())
cC.write(df_filtro["IMC"].describe())

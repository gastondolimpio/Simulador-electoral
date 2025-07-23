# SIMULADOR ELECTORAL GENERAL ALVARADO - STREAMLIT VERSION

import streamlit as st
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import tempfile
import os

# ================= FUNCIONES ===================
def calcular_distribucion_bancas(votos_partidos, blancos_nulos, total_bancas, piso_porcentual, es_consejeros=False):
    votos_afirmativos = sum(votos_partidos.values())
    if votos_afirmativos == 0:
        return {"bancas": {p: 0 for p in votos_partidos}, "detalle": {}}

    piso_electoral = (piso_porcentual / 100) * votos_afirmativos
    cociente = votos_afirmativos / total_bancas
    bancas = {p: int(v // cociente) for p, v in votos_partidos.items()}
    restos = {p: v % cociente for p, v in votos_partidos.items()}
    bancas_restantes = total_bancas - sum(bancas.values())

    partidos_validos = [p for p in votos_partidos if votos_partidos[p] >= piso_electoral]
    partidos_ordenados = sorted(partidos_validos, key=lambda p: (-restos[p], -votos_partidos[p]))

    for i in range(bancas_restantes):
        if i < len(partidos_ordenados):
            bancas[partidos_ordenados[i]] += 1

    return {"bancas": bancas, "detalle": {"piso": piso_electoral, "cociente": cociente}}

# ================= UI STREAMLIT ===================
st.set_page_config(page_title="Simulador Electoral", layout="centered")
st.title("🗳️ Simulador Electoral - General Alvarado 2025")
st.caption("Distribución de bancas por método Hare")

partidos = ["Fuerza Patria", "LLA", "UCR", "Es Ahora", "Potencia BA - Accion Alvarado", "FIT", "URGA"]
electores_totales = 40134

participacion_porcentual = st.slider("Participación estimada (%)", 10.0, 100.0, 70.0)
votos_totales = int(electores_totales * participacion_porcentual / 100)
blancos_nulos = st.number_input("Votos blancos/nulos", min_value=0, max_value=votos_totales, value=1000, step=100)
votos_disponibles = votos_totales - blancos_nulos

st.markdown(f"**Electores totales:** {electores_totales:,}  ")
st.markdown(f"**Votos totales:** {votos_totales:,}  ")
st.markdown(f"**Votos afirmativos disponibles:** {votos_disponibles:,}  ")

votos_partidos = {}
suma = 0
for partido in partidos:
    votos = st.number_input(f"{partido}", min_value=0, max_value=votos_disponibles - suma, step=100, key=partido)
    votos_partidos[partido] = votos
    suma += votos
    if suma >= votos_disponibles:
        break

if st.button("Calcular distribución de bancas"):
    resultado_concejales = calcular_distribucion_bancas(votos_partidos, blancos_nulos, 8, 12.5)
    resultado_consejeros = calcular_distribucion_bancas(votos_partidos, blancos_nulos, 3, 33.3, es_consejeros=True)

    st.subheader("📊 Resultados")

    st.markdown("**Distribución de Concejales (8 bancas)**")
    st.write(resultado_concejales["bancas"])

    st.markdown("**Distribución de Consejeros Escolares (3 bancas)**")
    st.write(resultado_consejeros["bancas"])

    fig1, ax1 = plt.subplots()
    partidos_v = list(votos_partidos.keys())
    votos_v = list(votos_partidos.values())
    ax1.pie(votos_v, labels=partidos_v, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    st.success("Cálculo realizado correctamente.")

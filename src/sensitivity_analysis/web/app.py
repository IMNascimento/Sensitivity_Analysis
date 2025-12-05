from __future__ import annotations

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from sensitivity_analysis.utils.calculadora import CalculadoraBasica, GeradorSinal


def main() -> None:
    st.set_page_config(page_title="Lab de Cálculos", layout="wide")

    st.title("🔢 Laboratório de Cálculos com Streamlit")
    st.write("Interface conectada às classes de cálculo em `src/core`.")

    calc = CalculadoraBasica()
    gerador = GeradorSinal()

    st.sidebar.header("Menu")
    pagina = st.sidebar.radio(
        "Escolha a funcionalidade:",
        ["Cálculos básicos", "Sinal senoidal (NumPy + Matplotlib)"],
    )

    if pagina == "Cálculos básicos":
        pagina_calculos_basicos(calc)
    elif pagina == "Sinal senoidal (NumPy + Matplotlib)":
        pagina_sinal_senoidal(gerador)


def pagina_calculos_basicos(calc: CalculadoraBasica) -> None:
    st.subheader("🧮 Cálculos básicos")

    col1, col2 = st.columns(2)

    with col1:
        a = st.number_input("Valor A", value=1.0)
        b = st.number_input("Valor B", value=2.0)

    operacao = st.selectbox("Operação", ["soma", "subtração"])

    if st.button("Calcular"):
        if operacao == "soma":
            resultado = calc.soma(a, b)
        else:
            resultado = calc.subtrai(a, b)

        st.success(f"Resultado ({operacao}): **{resultado}**")


def pagina_sinal_senoidal(gerador: GeradorSinal) -> None:
    st.subheader("📈 Sinal senoidal (NumPy + Matplotlib)")

    tamanho = st.slider("Tamanho do sinal", min_value=50, max_value=2000, value=500, step=50)

    x, y = gerador.seno(tamanho)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Sinal Senoidal")
    ax.set_xlabel("x")
    ax.set_ylabel("sin(x)")

    st.pyplot(fig)

    st.write("Primeiros 10 valores do sinal:")
    st.write(y[:10])


if __name__ == "__main__":
    main()

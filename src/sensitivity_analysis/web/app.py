from __future__ import annotations

from typing import cast

import matplotlib.pyplot as plt
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from sensitivity_analysis.utils.calculadora import (
    DistribuicaoTipo,
    MetodoConfiabilidade,
    RandomVariableConfig,
    ReliabilityConfig,
    SoilReliabilityCalculator,
)
from sensitivity_analysis.interface.soil import SoilInput


def main() -> None:
    """Ponto de entrada do aplicativo Streamlit."""
    st.set_page_config(page_title="Lab de Cálculos", layout="wide")

    st.title(" Confiabilidade na Geotecnia ")
    st.write(
        (
            "Preencha os parâmetros do solo, escolha as variáveis aleatórias e o método "
            "de confiabilidade (FORM/FOSM). Opcionalmente, gere o gráfico tensão × "
            "deformação."
        ),
    )

    pagina_solo_reliability()
    add_footer()


def add_footer() -> None:
    """Adiciona um rodapé fixo ao final da página."""
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            color: #888888;
            font-size: 0.8rem;
            padding: 0.5rem 0;
        }
        </style>
        <div class="footer">
            Powered by <strong>SophiaLabs</strong> lied by <strong>Bruna Martins</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===================== PÁGINA SOLO / CONFIABILIDADE ===================== #


def pagina_solo_reliability() -> None:
    """Constroi a página principal de entrada de dados e execução da análise."""
    st.header("Parâmetros do problema")

    # --- Condições do solo ---
    st.subheader("Condições do Solo")
    col1, col2, col3 = st.columns(3)

    with col1:
        gama: float = st.number_input(
            "γ – peso específico (kN/m³)",
            value=18.0,
            format="%.4f",
        )
    with col2:
        e0: float = st.number_input(
            "e₀ – índice de vazios inicial",
            value=0.8,
            format="%.4f",
        )
    with col3:
        sigma0_eff: float = st.number_input(
            "σ₀' – tensão vertical efetiva inicial (kPa)",
            value=100.0,
            format="%.4f",
        )

    # --- Parâmetros de rigidez ---
    st.subheader("Parâmetros de rigidez")
    colr1, colr2, colr3 = st.columns(3)

    with colr1:
        E50_ref: float = st.number_input(
            "E50_ref — módulo secante (kPa)",
            value=30_000.0,
            format="%.2f",
        )
        Eoed_ref: float = st.number_input(
            "Eoed_ref — módulo edométrico (kPa)",
            value=25_000.0,
            format="%.2f",
        )
        Eur_ref: float = st.number_input(
            "Eur_ref — módulo recarregamento (kPa)",
            value=90_000.0,
            format="%.2f",
        )

    with colr2:
        m: float = st.number_input(
            "m — expoente da dependência com a tensão",
            value=0.7,
            format="%.4f",
        )
        p_ref: float = st.number_input(
            "p_ref — tensão de referência (kPa)",
            value=100.0,
            format="%.2f",
        )
        nu: float = st.number_input(
            "ν — coeficiente de Poisson",
            value=0.3,
            format="%.4f",
        )

    with colr3:
        st.info(
            (
                "Aqui você pode ajustar os módulos e parâmetros de rigidez "
                "típicos de um modelo tipo Hardening Soil."
            ),
            icon="ℹ️",
        )

    # --- Parâmetros de resistência ---
    st.subheader("Parâmetros de resistência")
    colres1, colres2, colres3 = st.columns(3)

    with colres1:
        phi: float = st.number_input(
            "φ' – ângulo de atrito efetivo (°)",
            value=30.0,
            format="%.2f",
        )
    with colres2:
        c: float = st.number_input(
            "c' – coesão efetiva (kPa)",
            value=5.0,
            format="%.2f",
        )
    with colres3:
        psi: float = st.number_input(
            "ψ – dilatância (°)",
            value=0.0,
            format="%.2f",
        )

    # --- Parâmetros de endurecimento ---
    st.subheader("Parâmetros de endurecimento")
    cole1, cole2 = st.columns(2)

    with cole1:
        h0: float = st.number_input(
            "h₀ – parâmetro hardening",
            value=1.0,
            format="%.4f",
        )
    with cole2:
        alfa_h: float = st.number_input(
            "α_h – taxa de endurecimento",
            value=0.5,
            format="%.4f",
        )

    # --- Carregamento ---
    st.subheader("Carregamento atual")
    sigma_aplicado: float = st.number_input(
        "σ_aplicado – tensão vertical aplicada (kPa)",
        value=150.0,
        format="%.2f",
    )

    # --- Função limite / ε limite ---
    st.subheader("Função limite (opcional)")
    colg1, colg2 = st.columns([2, 1])

    with colg1:
        g_func_text: str = st.text_area(
            (
                "Função de equilíbrio limite g(x) "
                "(opcional, por enquanto só texto para documentação)"
            ),
            placeholder="Ex: g(x) = ε_limite - ε(z) ...",
        )

    with colg2:
        epsilon_limite: float = st.number_input(
            "ε_limite – deformação máxima admissível",
            min_value=0.0,
            value=0.02,
            format="%.5f",
        )

    st.markdown("---")

    # ===================== VARIÁVEIS ALEATÓRIAS ===================== #

    st.subheader("Variáveis aleatórias (opcional)")

    st.caption(
        (
            "Somente os seguintes parâmetros podem ser marcados como variáveis aleatórias:\n"
            "E50_ref, Eoed_ref, m, φ', e0, h0, α_h."
        ),
    )

    distrib_opcoes: list[DistribuicaoTipo] = [
        "Normal",
        "Lognormal",
        "Gumbel",
        "Uniforme",
    ]

    random_vars_cfg: dict[str, RandomVariableConfig] = {}

    with st.expander("Configurar variáveis aleatórias"):
        rv_cols = st.columns(3)

        def _bloco_rv(
            label_mostrado: str,
            nome_interno: str,
            col: DeltaGenerator,
        ) -> None:
            with col:
                usar: bool = bool(
                    st.checkbox(
                        label_mostrado,
                        key=f"chk_{nome_interno}",
                    ),
                )
                if not usar:
                    return

                distrib_escolhida: DistribuicaoTipo = cast(
                    DistribuicaoTipo,
                    st.selectbox(
                        f"Distribuição - {label_mostrado}",
                        distrib_opcoes,
                        key=f"dist_{nome_interno}",
                    ),
                )
                media: float = st.number_input(
                    f"Média - {label_mostrado}",
                    value=0.0,
                    format="%.6f",
                    key=f"mean_{nome_interno}",
                )
                desvio: float = st.number_input(
                    f"Desvio-padrão - {label_mostrado}",
                    value=0.0,
                    format="%.6f",
                    key=f"std_{nome_interno}",
                )
                correlacao: float = st.number_input(
                    f"Correlação (opcional) - {label_mostrado}",
                    value=0.0,
                    format="%.6f",
                    key=f"corr_{nome_interno}",
                )

                random_vars_cfg[nome_interno] = RandomVariableConfig(
                    distrib=distrib_escolhida,
                    media=media,
                    desvio=desvio,
                    correlacao=correlacao,
                )

        # Linha 1
        _bloco_rv("E50_ref", "E50_ref", rv_cols[0])
        _bloco_rv("Eoed_ref", "Eoed_ref", rv_cols[1])
        _bloco_rv("m", "m", rv_cols[2])

        # Linha 2
        rv_cols2 = st.columns(3)
        _bloco_rv("φ' (phi')", "phi", rv_cols2[0])
        _bloco_rv("e0", "e0", rv_cols2[1])
        _bloco_rv("h0", "h0", rv_cols2[2])

        # Linha 3
        rv_cols3 = st.columns(3)
        _bloco_rv("α_h", "alfa_h", rv_cols3[0])

    st.markdown("---")

    # ===================== MÉTODO + GRÁFICO ===================== #

    colmet1, colmet2 = st.columns([1, 1])
    with colmet1:
        metodo: MetodoConfiabilidade = cast(
            MetodoConfiabilidade,
            st.radio(
                "Método de confiabilidade",
                options=["FORM", "FOSM"],
                horizontal=True,
            ),
        )

    with colmet2:
        gerar_grafico: bool = bool(
            st.checkbox(
                "Gerar gráfico tensão × deformação",
                value=True,
            ),
        )

    # Botão de cálculo
    if st.button("Executar análise de confiabilidade", type="primary"):
        # Montar objetos de entrada
        soil_input = SoilInput(
            gama=gama,
            e0=e0,
            sigma0_eff=sigma0_eff,
            E50_ref=E50_ref,
            Eoed_ref=Eoed_ref,
            Eur_ref=Eur_ref,
            m=m,
            p_ref=p_ref,
            nu=nu,
            phi=phi,
            c=c,
            psi=psi,
            h0=h0,
            alfa_h=alfa_h,
            sigma_aplicado=sigma_aplicado,
            g_func_text=g_func_text.strip() or None,
            epsilon_limite=epsilon_limite,
        )

        rel_cfg = ReliabilityConfig(
            metodo=metodo,
            random_vars=random_vars_cfg,
        )

        calc = SoilReliabilityCalculator()
        resultado = calc.analisar(soil_input, rel_cfg)

        st.success(
            (
                "Análise concluída (placeholder). "
                "Conecte aqui sua rotina FORM/FOSM real."
            ),
        )

        colres1, colres2 = st.columns(2)
        with colres1:
            st.metric(
                "Índice de confiabilidade β",
                f"{resultado.indice_confiabilidade:.3f}",
            )
        with colres2:
            st.metric(
                "Probabilidade de falha P_f",
                f"{resultado.prob_falha:.5f}",
            )

        with st.expander("Detalhes do cálculo"):
            st.text(resultado.detalhes)
            st.json(
                {
                    "num_variaveis_aleatorias": len(random_vars_cfg),
                    "variaveis_aleatorias": {
                        nome: {
                            "distrib": cfg.distrib,
                            "media": cfg.media,
                            "desvio": cfg.desvio,
                            "correlacao": cfg.correlacao,
                        }
                        for nome, cfg in random_vars_cfg.items()
                    },
                },
            )

        if gerar_grafico:
            st.subheader("Gráfico tensão × deformação")
            fig, ax = plt.subplots()
            ax.plot(resultado.epsilon, resultado.sigma)
            ax.set_xlabel("Deformação ε")
            ax.set_ylabel("Tensão σ (kPa)")
            ax.set_title("Curva tensão × deformação (placeholder)")
            ax.grid(True)
            st.pyplot(fig)


if __name__ == "__main__":
    main()

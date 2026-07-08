from __future__ import annotations

import copy
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from simulador import (
    aplicar_veiculo_no_config,
    calcular_simulacao,
    config_padrao,
    ficha_veiculo,
    modelos_veiculo_disponiveis,
    moeda,
    percentual,
)


st.set_page_config(page_title="Driver Simulator", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
      .block-container {
        padding-top: 1.6rem;
      }

      /* Navegação principal com estilo de botões pastel */
      div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] {
        gap: 0.7rem;
        flex-wrap: wrap;
      }

      div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] button {
        background: #f2f7ef !important;
        border: 1px solid #d2ddca !important;
        border-radius: 10px !important;
        color: #2f3a2b !important;
        font-size: 1.12rem !important;
        font-weight: 700 !important;
        padding: 0.7rem 1.6rem !important;
        min-height: 50px !important;
        transition: all 0.18s ease;
      }

      div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] button p,
      div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] button span {
        font-size: 1.12rem !important;
        font-weight: 700 !important;
      }

      div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] button:hover {
        background: #e7f1e1;
        border-color: #b8caa9;
      }

      div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] button[aria-pressed="true"] {
        background: #d9e9cf;
        border-color: #9db98a;
        color: #1f2a1b;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def cfg_inicial() -> Dict[str, Any]:
    return copy.deepcopy(config_padrao())


def inicializar_estado() -> None:
    if "cfg" not in st.session_state:
        st.session_state.cfg = cfg_inicial()


def resetar_config() -> None:
    st.session_state.cfg = cfg_inicial()
    st.session_state["_sync_widgets_force"] = True


def garantir_config_v2(cfg: Dict[str, Any]) -> None:
    cfg_ref = config_padrao()
    cfg.setdefault("combustivel", copy.deepcopy(cfg_ref["combustivel"]))
    for chave, valor in cfg_ref["combustivel"].items():
        cfg["combustivel"].setdefault(chave, valor)

    modelo = cfg.get("veiculo", {}).get("modelo")
    if modelo:
        ficha = ficha_veiculo(modelo)
        for chave in (
            "autonomia_oficial_km",
            "autonomia_operacional_km",
            "reserva_bateria_percentual",
            "tempo_medio_recarga_min",
            "consumo_combustivel_km_l",
            "combustivel_default_litro",
            "capacidade_tanque_l",
        ):
            cfg["veiculo"].setdefault(chave, ficha[chave])


def div(n: float, d: float) -> float:
    return n / d if d else 0.0


def formatar_df_moeda(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in colunas:
        out[c] = out[c].map(moeda)
    return out


def sincronizar_estado_widgets(cfg: Dict[str, Any], force: bool = False) -> None:
    black = cfg["tarifas"]["black"]
    comfort = cfg["tarifas"]["comfort"]
    fixos = cfg["custos_fixos"]
    estado = {
        "sel_modelo": cfg["veiculo"]["modelo"],
        "veic_autonomia_operacional": float(cfg["veiculo"]["autonomia_operacional_km"]),
        "veic_reserva_bateria": int(cfg["veiculo"]["reserva_bateria_percentual"] * 100),
        "veic_tempo_recarga": float(cfg["veiculo"]["tempo_medio_recarga_min"]),
        "veic_consumo_combustivel": float(cfg["veiculo"].get("consumo_combustivel_km_l", 0.0)),
        "phev_eletrico_pct": int(cfg.get("combustivel", {}).get("percentual_eletrico_phev", 0.70) * 100),
        "preco_combustivel": float(cfg.get("combustivel", {}).get("preco_litro", 6.0)),
        "comb_cons": bool(cfg.get("combustivel", {}).get("considerar", True)),
        "mix_black_cfg": int(cfg["mix_categoria"]["percentual_black"] * 100),
        "tipo_modelo": cfg["modelo_financeiro"]["tipo"],
        "comissao_mesma_todas": bool(cfg["modelo_financeiro"]["comissao"].get("mesma_para_todas", True)),
        "comissao_unica_pct": int(cfg["modelo_financeiro"]["comissao"]["black"]["percentual"] * 100),
        "comissao_unica_fixa": float(cfg["modelo_financeiro"]["comissao"]["black"]["fixa_por_corrida"]),
        "comissao_black_pct": int(cfg["modelo_financeiro"]["comissao"]["black"]["percentual"] * 100),
        "comissao_black_fixa": float(cfg["modelo_financeiro"]["comissao"]["black"]["fixa_por_corrida"]),
        "comissao_comfort_pct": int(cfg["modelo_financeiro"]["comissao"]["comfort"]["percentual"] * 100),
        "comissao_comfort_fixa": float(
            cfg["modelo_financeiro"]["comissao"]["comfort"]["fixa_por_corrida"]
        ),
        "plano_sel": cfg["modelo_financeiro"]["passe"]["plano_selecionado"],
        "passe_24h": float(cfg["modelo_financeiro"]["passe"]["plano_24h"]),
        "passe_72h": float(cfg["modelo_financeiro"]["passe"]["plano_72h"]),
        "j_horas": float(cfg["jornada"]["horas_online_dia"]),
        "j_dias": float(cfg["jornada"]["dias_semana"]),
        "j_semanas": float(cfg["jornada"]["semanas_mes"]),
        "j_km_hora": float(cfg["jornada"]["km_rodados_hora"]),
        "j_km_corrida": float(cfg["jornada"]["km_corrida_media"]),
        "j_min_corrida": float(cfg["jornada"]["minutos_corrida_media"]),
        "j_km_pass": int(cfg["jornada"]["percentual_km_com_passageiro"] * 100),
        "usar_mesma_tarifa": bool(cfg["tarifas"].get("mesma_tarifa", False)),
        "t_same_base": float(black["tarifa_base"]),
        "t_same_km": float(black["valor_km"]),
        "t_same_min": float(black["valor_minuto"]),
        "t_same_mult": float(black["multiplicador_dinamico"]),
        "t_same_taxa_pct": int(black["taxa_plataforma_percentual"] * 100),
        "t_same_bonus": float(black["bonus_por_corrida"]),
        "tb_base": float(black["tarifa_base"]),
        "tb_km": float(black["valor_km"]),
        "tb_min": float(black["valor_minuto"]),
        "tb_mult": float(black["multiplicador_dinamico"]),
        "tb_taxa_pct": int(black["taxa_plataforma_percentual"] * 100),
        "tb_bonus": float(black["bonus_por_corrida"]),
        "tc_base": float(comfort["tarifa_base"]),
        "tc_km": float(comfort["valor_km"]),
        "tc_min": float(comfort["valor_minuto"]),
        "tc_mult": float(comfort["multiplicador_dinamico"]),
        "tc_taxa_pct": int(comfort["taxa_plataforma_percentual"] * 100),
        "tc_bonus": float(comfort["bonus_por_corrida"]),
        "e_cons": bool(cfg["energia"]["considerar"]),
        "e_solar": bool(cfg["energia"]["possui_solar"]),
        "e_prod": float(cfg["energia"]["producao_fotovoltaico_kwh_mes"]),
        "e_uso": int(cfg["energia"]["percentual_solar_usado"] * 100),
        "e_casa": float(cfg["energia"]["custo_kwh_casa"]),
        "e_rede": float(cfg["energia"]["custo_kwh_rede"]),
        "e_rede_publico": float(cfg["energia"]["custo_kwh_rede"]),
        "d_cons": bool(cfg["depreciacao"]["considerar"]),
        "d_val": float(cfg["depreciacao"]["valor_km"]),
        "v_cons": bool(cfg["custos_variaveis_km"]["considerar"]),
        "v_manut": float(cfg["custos_variaveis_km"]["manutencao_corretiva"]),
        "v_pneu": float(cfg["custos_variaveis_km"]["pneus"]),
        "v_freio": float(cfg["custos_variaveis_km"]["freios"]),
        "f_cons": bool(fixos["considerar"]),
        "fixo_seguro": float(fixos["seguro"]),
        "fixo_ipva_mensal": float(fixos["ipva_mensal"]),
        "fixo_licenciamento_mensal": float(fixos["licenciamento_mensal"]),
        "fixo_mei_das": float(fixos["mei_das"]),
        "fixo_internet_celular": float(fixos["internet_celular"]),
        "fixo_manutencao_preventiva_mensal": float(fixos["manutencao_preventiva_mensal"]),
        "fixo_lavagem_estetica": float(fixos["lavagem_estetica"]),
        "fixo_outros": float(fixos["outros"]),
    }
    for chave, valor in estado.items():
        if force or chave not in st.session_state:
            st.session_state[chave] = valor


def sincronizar_sugestoes_veiculo_no_widget_state(cfg: Dict[str, Any]) -> None:
    if "d_val" in st.session_state:
        st.session_state["d_val"] = float(cfg["depreciacao"]["valor_km"])
    if "fixo_seguro" in st.session_state:
        st.session_state["fixo_seguro"] = float(cfg["custos_fixos"]["seguro"])
    st.session_state["veic_autonomia_operacional"] = float(
        cfg["veiculo"]["autonomia_operacional_km"]
    )
    st.session_state["veic_reserva_bateria"] = int(
        cfg["veiculo"]["reserva_bateria_percentual"] * 100
    )
    st.session_state["veic_tempo_recarga"] = float(cfg["veiculo"]["tempo_medio_recarga_min"])
    st.session_state["veic_consumo_combustivel"] = float(
        cfg["veiculo"].get("consumo_combustivel_km_l", 0.0)
    )
    st.session_state["preco_combustivel"] = float(cfg["combustivel"].get("preco_litro", 6.0))


def aplicar_veiculo_selecionado_no_cfg(cfg: Dict[str, Any]) -> None:
    modelo = st.session_state.get("sel_modelo")
    if not modelo or modelo == cfg["veiculo"]["modelo"]:
        return

    atualizar_sugestoes = bool(st.session_state.get("aplicar_sugestao", True))
    aplicar_veiculo_no_config(cfg, modelo, atualizar_custos_sugeridos=atualizar_sugestoes)
    if atualizar_sugestoes:
        sincronizar_sugestoes_veiculo_no_widget_state(cfg)


def aplicar_widget_state_no_cfg(cfg: Dict[str, Any]) -> None:
    if "veic_autonomia_operacional" in st.session_state:
        cfg["veiculo"]["autonomia_operacional_km"] = float(
            st.session_state["veic_autonomia_operacional"]
        )
    if "veic_reserva_bateria" in st.session_state:
        cfg["veiculo"]["reserva_bateria_percentual"] = (
            int(st.session_state["veic_reserva_bateria"]) / 100.0
        )
    if "veic_tempo_recarga" in st.session_state:
        cfg["veiculo"]["tempo_medio_recarga_min"] = float(st.session_state["veic_tempo_recarga"])
    if "veic_consumo_combustivel" in st.session_state:
        cfg["veiculo"]["consumo_combustivel_km_l"] = float(
            st.session_state["veic_consumo_combustivel"]
        )

    if "phev_eletrico_pct" in st.session_state:
        cfg["combustivel"]["percentual_eletrico_phev"] = (
            int(st.session_state["phev_eletrico_pct"]) / 100.0
        )
    if "preco_combustivel" in st.session_state:
        cfg["combustivel"]["preco_litro"] = float(st.session_state["preco_combustivel"])
    if "comb_cons" in st.session_state:
        cfg["combustivel"]["considerar"] = bool(st.session_state["comb_cons"])

    for origem, destino in (
        ("e_cons", ("energia", "considerar")),
        ("e_solar", ("energia", "possui_solar")),
        ("d_cons", ("depreciacao", "considerar")),
        ("v_cons", ("custos_variaveis_km", "considerar")),
        ("f_cons", ("custos_fixos", "considerar")),
    ):
        if origem in st.session_state:
            cfg[destino[0]][destino[1]] = bool(st.session_state[origem])


def custos_consolidados(cfg: Dict[str, Any], res: Dict[str, Any]) -> Dict[str, float]:
    km_total = res["km_total_mes"]
    comp = res["componentes_km"]

    energia = comp["energia"] * km_total
    combustivel = comp.get("combustivel", 0.0) * km_total
    depreciacao = comp["depreciacao"] * km_total
    variaveis_sem_energia_dep = (
        comp["manutencao_corretiva"] + comp["pneus"] + comp["freios"]
    ) * km_total
    fixos = res["custo_fixo_total"]
    plataforma = res["cenario_misto"]["taxas_ou_passe_mes"]
    total_operacional = energia + combustivel + depreciacao + variaveis_sem_energia_dep + fixos
    total_geral = total_operacional + plataforma

    return {
        "energia": energia,
        "combustivel": combustivel,
        "plataforma": plataforma,
        "depreciacao": depreciacao,
        "variaveis_sem_energia_dep": variaveis_sem_energia_dep,
        "fixos": fixos,
        "total_operacional": total_operacional,
        "total_geral": total_geral,
    }


def receita_por_categoria(cfg: Dict[str, Any], res: Dict[str, Any]) -> Dict[str, float]:
    black = res["receita_black"]["receita_bruta_mes"]
    comfort = res["receita_comfort"]["receita_bruta_mes"]
    total = black + comfort
    return {"black": black, "comfort": comfort, "total": total}


def indicadores_gerais(cfg: Dict[str, Any], res: Dict[str, Any]) -> Dict[str, float]:
    receita_bruta = res["cenario_misto"]["receita_bruta_mes"]
    receita_apos_uber = res["cenario_misto"]["receita_liquida_mes"]
    custos_operacao = res["custo_total_mes"]
    lucro = res["lucro_liquido"]

    horas_mes = res["horas_mes"]
    km_mes = res["km_total_mes"]
    dias_trabalhados = cfg["jornada"]["dias_semana"] * cfg["jornada"]["semanas_mes"]
    semanas_mes = cfg["jornada"]["semanas_mes"]

    return {
        "receita_bruta": receita_bruta,
        "receita_apos_uber": receita_apos_uber,
        "custos_operacao": custos_operacao,
        "lucro": lucro,
        "margem_liquida": div(lucro, receita_bruta),
        "lucro_hora": div(lucro, horas_mes),
        "receita_hora": div(receita_apos_uber, horas_mes),
        "lucro_dia": div(lucro, dias_trabalhados),
        "lucro_semana": div(lucro, semanas_mes),
        "receita_km": div(receita_apos_uber, km_mes),
        "custo_km": div(custos_operacao, km_mes),
        "lucro_km": div(lucro, km_mes),
    }


def tabela_semanal(cfg: Dict[str, Any], res: Dict[str, Any]) -> pd.DataFrame:
    semanas_mes = max(cfg["jornada"]["semanas_mes"], 0.0)
    if semanas_mes == 0:
        return pd.DataFrame(
            columns=["Semana", "Horas", "KM", "Corridas", "Recargas", "Receita", "Custos", "Lucro"]
        )

    semanas_cheias = int(semanas_mes)
    sobra = semanas_mes - semanas_cheias
    fatores = [1.0] * semanas_cheias
    if sobra > 1e-9:
        fatores.append(sobra)

    rows = []
    for i, fator in enumerate(fatores, start=1):
        receita = res["cenario_misto"]["receita_liquida_mes"] * (fator / semanas_mes)
        custos = res["custo_total_mes"] * (fator / semanas_mes)
        rows.append(
            {
                "Semana": f"Semana {i}" if fator == 1.0 else f"Semana {i} (parcial)",
                "Horas": res["horas_produtivas_mes"] * (fator / semanas_mes),
                "KM": res["km_total_mes"] * (fator / semanas_mes),
                "Corridas": res["corridas_mes"] * (fator / semanas_mes),
                "Recargas": res["recargas_mes"] * (fator / semanas_mes),
                "Receita": receita,
                "Custos": custos,
                "Lucro": receita - custos,
            }
        )
    return pd.DataFrame(rows)


def cenarios_rapidos(cfg_base: Dict[str, Any]) -> pd.DataFrame:
    rows = []

    def add(nome: str, mutator) -> None:
        cfg = copy.deepcopy(cfg_base)
        mutator(cfg)
        r = calcular_simulacao(cfg)
        rows.append(
            {
                "Cenário": nome,
                "Receita": r["cenario_misto"]["receita_liquida_mes"],
                "Custos": r["custo_total_mes"],
                "Lucro": r["lucro_liquido"],
                "Margem": div(r["lucro_liquido"], r["cenario_misto"]["receita_bruta_mes"]),
            }
        )

    add("Base", lambda cfg: None)

    def conservador(cfg: Dict[str, Any]) -> None:
        cfg["mix_categoria"]["percentual_black"] = max(
            0.0, cfg["mix_categoria"]["percentual_black"] - 0.10
        )
        cfg["jornada"]["km_rodados_hora"] = max(1.0, cfg["jornada"]["km_rodados_hora"] * 0.92)
        for cat in ("black", "comfort"):
            cfg["tarifas"][cat]["multiplicador_dinamico"] = max(
                0.7, cfg["tarifas"][cat]["multiplicador_dinamico"] - 0.10
            )
            cfg["tarifas"][cat]["bonus_por_corrida"] = max(
                0.0, cfg["tarifas"][cat]["bonus_por_corrida"] - 0.5
            )
        if cfg["modelo_financeiro"]["tipo"] == "comissao":
            for cat in ("black", "comfort"):
                cfg["modelo_financeiro"]["comissao"][cat]["percentual"] = min(
                    0.60, cfg["modelo_financeiro"]["comissao"][cat]["percentual"] + 0.05
                )
        else:
            cfg["modelo_financeiro"]["passe"]["plano_selecionado"] = "72h"
            cfg["modelo_financeiro"]["passe"]["plano_72h"] *= 1.15
        for k in list(cfg["custos_fixos"].keys()):
            if k != "considerar":
                cfg["custos_fixos"][k] *= 1.10
        cfg["depreciacao"]["valor_km"] *= 1.10
        for k in ("manutencao_corretiva", "pneus", "freios"):
            cfg["custos_variaveis_km"][k] *= 1.10

    def otimista(cfg: Dict[str, Any]) -> None:
        cfg["mix_categoria"]["percentual_black"] = min(
            1.0, cfg["mix_categoria"]["percentual_black"] + 0.10
        )
        cfg["jornada"]["km_rodados_hora"] = cfg["jornada"]["km_rodados_hora"] * 1.08
        for cat in ("black", "comfort"):
            cfg["tarifas"][cat]["multiplicador_dinamico"] += 0.10
            cfg["tarifas"][cat]["bonus_por_corrida"] += 0.5
        if cfg["modelo_financeiro"]["tipo"] == "comissao":
            for cat in ("black", "comfort"):
                cfg["modelo_financeiro"]["comissao"][cat]["percentual"] = max(
                    0.0, cfg["modelo_financeiro"]["comissao"][cat]["percentual"] - 0.05
                )
        else:
            cfg["modelo_financeiro"]["passe"]["plano_24h"] *= 0.90
            cfg["modelo_financeiro"]["passe"]["plano_72h"] *= 0.90
        for k in list(cfg["custos_fixos"].keys()):
            if k != "considerar":
                cfg["custos_fixos"][k] *= 0.95
        cfg["depreciacao"]["valor_km"] *= 0.95
        for k in ("manutencao_corretiva", "pneus", "freios"):
            cfg["custos_variaveis_km"][k] *= 0.95

    add("Conservador", conservador)
    add("Otimista", otimista)
    return pd.DataFrame(rows)


inicializar_estado()
cfg = st.session_state.cfg
garantir_config_v2(cfg)
cfg_default = config_padrao()
sincronizar_estado_widgets(cfg, force=bool(st.session_state.pop("_sync_widgets_force", False)))
aplicar_veiculo_selecionado_no_cfg(cfg)

st.title("Driver Simulator")
st.caption("Versão 1.0")

opcoes_abas = ["Configurar", "Resumo", "Semanal", "Cenários", "Dashboard"]
if hasattr(st, "segmented_control"):
    aba_ativa = st.segmented_control(
        "Navegação",
        options=opcoes_abas,
        default=st.session_state.get("aba_ativa", opcoes_abas[0]),
        selection_mode="single",
        label_visibility="collapsed",
        key="aba_ativa",
    )
else:
    aba_ativa = st.radio(
        "Navegação",
        opcoes_abas,
        horizontal=True,
        label_visibility="collapsed",
        key="aba_ativa",
    )

if aba_ativa == "Configurar":
    top1, top2 = st.columns([1, 4])
    with top1:
        if st.button("Resetar padrão", use_container_width=True):
            resetar_config()
            st.rerun()

    left, right = st.columns([1.1, 1.9])

    with left:
        st.subheader("Veículo")
        modelos = modelos_veiculo_disponiveis()
        modelo_atual = cfg["veiculo"]["modelo"]
        idx = modelos.index(modelo_atual) if modelo_atual in modelos else 0
        modelo_sel = st.selectbox("Modelo BYD", modelos, index=idx, key="sel_modelo")
        v1, v2 = st.columns(2)
        with v1:
            aplicar_sugestao = st.checkbox(
                "Aplicar custos sugeridos do veículo", value=True, key="aplicar_sugestao"
            )
        with v2:
            if st.button("🔄 Restaurar valores do veículo", key="btn_restaurar_veiculo"):
                aplicar_veiculo_no_config(cfg, modelo_sel, atualizar_custos_sugeridos=True)
                sincronizar_sugestoes_veiculo_no_widget_state(cfg)

        op1, op2, op3 = st.columns(3)
        with op1:
            cfg["veiculo"]["autonomia_operacional_km"] = st.number_input(
                "Autonomia operacional (km)",
                min_value=1.0,
                value=float(cfg["veiculo"]["autonomia_operacional_km"]),
                step=5.0,
                key="veic_autonomia_operacional",
            )
        with op2:
            cfg["veiculo"]["reserva_bateria_percentual"] = (
                st.slider(
                    "Reserva bateria (%)",
                    min_value=0,
                    max_value=50,
                    value=int(cfg["veiculo"]["reserva_bateria_percentual"] * 100),
                    step=1,
                    key="veic_reserva_bateria",
                )
                / 100.0
            )
        with op3:
            cfg["veiculo"]["tempo_medio_recarga_min"] = st.number_input(
                "Tempo recarga (min)",
                min_value=0.0,
                value=float(cfg["veiculo"]["tempo_medio_recarga_min"]),
                step=5.0,
                key="veic_tempo_recarga",
            )

        if cfg["veiculo"]["propulsao"] == "PHEV":
            ph0, ph1, ph2, ph3 = st.columns(4)
            with ph0:
                cfg["combustivel"]["considerar"] = st.checkbox(
                    "Considerar combustível",
                    value=bool(cfg["combustivel"]["considerar"]),
                    key="comb_cons",
                )
            with ph1:
                cfg["combustivel"]["percentual_eletrico_phev"] = (
                    st.slider(
                        "Uso elétrico PHEV (%)",
                        min_value=0,
                        max_value=100,
                        value=int(cfg["combustivel"]["percentual_eletrico_phev"] * 100),
                        step=5,
                        key="phev_eletrico_pct",
                    )
                    / 100.0
                )
            with ph2:
                cfg["combustivel"]["preco_litro"] = st.number_input(
                    "Combustível (R$/L)",
                    min_value=0.0,
                    value=float(cfg["combustivel"]["preco_litro"]),
                    step=0.1,
                    key="preco_combustivel",
                )
            with ph3:
                cfg["veiculo"]["consumo_combustivel_km_l"] = st.number_input(
                    "Consumo (km/L)",
                    min_value=0.0,
                    value=max(0.0, float(cfg["veiculo"]["consumo_combustivel_km_l"])),
                    step=0.5,
                    key="veic_consumo_combustivel",
                )

        ficha_df = pd.DataFrame(
            [
                {"Campo": "Modelo", "Valor": cfg["veiculo"]["modelo"]},
                {"Campo": "Propulsão", "Valor": cfg["veiculo"]["propulsao"]},
                {"Campo": "Bateria", "Valor": f"{cfg['veiculo']['bateria_kwh']:.1f} kWh"},
                {"Campo": "Autonomia oficial", "Valor": f"{cfg['veiculo']['autonomia_oficial_km']:.0f} km"},
                {"Campo": "Autonomia operacional", "Valor": f"{cfg['veiculo']['autonomia_operacional_km']:.0f} km"},
                {
                    "Campo": "Autonomia útil",
                    "Valor": f"{cfg['veiculo']['autonomia_operacional_km'] * (1 - cfg['veiculo']['reserva_bateria_percentual']):.0f} km",
                },
                {"Campo": "Potência", "Valor": f"{cfg['veiculo']['potencia_cv']} cv"},
                {"Campo": "Consumo", "Valor": f"{cfg['veiculo']['consumo_kwh_por_km']:.3f} kWh/km"},
                {"Campo": "Valor do veículo", "Valor": moeda(cfg["veiculo"]["preco_veiculo"])},
            ]
        )
        st.dataframe(ficha_df, use_container_width=True, hide_index=True)

        st.subheader("Categoria")
        black_pct_atual = int(cfg["mix_categoria"]["percentual_black"] * 100)
        comfort_pct_atual = 100 - black_pct_atual
        st.markdown("**Black**")
        st.markdown(f"**{black_pct_atual}%**")
        cfg["mix_categoria"]["percentual_black"] = (
            st.slider(
                "Mix Black (%)",
                min_value=0,
                max_value=100,
                value=black_pct_atual,
                step=1,
                key="mix_black_cfg",
                label_visibility="collapsed",
            )
            / 100.0
        )
        black_pct = int(cfg["mix_categoria"]["percentual_black"] * 100)
        comfort_pct = 100 - black_pct
        st.markdown("**Comfort**")
        st.markdown(f"**{comfort_pct}%**")
        st.markdown(f"Black {black_pct}%  \nComfort {comfort_pct}%")

        st.subheader("Modelo Financeiro")
        tipo = st.radio(
            "Tipo",
            options=["passe", "comissao"],
            index=0 if cfg["modelo_financeiro"]["tipo"] == "passe" else 1,
            format_func=lambda x: "Passe para Motoristas" if x == "passe" else "Comissão por corrida",
            horizontal=True,
            key="tipo_modelo",
        )
        cfg["modelo_financeiro"]["tipo"] = tipo

        if tipo == "comissao":
            mesma = st.checkbox(
                "Utilizar a mesma comissão para todas as categorias",
                value=bool(cfg["modelo_financeiro"]["comissao"].get("mesma_para_todas", True)),
                key="comissao_mesma_todas",
            )
            cfg["modelo_financeiro"]["comissao"]["mesma_para_todas"] = bool(mesma)
            if mesma:
                comissao_pct = (
                    st.slider(
                        "Comissão (%)",
                        min_value=0,
                        max_value=60,
                        value=int(cfg["modelo_financeiro"]["comissao"]["black"]["percentual"] * 100),
                        key="comissao_unica_pct",
                    )
                    / 100.0
                )
                comissao_fixa = st.number_input(
                    "Taxa fixa por corrida (R$)",
                    min_value=0.0,
                    value=float(cfg["modelo_financeiro"]["comissao"]["black"]["fixa_por_corrida"]),
                    step=0.1,
                    key="comissao_unica_fixa",
                )
                for cat in ("black", "comfort"):
                    cfg["modelo_financeiro"]["comissao"][cat]["percentual"] = comissao_pct
                    cfg["modelo_financeiro"]["comissao"][cat]["fixa_por_corrida"] = comissao_fixa
            else:
                cfg["modelo_financeiro"]["comissao"]["black"]["percentual"] = (
                    st.slider(
                        "Comissão Black (%)",
                        min_value=0,
                        max_value=60,
                        value=int(cfg["modelo_financeiro"]["comissao"]["black"]["percentual"] * 100),
                        key="comissao_black_pct",
                    )
                    / 100.0
                )
                cfg["modelo_financeiro"]["comissao"]["black"]["fixa_por_corrida"] = st.number_input(
                    "Taxa fixa por corrida - Black (R$)",
                    min_value=0.0,
                    value=float(cfg["modelo_financeiro"]["comissao"]["black"]["fixa_por_corrida"]),
                    step=0.1,
                    key="comissao_black_fixa",
                )
                cfg["modelo_financeiro"]["comissao"]["comfort"]["percentual"] = (
                    st.slider(
                        "Comissão Comfort (%)",
                        min_value=0,
                        max_value=60,
                        value=int(cfg["modelo_financeiro"]["comissao"]["comfort"]["percentual"] * 100),
                        key="comissao_comfort_pct",
                    )
                    / 100.0
                )
                cfg["modelo_financeiro"]["comissao"]["comfort"]["fixa_por_corrida"] = st.number_input(
                    "Taxa fixa por corrida - Comfort (R$)",
                    min_value=0.0,
                    value=float(cfg["modelo_financeiro"]["comissao"]["comfort"]["fixa_por_corrida"]),
                    step=0.1,
                    key="comissao_comfort_fixa",
                )
        else:
            cfg["modelo_financeiro"]["passe"]["plano_selecionado"] = st.radio(
                "Plano",
                options=["24h", "72h"],
                index=0 if cfg["modelo_financeiro"]["passe"]["plano_selecionado"] == "24h" else 1,
                horizontal=True,
                key="plano_sel",
            )
            if cfg["modelo_financeiro"]["passe"]["plano_selecionado"] == "24h":
                cfg["modelo_financeiro"]["passe"]["plano_24h"] = st.number_input(
                    "Valor do Passe 24h (R$)",
                    min_value=0.0,
                    value=float(cfg["modelo_financeiro"]["passe"]["plano_24h"]),
                    step=1.0,
                    key="passe_24h",
                )
            else:
                cfg["modelo_financeiro"]["passe"]["plano_72h"] = st.number_input(
                    "Valor do Passe 72h (R$)",
                    min_value=0.0,
                    value=float(cfg["modelo_financeiro"]["passe"]["plano_72h"]),
                    step=1.0,
                    key="passe_72h",
                )

    with right:
        st.subheader("Jornada")
        j1, j2, j3 = st.columns(3)
        with j1:
            cfg["jornada"]["horas_online_dia"] = st.number_input(
                "Horas por dia",
                min_value=0.0,
                max_value=24.0,
                value=float(cfg["jornada"]["horas_online_dia"]),
                step=0.5,
                key="j_horas",
            )
            cfg["jornada"]["dias_semana"] = st.number_input(
                "Dias por semana",
                min_value=0.0,
                max_value=7.0,
                value=float(cfg["jornada"]["dias_semana"]),
                step=1.0,
                key="j_dias",
            )
            cfg["jornada"]["semanas_mes"] = st.number_input(
                "Semanas por mês",
                min_value=0.0,
                max_value=5.0,
                value=float(cfg["jornada"]["semanas_mes"]),
                step=0.1,
                key="j_semanas",
            )
        with j2:
            cfg["jornada"]["km_rodados_hora"] = st.number_input(
                "KM/hora",
                min_value=0.0,
                value=float(cfg["jornada"]["km_rodados_hora"]),
                step=0.5,
                key="j_km_hora",
            )
            cfg["jornada"]["km_corrida_media"] = st.number_input(
                "KM por corrida",
                min_value=0.1,
                value=float(cfg["jornada"]["km_corrida_media"]),
                step=0.1,
                key="j_km_corrida",
            )
            cfg["jornada"]["minutos_corrida_media"] = st.number_input(
                "Minutos por corrida",
                min_value=1.0,
                value=float(cfg["jornada"]["minutos_corrida_media"]),
                step=1.0,
                key="j_min_corrida",
            )
        with j3:
            cfg["jornada"]["percentual_km_com_passageiro"] = (
                st.slider(
                    "Aproveitamento da quilometragem (%)",
                    min_value=0,
                    max_value=100,
                    value=int(cfg["jornada"]["percentual_km_com_passageiro"] * 100),
                    step=1,
                    key="j_km_pass",
                )
                / 100.0
            )
            pct_com = int(cfg["jornada"]["percentual_km_com_passageiro"] * 100)
            pct_sem = 100 - pct_com
            st.caption(f"{pct_com}% dos quilômetros serão rodados com passageiro.")
            st.caption(f"{pct_sem}% dos quilômetros serão rodados sem passageiro.")

        if st.button("🔄 Restaurar jornada sugerida", key="restaurar_jornada"):
            cfg["jornada"]["horas_online_dia"] = 10.0
            cfg["jornada"]["dias_semana"] = 6.0
            cfg["jornada"]["semanas_mes"] = 4.3
            cfg["jornada"]["km_rodados_hora"] = 22.0
            cfg["jornada"]["km_corrida_media"] = 8.5
            cfg["jornada"]["minutos_corrida_media"] = 18.0
            cfg["jornada"]["percentual_km_com_passageiro"] = 0.65
            st.session_state["_sync_widgets_force"] = True
            st.rerun()

        st.subheader(
            "Tarifas",
            help="Esses valores representam quanto o motorista recebe por corrida antes da aplicação do modelo financeiro (Passe ou Comissão).",
        )
        if st.button("🔄 Restaurar tarifas sugeridas", key="restaurar_tarifas"):
            cfg["tarifas"]["black"]["tarifa_base"] = 5.00
            cfg["tarifas"]["black"]["valor_km"] = 2.35
            cfg["tarifas"]["black"]["valor_minuto"] = 0.40
            cfg["tarifas"]["black"]["multiplicador_dinamico"] = 1.00
            cfg["tarifas"]["black"]["taxa_plataforma_percentual"] = 0.00
            cfg["tarifas"]["black"]["bonus_por_corrida"] = 0.00
            cfg["tarifas"]["comfort"]["tarifa_base"] = 3.50
            cfg["tarifas"]["comfort"]["valor_km"] = 1.65
            cfg["tarifas"]["comfort"]["valor_minuto"] = 0.28
            cfg["tarifas"]["comfort"]["multiplicador_dinamico"] = 1.00
            cfg["tarifas"]["comfort"]["taxa_plataforma_percentual"] = 0.00
            cfg["tarifas"]["comfort"]["bonus_por_corrida"] = 0.00
            st.session_state["_sync_widgets_force"] = True
            st.rerun()

        usar_mesma_tarifa = st.checkbox(
            "Utilizar a mesma tarifa para Black e Comfort",
            value=bool(cfg["tarifas"].get("mesma_tarifa", False)),
            key="usar_mesma_tarifa",
        )
        cfg["tarifas"]["mesma_tarifa"] = bool(usar_mesma_tarifa)

        if usar_mesma_tarifa:
            st.markdown("**Tarifa Única (Black e Comfort)**")
            t = cfg["tarifas"]["black"]
            t["tarifa_base"] = st.number_input(
                "Tarifa Base (R$)",
                min_value=0.0,
                value=float(t["tarifa_base"]),
                step=0.1,
                key="t_same_base",
            )
            t["valor_km"] = st.number_input(
                "Valor por KM (R$)",
                min_value=0.0,
                value=float(t["valor_km"]),
                step=0.1,
                key="t_same_km",
            )
            t["valor_minuto"] = st.number_input(
                "Valor por Minuto (R$)",
                min_value=0.0,
                value=float(t["valor_minuto"]),
                step=0.01,
                key="t_same_min",
            )
            t["multiplicador_dinamico"] = st.number_input(
                "Multiplicador da tarifa dinâmica",
                min_value=0.0,
                value=float(t["multiplicador_dinamico"]),
                step=0.05,
                key="t_same_mult",
            )
            st.caption("1,00 = sem dinâmica | 1,20 = +20% | 1,50 = +50% | 2,00 = dobro da tarifa")
            if cfg["modelo_financeiro"]["tipo"] == "comissao":
                t["taxa_plataforma_percentual"] = (
                    st.slider(
                        "Taxa da plataforma (%)",
                        min_value=0,
                        max_value=40,
                        value=int(t["taxa_plataforma_percentual"] * 100),
                        step=1,
                        format="%d%%",
                        key="t_same_taxa_pct",
                    )
                    / 100.0
                )
            else:
                t["taxa_plataforma_percentual"] = 0.0
            t["bonus_por_corrida"] = st.number_input(
                "Bônus (R$/corrida)",
                min_value=0.0,
                value=float(t["bonus_por_corrida"]),
                step=0.1,
                key="t_same_bonus",
            )
            for cat in ("black", "comfort"):
                cfg["tarifas"][cat]["tarifa_base"] = t["tarifa_base"]
                cfg["tarifas"][cat]["valor_km"] = t["valor_km"]
                cfg["tarifas"][cat]["valor_minuto"] = t["valor_minuto"]
                cfg["tarifas"][cat]["multiplicador_dinamico"] = t["multiplicador_dinamico"]
                cfg["tarifas"][cat]["taxa_plataforma_percentual"] = t["taxa_plataforma_percentual"]
                cfg["tarifas"][cat]["bonus_por_corrida"] = t["bonus_por_corrida"]
        else:
            b, c = st.columns(2)
            with b:
                st.markdown("**Black**")
                tb = cfg["tarifas"]["black"]
                tb["tarifa_base"] = st.number_input(
                    "Tarifa Base Black (R$)",
                    min_value=0.0,
                    value=float(tb["tarifa_base"]),
                    step=0.1,
                    key="tb_base",
                )
                tb["valor_km"] = st.number_input(
                    "Valor por KM Black (R$)",
                    min_value=0.0,
                    value=float(tb["valor_km"]),
                    step=0.1,
                    key="tb_km",
                )
                tb["valor_minuto"] = st.number_input(
                    "Valor por Minuto Black (R$)",
                    min_value=0.0,
                    value=float(tb["valor_minuto"]),
                    step=0.01,
                    key="tb_min",
                )
                tb["multiplicador_dinamico"] = st.number_input(
                    "Multiplicador da tarifa dinâmica Black",
                    min_value=0.0,
                    value=float(tb["multiplicador_dinamico"]),
                    step=0.05,
                    key="tb_mult",
                )
                st.caption("1,00 = sem dinâmica | 1,20 = +20% | 1,50 = +50% | 2,00 = dobro da tarifa")
                if cfg["modelo_financeiro"]["tipo"] == "comissao":
                    tb["taxa_plataforma_percentual"] = (
                        st.slider(
                            "Taxa da plataforma Black (%)",
                            min_value=0,
                            max_value=40,
                            value=int(tb["taxa_plataforma_percentual"] * 100),
                            step=1,
                            format="%d%%",
                            key="tb_taxa_pct",
                        )
                        / 100.0
                    )
                else:
                    tb["taxa_plataforma_percentual"] = 0.0
                tb["bonus_por_corrida"] = st.number_input(
                    "Bônus Black (R$/corrida)",
                    min_value=0.0,
                    value=float(tb["bonus_por_corrida"]),
                    step=0.1,
                    key="tb_bonus",
                )
            with c:
                st.markdown("**Comfort**")
                tc = cfg["tarifas"]["comfort"]
                tc["tarifa_base"] = st.number_input(
                    "Tarifa Base Comfort (R$)",
                    min_value=0.0,
                    value=float(tc["tarifa_base"]),
                    step=0.1,
                    key="tc_base",
                )
                tc["valor_km"] = st.number_input(
                    "Valor por KM Comfort (R$)",
                    min_value=0.0,
                    value=float(tc["valor_km"]),
                    step=0.1,
                    key="tc_km",
                )
                tc["valor_minuto"] = st.number_input(
                    "Valor por Minuto Comfort (R$)",
                    min_value=0.0,
                    value=float(tc["valor_minuto"]),
                    step=0.01,
                    key="tc_min",
                )
                tc["multiplicador_dinamico"] = st.number_input(
                    "Multiplicador da tarifa dinâmica Comfort",
                    min_value=0.0,
                    value=float(tc["multiplicador_dinamico"]),
                    step=0.05,
                    key="tc_mult",
                )
                st.caption("1,00 = sem dinâmica | 1,20 = +20% | 1,50 = +50% | 2,00 = dobro da tarifa")
                if cfg["modelo_financeiro"]["tipo"] == "comissao":
                    tc["taxa_plataforma_percentual"] = (
                        st.slider(
                            "Taxa da plataforma Comfort (%)",
                            min_value=0,
                            max_value=40,
                            value=int(tc["taxa_plataforma_percentual"] * 100),
                            step=1,
                            format="%d%%",
                            key="tc_taxa_pct",
                        )
                        / 100.0
                    )
                else:
                    tc["taxa_plataforma_percentual"] = 0.0
                tc["bonus_por_corrida"] = st.number_input(
                    "Bônus Comfort (R$/corrida)",
                    min_value=0.0,
                    value=float(tc["bonus_por_corrida"]),
                    step=0.1,
                    key="tc_bonus",
                )

        st.subheader("Custos (Avançado)")
        with st.expander("Energia Elétrica", expanded=False):
            e = cfg["energia"]
            st.caption(
                "Configure apenas se desejar calcular o custo real de energia do veículo.\n"
                "Caso contrário, desmarque \"Considerar custo de energia\" e esse custo será ignorado."
            )
            l1, l2 = st.columns([2, 1.2])
            with l1:
                e["considerar"] = st.checkbox(
                    "Considerar custo de energia", value=bool(e["considerar"]), key="e_cons"
                )
            with l2:
                if st.button("🔄 Restaurar valores sugeridos", key="restaurar_energia"):
                    e["producao_fotovoltaico_kwh_mes"] = cfg_default["energia"][
                        "producao_fotovoltaico_kwh_mes"
                    ]
                    e["percentual_solar_usado"] = cfg_default["energia"]["percentual_solar_usado"]
                    e["custo_kwh_casa"] = cfg_default["energia"]["custo_kwh_casa"]
                    e["custo_kwh_rede"] = cfg_default["energia"]["custo_kwh_rede"]
                    e["custo_kwh_unico"] = cfg_default["energia"]["custo_kwh_unico"]
                    e["considerar"] = bool(cfg_default["energia"]["considerar"])
                    e["possui_solar"] = bool(cfg_default["energia"]["possui_solar"])
                    st.session_state["_sync_widgets_force"] = True
                    st.rerun()
            if e["considerar"]:
                e["possui_solar"] = st.checkbox(
                    "Possui energia solar", value=bool(e["possui_solar"]), key="e_solar"
                )
                if e["possui_solar"]:
                    e["producao_fotovoltaico_kwh_mes"] = st.number_input(
                        "Produção solar (kWh/mês)",
                        min_value=0.0,
                        value=float(e["producao_fotovoltaico_kwh_mes"]),
                        step=50.0,
                        key="e_prod",
                    )
                    e["percentual_solar_usado"] = (
                        st.slider(
                            "Uso da energia solar (%)",
                            min_value=0,
                            max_value=100,
                            value=int(e["percentual_solar_usado"] * 100),
                            key="e_uso",
                        )
                        / 100.0
                    )
                    pct_solar = int(e["percentual_solar_usado"] * 100)
                    pct_rede = 100 - pct_solar
                    st.caption(f"Energia solar: {pct_solar}%")
                    st.caption(f"Rede elétrica: {pct_rede}%")
                    e["custo_kwh_casa"] = st.number_input(
                        "Custo do kWh residencial (R$)",
                        min_value=0.0,
                        value=float(e["custo_kwh_casa"]),
                        step=0.05,
                        key="e_casa",
                    )
                    e["custo_kwh_rede"] = st.number_input(
                        "Custo do carregador público (R$)",
                        min_value=0.0,
                        value=float(e["custo_kwh_rede"]),
                        step=0.05,
                        key="e_rede",
                    )
                else:
                    e["custo_kwh_rede"] = st.number_input(
                        "Custo do carregador público (R$)",
                        min_value=0.0,
                        value=float(e["custo_kwh_rede"]),
                        step=0.05,
                        key="e_rede_publico",
                    )

        with st.expander("Depreciação", expanded=False):
            d = cfg["depreciacao"]
            l1, l2 = st.columns([2, 1.2])
            with l1:
                d["considerar"] = st.checkbox(
                    "Considerar depreciação", value=bool(d["considerar"]), key="d_cons"
                )
            with l2:
                if st.button("🔄 Restaurar valores sugeridos", key="restaurar_depreciacao"):
                    d["considerar"] = True
                    d["valor_km"] = float(cfg["veiculo"]["depreciacao_km_sugerida"])
                    st.session_state["_sync_widgets_force"] = True
                    st.rerun()
            if d["considerar"]:
                d["valor_km"] = st.number_input(
                    "Depreciação (R$/km)",
                    min_value=0.0,
                    value=float(d["valor_km"]),
                    step=0.01,
                    key="d_val",
                )

        with st.expander("Custos Variáveis", expanded=False):
            v = cfg["custos_variaveis_km"]
            l1, l2 = st.columns([2, 1.2])
            with l1:
                v["considerar"] = st.checkbox(
                    "Considerar custos variáveis", value=bool(v["considerar"]), key="v_cons"
                )
            with l2:
                if st.button("🔄 Restaurar valores sugeridos", key="restaurar_variaveis"):
                    v["considerar"] = True
                    v["manutencao_corretiva"] = cfg_default["custos_variaveis_km"][
                        "manutencao_corretiva"
                    ]
                    v["pneus"] = cfg_default["custos_variaveis_km"]["pneus"]
                    v["freios"] = cfg_default["custos_variaveis_km"]["freios"]
                    st.session_state["_sync_widgets_force"] = True
                    st.rerun()
            if v["considerar"]:
                v["manutencao_corretiva"] = st.number_input(
                    "Manutenção corretiva (R$/km)",
                    min_value=0.0,
                    value=float(v["manutencao_corretiva"]),
                    step=0.01,
                    key="v_manut",
                )
                v["pneus"] = st.number_input(
                    "Pneus (R$/km)",
                    min_value=0.0,
                    value=float(v["pneus"]),
                    step=0.01,
                    key="v_pneu",
                )
                v["freios"] = st.number_input(
                    "Freios (R$/km)",
                    min_value=0.0,
                    value=float(v["freios"]),
                    step=0.01,
                    key="v_freio",
                )

        with st.expander("Custos Fixos Mensais", expanded=False):
            f = cfg["custos_fixos"]
            campos_fixos = [
                ("seguro", "Seguro"),
                ("ipva_mensal", "IPVA (mensal)"),
                ("licenciamento_mensal", "Licenciamento (mensal)"),
                ("mei_das", "DAS MEI"),
                ("internet_celular", "Plano de Internet"),
                ("manutencao_preventiva_mensal", "Manutenção Preventiva"),
                ("lavagem_estetica", "Lavagem / Estética"),
                ("outros", "Outros"),
            ]
            l1, l2 = st.columns([2, 1.2])
            with l1:
                f["considerar"] = st.checkbox(
                    "Considerar custos fixos", value=bool(f["considerar"]), key="f_cons"
                )
            with l2:
                if st.button("🔄 Restaurar valores sugeridos", key="restaurar_fixos"):
                    f["considerar"] = True
                    for k, _ in campos_fixos:
                        f[k] = cfg_default["custos_fixos"][k]
                    st.session_state["_sync_widgets_force"] = True
                    st.rerun()
            if f["considerar"]:
                col_a, col_b = st.columns(2)
                for idx, (k, label) in enumerate(campos_fixos):
                    col = col_a if idx < 4 else col_b
                    with col:
                        f[k] = st.number_input(
                            label,
                            min_value=0.0,
                            value=float(f[k]),
                            step=10.0,
                            key=f"fixo_{k}",
                        )
                        if k == "outros":
                            st.caption("Inclua qualquer gasto mensal que não esteja listado acima.")

            total_fixos_secao = sum(f[k] for k, _ in campos_fixos) if f["considerar"] else 0.0
            st.markdown("---")
            st.markdown("**Total Custos Fixos**")
            st.markdown(f"**{moeda(total_fixos_secao)}**")

aplicar_widget_state_no_cfg(cfg)
res = calcular_simulacao(cfg)
inds = indicadores_gerais(cfg, res)
custos = custos_consolidados(cfg, res)
rec_cat = receita_por_categoria(cfg, res)
df_sem = tabela_semanal(cfg, res)
df_cen = cenarios_rapidos(cfg)

if aba_ativa == "Resumo":
    st.subheader("Resumo Financeiro Consolidado")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Receita Bruta", moeda(inds["receita_bruta"]))
    nome_receita_uber = (
        "Receita após Comissão"
        if cfg["modelo_financeiro"]["tipo"] == "comissao"
        else "Receita após Passe"
    )
    m2.metric(nome_receita_uber, moeda(inds["receita_apos_uber"]))
    m3.metric("Custos Totais", moeda(inds["custos_operacao"]))
    m4.metric("Lucro Líquido", moeda(inds["lucro"]))

    st.divider()
    st.markdown("**Resumo da Simulação**")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.write(f"Veículo: **{cfg['veiculo']['modelo']}**")
        st.write(
            f"Categoria: **Black {cfg['mix_categoria']['percentual_black']*100:.0f}% / "
            f"Comfort {(1-cfg['mix_categoria']['percentual_black'])*100:.0f}%**"
        )
    with s2:
        if cfg["modelo_financeiro"]["tipo"] == "passe":
            st.write(
                f"Modelo: **Passe para Motoristas ({cfg['modelo_financeiro']['passe']['plano_selecionado']})**"
            )
        else:
            st.write("Modelo: **Comissão**")
        st.write(
            f"Jornada: **{cfg['jornada']['horas_online_dia']:.1f}h/dia | "
            f"{cfg['jornada']['dias_semana']:.0f} dias/semana**"
        )
    with s3:
        st.write(
            f"KM/Mês: **{res['km_total_mes']:.0f}** | Horas/Mês: **{res['horas_mes']:.0f}**"
        )
        st.write(f"Custo/KM: **{moeda(inds['custo_km'])}**")
        st.write(
            f"Consumo: **{cfg['veiculo']['consumo_kwh_por_km']:.3f} kWh/km** | "
            f"Energia: **{res['kwh_mes']:.0f} kWh/mês**"
        )
        st.write(
            f"Recargas/dia: **{res['recargas_dia']:.0f}** | "
            f"Disponibilidade: **{res['disponibilidade_operacional']*100:.1f}%**"
        )

    st.divider()
    st.markdown("**Dados do Veículo e Operação**")
    df_veiculo_resumo = pd.DataFrame(
        [
            {"Indicador": "Modelo", "Valor": cfg["veiculo"]["modelo"]},
            {"Indicador": "Tipo", "Valor": cfg["veiculo"]["propulsao"]},
            {"Indicador": "Valor do veículo", "Valor": moeda(cfg["veiculo"]["preco_veiculo"])},
            {"Indicador": "Bateria", "Valor": f"{cfg['veiculo']['bateria_kwh']:.1f} kWh"},
            {
                "Indicador": "Autonomia oficial",
                "Valor": f"{cfg['veiculo']['autonomia_oficial_km']:.0f} km",
            },
            {
                "Indicador": "Autonomia operacional",
                "Valor": f"{res['operacao']['autonomia_operacional_km']:.0f} km",
            },
            {"Indicador": "Autonomia útil", "Valor": f"{res['autonomia_util_km']:.0f} km"},
            {
                "Indicador": "Reserva bateria",
                "Valor": percentual(res["operacao"]["reserva_bateria_percentual"]),
            },
            {
                "Indicador": "Tempo recarga",
                "Valor": f"{cfg['veiculo']['tempo_medio_recarga_min']:.0f} min",
            },
            {"Indicador": "Recargas/dia", "Valor": f"{res['recargas_dia']:.0f}"},
            {"Indicador": "Recargas/mês", "Valor": f"{res['recargas_mes']:.0f}"},
            {
                "Indicador": "Tempo parado/dia",
                "Valor": f"{res['operacao']['tempo_recarga_horas_dia']*60:.0f} min",
            },
            {
                "Indicador": "Tempo parado/mês",
                "Valor": f"{res['horas_perdidas_recarga_mes']:.1f} h",
            },
            {
                "Indicador": "Disponibilidade operacional",
                "Valor": percentual(res["disponibilidade_operacional"]),
            },
            {"Indicador": "Energia elétrica", "Valor": f"{res['kwh_mes']:.0f} kWh"},
            {"Indicador": "Combustível", "Valor": f"{res['litros_combustivel']:.1f} L"},
            {"Indicador": "Custo energia", "Valor": moeda(res["custo_energia_total"])},
            {"Indicador": "Custo combustível", "Valor": moeda(res["custo_combustivel_total"])},
        ]
    )
    st.dataframe(df_veiculo_resumo, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("**Indicadores Financeiros**")
    label_receita_liquida = (
        "Receita após Comissão"
        if cfg["modelo_financeiro"]["tipo"] == "comissao"
        else "Receita após Passe"
    )
    df_ind = pd.DataFrame(
        {
            "Indicador": [
                "Receita Bruta",
                label_receita_liquida,
                "Custos Totais",
                "Lucro Líquido",
                "Margem Líquida",
                "Lucro/Hora",
                "Receita/Hora",
                "Lucro/Dia",
                "Lucro/Semana",
                "Receita/KM",
                "Custo/KM",
                "Lucro/KM",
                "Horas Produtivas",
                "Horas Perdidas Recarga",
                "KM Produtivo",
                "KM Perdido",
                "Corridas/Mês",
                "Recargas/Mês",
                "Disponibilidade",
            ],
            "Valor": [
                moeda(inds["receita_bruta"]),
                moeda(inds["receita_apos_uber"]),
                moeda(inds["custos_operacao"]),
                moeda(inds["lucro"]),
                percentual(inds["margem_liquida"]),
                moeda(inds["lucro_hora"]),
                moeda(inds["receita_hora"]),
                moeda(inds["lucro_dia"]),
                moeda(inds["lucro_semana"]),
                moeda(inds["receita_km"]),
                moeda(inds["custo_km"]),
                moeda(inds["lucro_km"]),
                f"{res['horas_produtivas_mes']:.1f} h",
                f"{res['horas_perdidas_recarga_mes']:.1f} h",
                f"{res['km_produtivo_mes']:.0f} km",
                f"{res['km_perdido_mes']:.0f} km",
                f"{res['corridas_mes']:.0f}",
                f"{res['recargas_mes']:.0f}",
                percentual(res["disponibilidade_operacional"]),
            ],
        }
    )
    st.dataframe(df_ind, use_container_width=True, hide_index=True)

    if cfg["modelo_financeiro"]["tipo"] == "passe":
        st.markdown("**Indicadores do Passe**")
        info = res["passe_info"]
        df_passe = pd.DataFrame(
            {
                "Indicador": [
                    "Tipo",
                    "Plano",
                    "Valor Unitário",
                    "Quantidade de Passes",
                    "Custo Mensal do Passe",
                ],
                "Valor": [
                    "Passe",
                    str(info["plano"]),
                    moeda(info["valor_unitario"]),
                    f"{info['quantidade_passes']}",
                    moeda(info["custo_mensal"]),
                ],
            }
        )
        st.dataframe(df_passe, use_container_width=True, hide_index=True)

    st.markdown("**Indicadores Financeiros (em breve)**")
    df_ind_fut = pd.DataFrame(
        {
            "Indicador": [
                "ROI",
                "Payback",
                "Break-even",
                "Receita mínima mensal",
                "Horas mínimas por dia",
                "KM mínimos por mês",
            ],
            "Valor": ["Em breve", "Em breve", "Em breve", "Em breve", "Em breve", "Em breve"],
        }
    )
    st.dataframe(df_ind_fut, use_container_width=True, hide_index=True)

    st.markdown("**Receita por Categoria**")
    df_cat = pd.DataFrame(
        [
            {
                "Categoria": "Black",
                "Receita": rec_cat["black"],
                "%": percentual(div(rec_cat["black"], rec_cat["total"])),
            },
            {
                "Categoria": "Comfort",
                "Receita": rec_cat["comfort"],
                "%": percentual(div(rec_cat["comfort"], rec_cat["total"])),
            },
            {"Categoria": "Total", "Receita": rec_cat["total"], "%": "100%"},
        ]
    )
    st.dataframe(
        formatar_df_moeda(df_cat, ["Receita"]),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("**Custos Consolidados**")
    df_custos = pd.DataFrame(
        [
            {"Grupo": "Energia", "Valor": custos["energia"]},
            {"Grupo": "Combustível", "Valor": custos["combustivel"]},
            {"Grupo": "Taxas/Passe", "Valor": custos["plataforma"]},
            {"Grupo": "Depreciação", "Valor": custos["depreciacao"]},
            {"Grupo": "Custos Variáveis", "Valor": custos["variaveis_sem_energia_dep"]},
            {"Grupo": "Custos Fixos", "Valor": custos["fixos"]},
            {"Grupo": "Custos Operacionais", "Valor": custos["total_operacional"]},
            {"Grupo": "Total Geral", "Valor": custos["total_geral"]},
        ]
    )
    st.dataframe(
        formatar_df_moeda(df_custos, ["Valor"]),
        use_container_width=True,
        hide_index=True,
    )

if aba_ativa == "Semanal":
    st.subheader("Distribuição Semanal")
    st.dataframe(
        formatar_df_moeda(df_sem, ["Receita", "Custos", "Lucro"]),
        use_container_width=True,
        hide_index=True,
    )
    fig_sem = px.bar(
        df_sem,
        x="Semana",
        y=["Receita", "Custos", "Lucro"],
        barmode="group",
        title="Receita x Custos x Lucro por Semana",
    )
    st.plotly_chart(fig_sem, use_container_width=True)

    st.markdown("**Indicadores**")
    ind_sem = pd.DataFrame(
        {
            "Indicador": [
                "Receita Média/Semana",
                "Lucro Médio/Semana",
                "KM Médio/Semana",
                "Horas/Semana",
            ],
            "Valor": [
                moeda(df_sem["Receita"].mean()) if len(df_sem) else moeda(0),
                moeda(df_sem["Lucro"].mean()) if len(df_sem) else moeda(0),
                f"{df_sem['KM'].mean():.0f}" if len(df_sem) else "0",
                f"{df_sem['Horas'].mean():.1f}" if len(df_sem) else "0",
            ],
        }
    )
    st.dataframe(ind_sem, use_container_width=True, hide_index=True)

if aba_ativa == "Cenários":
    st.subheader("Comparação de Cenários")
    df_show = df_cen.copy()
    df_show["Margem"] = df_show["Margem"].map(percentual)
    st.dataframe(
        formatar_df_moeda(df_show, ["Receita", "Custos", "Lucro"]),
        use_container_width=True,
        hide_index=True,
    )

    melt = df_cen.melt(
        id_vars=["Cenário"],
        value_vars=["Receita", "Custos", "Lucro"],
        var_name="Métrica",
        value_name="Valor",
    )
    fig_cen = px.bar(
        melt,
        x="Cenário",
        y="Valor",
        color="Métrica",
        barmode="group",
        title="Receita x Custos x Lucro entre cenários",
    )
    st.plotly_chart(fig_cen, use_container_width=True)

    melhor = df_cen.loc[df_cen["Lucro"].idxmax()]
    pior = df_cen.loc[df_cen["Lucro"].idxmin()]
    dif_pct = div(melhor["Lucro"] - pior["Lucro"], abs(pior["Lucro"]))
    df_ind_cen = pd.DataFrame(
        {
            "Indicador": ["Melhor Cenário", "Pior Cenário", "Diferença (%)"],
            "Valor": [melhor["Cenário"], pior["Cenário"], percentual(dif_pct)],
        }
    )
    st.dataframe(df_ind_cen, use_container_width=True, hide_index=True)

if aba_ativa == "Dashboard":
    st.subheader("Dashboard Visual")

    d1, d2 = st.columns(2)
    with d1:
        taxas_ou_passe = res["cenario_misto"]["taxas_ou_passe_mes"]
        fig_receita_mensal = go.Figure(
            go.Waterfall(
                name="Receita Mensal",
                orientation="v",
                measure=["relative", "relative", "total"],
                x=["Receita Bruta", "Taxas/Passe", "Receita Líquida"],
                y=[inds["receita_bruta"], -taxas_ou_passe, 0],
                text=[
                    moeda(inds["receita_bruta"]),
                    moeda(-taxas_ou_passe),
                    moeda(inds["receita_apos_uber"]),
                ],
            )
        )
        fig_receita_mensal.update_layout(title="Receita Mensal", yaxis_title="R$")
        st.plotly_chart(fig_receita_mensal, use_container_width=True)

    with d2:
        df_dist = pd.DataFrame(
            {
                "Grupo": [
                    "Energia",
                    "Combustível",
                    "Taxas/Passe",
                    "Depreciação",
                    "Fixos",
                    "Variáveis",
                ],
                "Valor": [
                    custos["energia"],
                    custos["combustivel"],
                    custos["plataforma"],
                    custos["depreciacao"],
                    custos["fixos"],
                    custos["variaveis_sem_energia_dep"],
                ],
            }
        )
        fig_dist = px.pie(
            df_dist,
            names="Grupo",
            values="Valor",
            hole=0.45,
            title="Distribuição de Custos",
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    d3, d4 = st.columns(2)
    with d3:
        km_total = res["km_total_mes"]
        comp = res["componentes_km"]
        df_var = pd.DataFrame(
            {
                "Componente": ["Energia", "Combustível", "Pneus", "Freios", "Manutenção", "Depreciação"],
                "Valor": [
                    comp["energia"] * km_total,
                    comp.get("combustivel", 0.0) * km_total,
                    comp["pneus"] * km_total,
                    comp["freios"] * km_total,
                    comp["manutencao_corretiva"] * km_total,
                    comp["depreciacao"] * km_total,
                ],
            }
        )
        fig_var = px.pie(
            df_var,
            names="Componente",
            values="Valor",
            hole=0.45,
            title="Custos Variáveis",
        )
        st.plotly_chart(fig_var, use_container_width=True)

    with d4:
        df_rc = pd.DataFrame(
            {
                "Categoria": ["Black", "Comfort"],
                "Receita": [rec_cat["black"], rec_cat["comfort"]],
            }
        )
        fig_rc = px.pie(
            df_rc,
            names="Categoria",
            values="Receita",
            hole=0.45,
            title="Receita por Categoria",
        )
        st.plotly_chart(fig_rc, use_container_width=True)

    d5, d6 = st.columns(2)
    with d5:
        nome_receita_liquida = (
            "Receita após Comissão"
            if cfg["modelo_financeiro"]["tipo"] == "comissao"
            else "Receita após Passe"
        )
        df_rx = pd.DataFrame(
            {
                "Item": [nome_receita_liquida, "Custos", "Lucro"],
                "Valor": [inds["receita_apos_uber"], inds["custos_operacao"], inds["lucro"]],
            }
        )
        fig_rx = px.bar(
            df_rx,
            x="Item",
            y="Valor",
            color="Item",
            title="Receita x Custos",
            text_auto=".2s",
        )
        fig_rx.update_layout(showlegend=False, yaxis_title="R$")
        st.plotly_chart(fig_rx, use_container_width=True)

    with d6:
        df_line = df_sem.copy()
        fig_line = px.line(
            df_line,
            x="Semana",
            y=["Receita", "Custos", "Lucro"],
            markers=True,
            title="Evolução Semanal",
        )
        st.plotly_chart(fig_line, use_container_width=True)

    d7, d8 = st.columns(2)
    with d7:
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=max(0.0, inds["margem_liquida"] * 100),
                number={"suffix": "%"},
                title={"text": "Eficiência Operacional (Margem Líquida)"},
                gauge={"axis": {"range": [0, 100]}},
            )
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with d8:
        st.markdown("**KPIs**")
        k1, k2, k3 = st.columns(3)
        k4, k5, k6 = st.columns(3)
        k7, k8, k9 = st.columns(3)
        k1.metric("Receita/Hora", moeda(inds["receita_hora"]))
        k2.metric("Lucro/Hora", moeda(inds["lucro_hora"]))
        k3.metric("Receita/KM", moeda(inds["receita_km"]))
        k4.metric("Lucro/KM", moeda(inds["lucro_km"]))
        k5.metric("Custo/KM", moeda(inds["custo_km"]))
        k6.metric("KM/Mês", f"{res['km_total_mes']:.0f}")
        k7.metric("Horas Produtivas", f"{res['horas_mes']:.0f}")
        k8.metric("Recargas/Mês", f"{res['recargas_mes']:.0f}")
        k9.metric("Disponibilidade", percentual(res["disponibilidade_operacional"]))

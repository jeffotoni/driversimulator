from __future__ import annotations

import argparse
import copy
import math
from typing import Any, Dict, List


def moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}"


def percentual(valor: float) -> str:
    return f"{valor * 100:.1f}%"


def _consumo_por_km(bateria_kwh: float, autonomia_km: float) -> float:
    if autonomia_km <= 0:
        return 0.0
    return bateria_kwh / autonomia_km


def _autonomia_operacional_padrao(modelo: str, propulsao: str, autonomia_oficial: float) -> float:
    autonomia_por_modelo = {
        "BYD Dolphin GS (Tradicional)": 380.0,
        "BYD Dolphin Mini (GL - Entrada)": 250.0,
        "BYD Dolphin Mini (GS - Plus)": 280.0,
        "BYD Dolphin Plus": 330.0,
        "BYD Dolphin Special Edition (SE)": 250.0,
        "BYD Han": 315.0,
        "BYD Seal": 372.0,
        "BYD Tan": 430.0,
        "BYD Yuan Plus": 294.0,
        "BYD Yuan Pro": 250.0,
    }
    if propulsao == "PHEV":
        return autonomia_oficial
    return autonomia_por_modelo.get(modelo, autonomia_oficial)


def _tempo_recarga_padrao(propulsao: str, bateria_kwh: float) -> float:
    if propulsao == "PHEV":
        return 25.0
    if bateria_kwh >= 80:
        return 50.0
    if bateria_kwh >= 55:
        return 42.0
    return 38.0


def catalogo_veiculos() -> Dict[str, Dict[str, Any]]:
    vida_util_por_modelo_km = {
        "BYD Atto 2": 400000.0,
        "BYD Dolphin GS (Tradicional)": 400000.0,
        "BYD Dolphin Mini (GL - Entrada)": 350000.0,
        "BYD Dolphin Mini (GS - Plus)": 350000.0,
        "BYD Dolphin Plus": 450000.0,
        "BYD Dolphin Special Edition (SE)": 450000.0,
        "BYD Han": 600000.0,
        "BYD King (GL/GS)": 450000.0,
        "BYD Seal": 600000.0,
        "BYD Shark": 500000.0,
        "BYD Song Plus": 500000.0,
        "BYD Song Pro (GL/GS)": 450000.0,
        "BYD Tan": 600000.0,
        "BYD Yuan Plus": 500000.0,
        "BYD Yuan Pro": 450000.0,
    }

    veiculos: List[Dict[str, Any]] = [
        {
            "modelo": "BYD Atto 2",
            "propulsao": "PHEV",
            "bateria_kwh": 12.9,
            "potencia_cv": 218,
            "autonomia_eletrica_km": 70.0,
            "autonomia_total_km": 1000.0,
            "consumo_combustivel_default_km_l": 18.0,
            "combustivel_default_litro": 6.00,
            "preco_veiculo": 149990.0,
            "seguro_mensal_sugerido": 470.0,
            "depreciacao_km_sugerida": 0.28,
        },
        {
            "modelo": "BYD Dolphin GS (Tradicional)",
            "propulsao": "BEV",
            "bateria_kwh": 44.9,
            "potencia_cv": 95,
            "autonomia_eletrica_km": 291.0,
            "autonomia_total_km": None,
            "preco_veiculo": 149990.0,
            "seguro_mensal_sugerido": 450.0,
            "depreciacao_km_sugerida": 0.30,
        },
        {
            "modelo": "BYD Dolphin Mini (GL - Entrada)",
            "propulsao": "BEV",
            "bateria_kwh": 30.0,
            "potencia_cv": 75,
            "autonomia_eletrica_km": 250.0,
            "autonomia_total_km": None,
            "preco_veiculo": 109990.0,
            "seguro_mensal_sugerido": 380.0,
            "depreciacao_km_sugerida": 0.22,
        },
        {
            "modelo": "BYD Dolphin Mini (GS - Plus)",
            "propulsao": "BEV",
            "bateria_kwh": 38.0,
            "potencia_cv": 75,
            "autonomia_eletrica_km": 280.0,
            "autonomia_total_km": None,
            "preco_veiculo": 119800.0,
            "seguro_mensal_sugerido": 400.0,
            "depreciacao_km_sugerida": 0.24,
        },
        {
            "modelo": "BYD Dolphin Plus",
            "propulsao": "BEV",
            "bateria_kwh": 60.4,
            "potencia_cv": 204,
            "autonomia_eletrica_km": 330.0,
            "autonomia_total_km": None,
            "preco_veiculo": 184800.0,
            "seguro_mensal_sugerido": 560.0,
            "depreciacao_km_sugerida": 0.35,
        },
        {
            "modelo": "BYD Dolphin Special Edition (SE)",
            "propulsao": "BEV",
            "bateria_kwh": 44.9,
            "potencia_cv": 177,
            "autonomia_eletrica_km": 250.0,
            "autonomia_total_km": None,
            "preco_veiculo": 176800.0,
            "seguro_mensal_sugerido": 520.0,
            "depreciacao_km_sugerida": 0.34,
        },
        {
            "modelo": "BYD Han",
            "propulsao": "BEV",
            "bateria_kwh": 85.4,
            "potencia_cv": 517,
            "autonomia_eletrica_km": 315.0,
            "autonomia_total_km": None,
            "preco_veiculo": 540000.0,
            "seguro_mensal_sugerido": 1020.0,
            "depreciacao_km_sugerida": 0.75,
        },
        {
            "modelo": "BYD King (GL/GS)",
            "propulsao": "PHEV",
            "bateria_kwh": 13.3,
            "potencia_cv": 220,
            "autonomia_eletrica_km": 56.0,
            "autonomia_total_km": 1200.0,
            "consumo_combustivel_default_km_l": 22.0,
            "combustivel_default_litro": 6.00,
            "preco_veiculo": 175990.0,
            "seguro_mensal_sugerido": 540.0,
            "depreciacao_km_sugerida": 0.33,
        },
        {
            "modelo": "BYD Seal",
            "propulsao": "BEV",
            "bateria_kwh": 82.5,
            "potencia_cv": 531,
            "autonomia_eletrica_km": 372.0,
            "autonomia_total_km": None,
            "preco_veiculo": 299990.0,
            "seguro_mensal_sugerido": 760.0,
            "depreciacao_km_sugerida": 0.50,
        },
        {
            "modelo": "BYD Shark",
            "propulsao": "PHEV",
            "bateria_kwh": 29.6,
            "potencia_cv": 437,
            "autonomia_eletrica_km": 57.0,
            "autonomia_total_km": 840.0,
            "consumo_combustivel_default_km_l": 11.0,
            "combustivel_default_litro": 6.00,
            "preco_veiculo": 311168.0,
            "seguro_mensal_sugerido": 780.0,
            "depreciacao_km_sugerida": 0.52,
        },
        {
            "modelo": "BYD Song Plus",
            "propulsao": "PHEV",
            "bateria_kwh": 18.3,
            "potencia_cv": 235,
            "autonomia_eletrica_km": 68.0,
            "autonomia_total_km": 1100.0,
            "consumo_combustivel_default_km_l": 20.0,
            "combustivel_default_litro": 6.00,
            "preco_veiculo": 249990.0,
            "seguro_mensal_sugerido": 650.0,
            "depreciacao_km_sugerida": 0.42,
        },
        {
            "modelo": "BYD Song Pro (GL/GS)",
            "propulsao": "PHEV",
            "bateria_kwh": 15.6,
            "potencia_cv": 223,
            "autonomia_eletrica_km": 58.5,
            "autonomia_total_km": 1100.0,
            "consumo_combustivel_default_km_l": 19.0,
            "combustivel_default_litro": 6.00,
            "preco_veiculo": 161490.0,
            "seguro_mensal_sugerido": 520.0,
            "depreciacao_km_sugerida": 0.31,
        },
        {
            "modelo": "BYD Tan",
            "propulsao": "BEV",
            "bateria_kwh": 108.8,
            "potencia_cv": 517,
            "autonomia_eletrica_km": 430.0,
            "autonomia_total_km": None,
            "preco_veiculo": 520000.0,
            "seguro_mensal_sugerido": 980.0,
            "depreciacao_km_sugerida": 0.70,
        },
        {
            "modelo": "BYD Yuan Plus",
            "propulsao": "BEV",
            "bateria_kwh": 60.5,
            "potencia_cv": 204,
            "autonomia_eletrica_km": 294.0,
            "autonomia_total_km": None,
            "preco_veiculo": 235990.0,
            "seguro_mensal_sugerido": 620.0,
            "depreciacao_km_sugerida": 0.40,
        },
        {
            "modelo": "BYD Yuan Pro",
            "propulsao": "BEV",
            "bateria_kwh": 45.1,
            "potencia_cv": 177,
            "autonomia_eletrica_km": 250.0,
            "autonomia_total_km": None,
            "preco_veiculo": 199990.0,
            "seguro_mensal_sugerido": 580.0,
            "depreciacao_km_sugerida": 0.37,
        },
    ]

    out: Dict[str, Dict[str, Any]] = {}
    for v in veiculos:
        item = copy.deepcopy(v)
        item["vida_util_km"] = float(vida_util_por_modelo_km.get(item["modelo"], 400000.0))
        item["autonomia_oficial_km"] = item["autonomia_eletrica_km"]
        if item["propulsao"] == "PHEV" and item.get("autonomia_total_km"):
            item["autonomia_operacional_km"] = item["autonomia_total_km"]
        else:
            item["autonomia_operacional_km"] = _autonomia_operacional_padrao(
                item["modelo"], item["propulsao"], item["autonomia_eletrica_km"]
            )
        item["reserva_bateria_percentual"] = 0.15
        item["tempo_medio_recarga_min"] = _tempo_recarga_padrao(
            item["propulsao"], item["bateria_kwh"]
        )
        item["consumo_combustivel_km_l"] = (
            float(item.get("consumo_combustivel_default_km_l", 0.0))
            if item["propulsao"] == "PHEV"
            else 0.0
        )
        item["combustivel_default_litro"] = (
            float(item.get("combustivel_default_litro", 6.0))
            if item["propulsao"] == "PHEV"
            else 0.0
        )
        item["capacidade_tanque_l"] = 45.0 if item["propulsao"] == "PHEV" else 0.0
        item["consumo_kwh_por_km"] = _consumo_por_km(
            item["bateria_kwh"], item["autonomia_eletrica_km"]
        )
        out[item["modelo"]] = item
    return out


def modelos_veiculo_disponiveis() -> List[str]:
    return list(catalogo_veiculos().keys())


def ficha_veiculo(modelo: str) -> Dict[str, Any]:
    catalogo = catalogo_veiculos()
    if modelo not in catalogo:
        raise ValueError(f"Veículo não encontrado no catálogo: {modelo}")
    return copy.deepcopy(catalogo[modelo])


def aplicar_veiculo_no_config(
    cfg: Dict[str, Any], modelo: str, atualizar_custos_sugeridos: bool = True
) -> None:
    ficha = ficha_veiculo(modelo)
    cfg["veiculo"] = ficha
    if ficha["propulsao"] == "PHEV":
        cfg["combustivel"]["preco_litro"] = float(ficha.get("combustivel_default_litro", 6.0))
    if atualizar_custos_sugeridos:
        cfg["depreciacao"]["valor_km"] = ficha["depreciacao_km_sugerida"]
        cfg["custos_fixos"]["seguro"] = ficha["seguro_mensal_sugerido"]


def config_padrao() -> Dict[str, Any]:
    cfg: Dict[str, Any] = {
        "veiculo": {},
        "modelo_financeiro": {
            "tipo": "passe",  # passe | comissao
            "comissao": {
                "mesma_para_todas": True,
                "black": {"percentual": 0.25, "fixa_por_corrida": 0.0},
                "comfort": {"percentual": 0.25, "fixa_por_corrida": 0.0},
            },
            "passe": {"plano_24h": 35.0, "plano_72h": 97.0, "plano_selecionado": "24h"},
        },
        "tarifas": {
            "black": {
                "tarifa_base": 5.00,
                "valor_km": 2.35,
                "valor_minuto": 0.40,
                "multiplicador_dinamico": 1.0,
                "bonus_por_corrida": 0.0,
                "taxa_plataforma_percentual": 0.00,
                "taxa_plataforma_fixa_por_corrida": 0.0,
            },
            "comfort": {
                "tarifa_base": 3.50,
                "valor_km": 1.65,
                "valor_minuto": 0.28,
                "multiplicador_dinamico": 1.0,
                "bonus_por_corrida": 0.0,
                "taxa_plataforma_percentual": 0.00,
                "taxa_plataforma_fixa_por_corrida": 0.0,
            },
        },
        "jornada": {
            "horas_online_dia": 10.0,
            "dias_semana": 6.0,
            "semanas_mes": 4.3,
            "km_rodados_hora": 22.0,
            "percentual_km_com_passageiro": 0.65,
            "minutos_corrida_media": 18.0,
            "km_corrida_media": 8.5,
        },
        "mix_categoria": {"percentual_black": 0.60},
        "energia": {
            "considerar": True,
            "possui_solar": False,
            "custo_kwh_unico": 1.50,
            "custo_kwh_casa": 1.00,
            "custo_kwh_rede": 1.50,
            "producao_fotovoltaico_kwh_mes": 1000.0,
            "percentual_solar_usado": 0.80,
        },
        "combustivel": {
            "considerar": False,
            "preco_litro": 6.00,
            "percentual_eletrico_phev": 0.70,
        },
        "custos_fixos": {
            "considerar": False,
            "seguro": 450.0,
            "ipva_mensal": 620.0,
            "licenciamento_mensal": 120.0,
            "mei_das": 72.0,
            "manutencao_preventiva_mensal": 200.0,
            "internet_celular": 80.0,
            "lavagem_estetica": 200.0,
            "outros": 100.0,
        },
        "custos_variaveis_km": {
            "considerar": False,
            "manutencao_corretiva": 0.05,
            "pneus": 0.08,
            "freios": 0.03,
        },
        "depreciacao": {"considerar": False, "valor_km": 0.30},
    }
    aplicar_veiculo_no_config(cfg, "BYD Dolphin GS (Tradicional)", atualizar_custos_sugeridos=True)
    cfg["depreciacao"]["valor_km"] = cfg["veiculo"]["depreciacao_km_sugerida"]
    return cfg


def limitar(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(maximo, valor))


def calcular_info_passe(
    modelo_financeiro: Dict[str, Any], jornada: Dict[str, float]
) -> Dict[str, Any]:
    if modelo_financeiro["tipo"] != "passe":
        return {
            "tipo": "comissao",
            "plano": None,
            "valor_unitario": 0.0,
            "quantidade_passes": 0,
            "dias_trabalhados": jornada["dias_semana"] * jornada["semanas_mes"],
            "custo_mensal": 0.0,
        }

    dias_trabalhados = jornada["dias_semana"] * jornada["semanas_mes"]
    dias_arredondados = math.ceil(dias_trabalhados)
    plano = modelo_financeiro["passe"]["plano_selecionado"]
    if plano == "72h":
        valor_unitario = modelo_financeiro["passe"]["plano_72h"]
        quantidade = math.ceil(dias_arredondados / 3.0)
    else:
        valor_unitario = modelo_financeiro["passe"]["plano_24h"]
        quantidade = dias_arredondados

    return {
        "tipo": "passe",
        "plano": plano,
        "valor_unitario": valor_unitario,
        "quantidade_passes": quantidade,
        "dias_trabalhados": dias_trabalhados,
        "custo_mensal": quantidade * valor_unitario,
    }


def custo_plano_mensal(modelo_financeiro: Dict[str, Any], jornada: Dict[str, float]) -> float:
    info = calcular_info_passe(modelo_financeiro, jornada)
    return info["custo_mensal"]


def calcular_metricas_jornada(jornada: Dict[str, float]) -> Dict[str, float]:
    horas_dia = max(0.0, jornada["horas_online_dia"])
    dias_semana = max(0.0, jornada["dias_semana"])
    semanas_mes = max(0.0, jornada["semanas_mes"])
    km_hora = max(0.0, jornada["km_rodados_hora"])
    km_corrida = max(1e-9, jornada["km_corrida_media"])
    aproveitamento = limitar(jornada["percentual_km_com_passageiro"], 0.0, 1.0)

    km_dia_total = horas_dia * km_hora
    km_mes_total = km_dia_total * dias_semana * semanas_mes
    km_dia_com_passageiro = km_dia_total * aproveitamento
    km_mes_com_passageiro = km_mes_total * aproveitamento
    km_mes_vazio = max(0.0, km_mes_total - km_mes_com_passageiro)

    corridas_dia = km_dia_com_passageiro / km_corrida
    corridas_mes = km_mes_com_passageiro / km_corrida
    horas_mes = horas_dia * dias_semana * semanas_mes
    corridas_hora = corridas_mes / horas_mes if horas_mes > 0 else 0.0

    return {
        "horas_dia": horas_dia,
        "dias_semana": dias_semana,
        "semanas_mes": semanas_mes,
        "horas_mes": horas_mes,
        "km_dia_total": km_dia_total,
        "km_mes_total": km_mes_total,
        "km_dia_com_passageiro": km_dia_com_passageiro,
        "km_mes_com_passageiro": km_mes_com_passageiro,
        "km_mes_vazio": km_mes_vazio,
        "corridas_dia": corridas_dia,
        "corridas_mes": corridas_mes,
        "corridas_hora": corridas_hora,
    }


def calcular_metricas_operacionais(
    jornada: Dict[str, float], veiculo: Dict[str, Any]
) -> Dict[str, float]:
    horas_dia = max(0.0, jornada["horas_online_dia"])
    dias_semana = max(0.0, jornada["dias_semana"])
    semanas_mes = max(0.0, jornada["semanas_mes"])
    km_hora = max(0.0, jornada["km_rodados_hora"])
    km_corrida = max(1e-9, jornada["km_corrida_media"])

    km_planejado_dia = horas_dia * km_hora
    autonomia_operacional = max(0.0, veiculo.get("autonomia_operacional_km", 0.0))
    reserva = limitar(veiculo.get("reserva_bateria_percentual", 0.15), 0.0, 0.95)
    autonomia_util = autonomia_operacional * (1 - reserva)
    if veiculo.get("propulsao") == "PHEV":
        recargas_dia = 0
    elif autonomia_util > 0 and km_planejado_dia > 0:
        recargas_dia = math.ceil(km_planejado_dia / autonomia_util)
    else:
        recargas_dia = 0

    tempo_recarga_horas_dia = recargas_dia * max(
        0.0, veiculo.get("tempo_medio_recarga_min", 0.0)
    ) / 60.0
    disponibilidade = (
        horas_dia / (horas_dia + tempo_recarga_horas_dia)
        if horas_dia > 0
        else 0.0
    )

    km_produtivo_dia = km_planejado_dia * disponibilidade
    horas_produtivas_dia = horas_dia * disponibilidade
    corridas_dia = km_produtivo_dia / km_corrida
    dias_mes = dias_semana * semanas_mes

    return {
        "horas_dia": horas_dia,
        "dias_semana": dias_semana,
        "semanas_mes": semanas_mes,
        "dias_mes": dias_mes,
        "km_planejado_dia": km_planejado_dia,
        "km_planejado_mes": km_planejado_dia * dias_mes,
        "autonomia_operacional_km": autonomia_operacional,
        "reserva_bateria_percentual": reserva,
        "autonomia_util_km": autonomia_util,
        "recargas_dia": float(recargas_dia),
        "recargas_mes": recargas_dia * dias_mes,
        "tempo_recarga_horas_dia": tempo_recarga_horas_dia,
        "tempo_recarga_horas_mes": tempo_recarga_horas_dia * dias_mes,
        "horas_produtivas_dia": horas_produtivas_dia,
        "horas_produtivas_mes": horas_produtivas_dia * dias_mes,
        "disponibilidade_operacional": disponibilidade,
        "km_produtivo_dia": km_produtivo_dia,
        "km_produtivo_mes": km_produtivo_dia * dias_mes,
        "km_perdido_dia": max(0.0, km_planejado_dia - km_produtivo_dia),
        "km_perdido_mes": max(0.0, (km_planejado_dia - km_produtivo_dia) * dias_mes),
        "corridas_dia": corridas_dia,
        "corridas_mes": corridas_dia * dias_mes,
        "corridas_hora": corridas_dia / horas_produtivas_dia if horas_produtivas_dia > 0 else 0.0,
    }


def calcular_receita_categoria(
    categoria: str,
    corridas_mes: float,
    horas_mes: float,
    jornada: Dict[str, float],
    tarifa: Dict[str, float],
    modelo_financeiro: Dict[str, Any],
) -> Dict[str, float]:
    corridas_mes = max(0.0, corridas_mes)
    corridas_por_hora = corridas_mes / horas_mes if horas_mes > 0 else 0.0

    receita_base_corrida = (
        tarifa["tarifa_base"]
        + tarifa["valor_km"] * jornada["km_corrida_media"]
        + tarifa["valor_minuto"] * jornada["minutos_corrida_media"]
    )

    multiplicador = max(0.0, tarifa["multiplicador_dinamico"])
    bonus = tarifa["bonus_por_corrida"]
    receita_bruta_corrida = receita_base_corrida * multiplicador + bonus

    taxa_plataforma_corrida = (
        receita_bruta_corrida * tarifa["taxa_plataforma_percentual"]
        + tarifa["taxa_plataforma_fixa_por_corrida"]
    )

    comissao_cfg = modelo_financeiro["comissao"][categoria]
    comissao_corrida = (
        receita_bruta_corrida * comissao_cfg["percentual"] + comissao_cfg["fixa_por_corrida"]
    )
    desconto_teorico_corrida = comissao_corrida + taxa_plataforma_corrida

    if modelo_financeiro["tipo"] == "passe":
        # No modelo Passe, qualquer taxa por corrida é estornada no fechamento.
        desconto_efetivo_corrida = 0.0
        estorno_corrida = desconto_teorico_corrida
    else:
        desconto_efetivo_corrida = desconto_teorico_corrida
        estorno_corrida = 0.0

    receita_liquida_corrida = receita_bruta_corrida - desconto_efetivo_corrida

    receita_bruta_mes = receita_bruta_corrida * corridas_mes
    desconto_efetivo_mes = desconto_efetivo_corrida * corridas_mes
    receita_liquida_mes = receita_liquida_corrida * corridas_mes
    estorno_mes = estorno_corrida * corridas_mes

    receita_bruta_hora = receita_bruta_mes / horas_mes if horas_mes > 0 else 0.0
    desconto_efetivo_hora = desconto_efetivo_mes / horas_mes if horas_mes > 0 else 0.0
    receita_liquida_hora = receita_liquida_mes / horas_mes if horas_mes > 0 else 0.0
    taxa_efetiva = desconto_efetivo_mes / receita_bruta_mes if receita_bruta_mes > 0 else 0.0

    return {
        "categoria": categoria.upper(),
        "corridas_mes": corridas_mes,
        "corridas_hora": corridas_por_hora,
        "receita_base_corrida": receita_base_corrida,
        "receita_bruta_corrida": receita_bruta_corrida,
        "taxa_plataforma_corrida": taxa_plataforma_corrida,
        "comissao_corrida": comissao_corrida,
        "desconto_teorico_corrida": desconto_teorico_corrida,
        "desconto_efetivo_corrida": desconto_efetivo_corrida,
        "estorno_corrida": estorno_corrida,
        "receita_liquida_corrida": receita_liquida_corrida,
        "receita_bruta_hora": receita_bruta_hora,
        "desconto_efetivo_hora": desconto_efetivo_hora,
        "receita_liquida_hora": receita_liquida_hora,
        "receita_bruta_mes": receita_bruta_mes,
        "desconto_efetivo_mes": desconto_efetivo_mes,
        "receita_liquida_mes": receita_liquida_mes,
        "estorno_mes": estorno_mes,
        "taxa_efetiva": taxa_efetiva,
    }


def calcular_simulacao(cfg: Dict[str, Any]) -> Dict[str, Any]:
    jornada = cfg["jornada"]
    mix_black = limitar(cfg["mix_categoria"]["percentual_black"], 0.0, 1.0)
    veiculo = cfg["veiculo"]
    operacao = calcular_metricas_operacionais(jornada, veiculo)

    horas_trabalhadas_mes = jornada["horas_online_dia"] * jornada["dias_semana"] * jornada["semanas_mes"]
    horas_mes = operacao["horas_produtivas_mes"]
    km_total_mes = operacao["km_produtivo_mes"]
    km_com_passageiro = km_total_mes
    km_vazio = 0.0
    corridas_mes_total = operacao["corridas_mes"]
    corridas_mes_black = corridas_mes_total * mix_black
    corridas_mes_comfort = corridas_mes_total * (1 - mix_black)

    combustivel_cfg = cfg.get("combustivel", {})
    if veiculo["propulsao"] == "PHEV":
        percentual_eletrico = limitar(
            combustivel_cfg.get("percentual_eletrico_phev", 0.70), 0.0, 1.0
        )
    else:
        percentual_eletrico = 1.0
    percentual_combustao = 1.0 - percentual_eletrico

    km_eletrico_mes = km_total_mes * percentual_eletrico
    km_combustao_mes = km_total_mes * percentual_combustao
    consumo_kwh_por_km = veiculo["consumo_kwh_por_km"]
    kwh_mes = km_eletrico_mes * consumo_kwh_por_km
    energia_cfg = cfg["energia"]

    custo_energia_total = 0.0
    kwh_solar_usado = 0.0
    kwh_rede = 0.0
    if energia_cfg["considerar"]:
        if energia_cfg["possui_solar"]:
            pct_solar = limitar(energia_cfg["percentual_solar_usado"], 0.0, 1.0)
            kwh_solar_teorico = kwh_mes * pct_solar
            kwh_solar_disponivel = max(0.0, energia_cfg["producao_fotovoltaico_kwh_mes"])
            kwh_solar_usado = min(kwh_solar_teorico, kwh_solar_disponivel)
            kwh_rede = max(0.0, kwh_mes - kwh_solar_usado)
            custo_energia_total = (
                kwh_solar_usado * energia_cfg["custo_kwh_casa"] + kwh_rede * energia_cfg["custo_kwh_rede"]
            )
        else:
            kwh_rede = kwh_mes
            custo_publico = energia_cfg.get("custo_kwh_rede", energia_cfg.get("custo_kwh_unico", 0.0))
            custo_energia_total = kwh_mes * custo_publico

    custo_energia_por_km = custo_energia_total / km_total_mes if km_total_mes > 0 else 0.0
    consumo_combustivel = max(0.0, veiculo.get("consumo_combustivel_km_l", 0.0))
    litros_combustivel = (
        km_combustao_mes / consumo_combustivel
        if consumo_combustivel > 0 and combustivel_cfg.get("considerar", True)
        else 0.0
    )
    custo_combustivel_total = litros_combustivel * combustivel_cfg.get("preco_litro", 0.0)
    custo_combustivel_por_km = custo_combustivel_total / km_total_mes if km_total_mes > 0 else 0.0

    receita_black = calcular_receita_categoria(
        "black",
        corridas_mes_black,
        horas_mes,
        jornada,
        cfg["tarifas"]["black"],
        cfg["modelo_financeiro"],
    )
    receita_comfort = calcular_receita_categoria(
        "comfort",
        corridas_mes_comfort,
        horas_mes,
        jornada,
        cfg["tarifas"]["comfort"],
        cfg["modelo_financeiro"],
    )

    receita_bruta_mes = receita_black["receita_bruta_mes"] + receita_comfort["receita_bruta_mes"]
    desconto_corridas_mes = (
        receita_black["desconto_efetivo_mes"] + receita_comfort["desconto_efetivo_mes"]
    )
    estorno_corridas_mes = receita_black["estorno_mes"] + receita_comfort["estorno_mes"]
    receita_liquida_app_mes = (
        receita_black["receita_liquida_mes"] + receita_comfort["receita_liquida_mes"]
    )

    passe_info = calcular_info_passe(cfg["modelo_financeiro"], jornada)
    custo_plano = passe_info["custo_mensal"]
    taxas_ou_passe_mes = (
        desconto_corridas_mes if cfg["modelo_financeiro"]["tipo"] == "comissao" else custo_plano
    )
    receita_liquida_mes = receita_bruta_mes - taxas_ou_passe_mes
    cenario_misto = {
        "receita_bruta_mes": receita_bruta_mes,
        "desconto_efetivo_mes": desconto_corridas_mes,
        "estorno_mes": estorno_corridas_mes,
        "receita_liquida_app_mes": receita_liquida_app_mes,
        "custo_passe_mes": custo_plano,
        "taxas_ou_passe_mes": taxas_ou_passe_mes,
        "receita_liquida_mes": receita_liquida_mes,
    }
    cenario_misto["taxa_efetiva"] = (
        cenario_misto["taxas_ou_passe_mes"] / cenario_misto["receita_bruta_mes"]
        if cenario_misto["receita_bruta_mes"] > 0
        else 0.0
    )

    # Custos variáveis
    var_cfg = cfg["custos_variaveis_km"]
    dep_cfg = cfg["depreciacao"]
    custo_manutencao_corretiva = (
        var_cfg["manutencao_corretiva"] * km_total_mes if var_cfg["considerar"] else 0.0
    )
    custo_pneus = var_cfg["pneus"] * km_total_mes if var_cfg["considerar"] else 0.0
    custo_freios = var_cfg["freios"] * km_total_mes if var_cfg["considerar"] else 0.0
    custo_depreciacao_total = dep_cfg["valor_km"] * km_total_mes if dep_cfg["considerar"] else 0.0

    componentes_km = {
        "energia": custo_energia_por_km if energia_cfg["considerar"] else 0.0,
        "combustivel": custo_combustivel_por_km,
        "manutencao_corretiva": var_cfg["manutencao_corretiva"] if var_cfg["considerar"] else 0.0,
        "depreciacao": dep_cfg["valor_km"] if dep_cfg["considerar"] else 0.0,
        "pneus": var_cfg["pneus"] if var_cfg["considerar"] else 0.0,
        "freios": var_cfg["freios"] if var_cfg["considerar"] else 0.0,
    }
    custo_variavel_total = (
        custo_energia_total
        + custo_combustivel_total
        + custo_depreciacao_total
        + custo_pneus
        + custo_freios
        + custo_manutencao_corretiva
    )
    custo_total_por_km = custo_variavel_total / km_total_mes if km_total_mes > 0 else 0.0

    fixos_cfg = cfg["custos_fixos"]
    custo_fixo_total = 0.0
    if fixos_cfg["considerar"]:
        for chave, valor in fixos_cfg.items():
            if chave != "considerar":
                custo_fixo_total += valor

    custo_total_mes = custo_fixo_total + custo_variavel_total

    lucro_liquido = cenario_misto["receita_liquida_mes"] - custo_total_mes
    lucro_hora = lucro_liquido / horas_mes if horas_mes > 0 else 0.0
    margem_liquida = (
        lucro_liquido / cenario_misto["receita_bruta_mes"]
        if cenario_misto["receita_bruta_mes"] > 0
        else 0.0
    )

    return {
        "modelo_financeiro": cfg["modelo_financeiro"]["tipo"],
        "veiculo": veiculo,
        "operacao": operacao,
        "horas_trabalhadas_mes": horas_trabalhadas_mes,
        "horas_mes": horas_mes,
        "horas_produtivas_mes": horas_mes,
        "horas_perdidas_recarga_mes": operacao["tempo_recarga_horas_mes"],
        "disponibilidade_operacional": operacao["disponibilidade_operacional"],
        "recargas_dia": operacao["recargas_dia"],
        "recargas_mes": operacao["recargas_mes"],
        "autonomia_util_km": operacao["autonomia_util_km"],
        "km_dia": operacao["km_produtivo_dia"],
        "km_planejado_mes": operacao["km_planejado_mes"],
        "km_produtivo_mes": km_total_mes,
        "km_perdido_mes": operacao["km_perdido_mes"],
        "km_total_mes": km_total_mes,
        "km_com_passageiro": km_com_passageiro,
        "km_vazio": km_vazio,
        "corridas_dia": operacao["corridas_dia"],
        "corridas_mes": corridas_mes_total,
        "corridas_black_mes": corridas_mes_black,
        "corridas_comfort_mes": corridas_mes_comfort,
        "km_eletrico_mes": km_eletrico_mes,
        "km_combustao_mes": km_combustao_mes,
        "kwh_mes": kwh_mes,
        "kwh_solar_usado": kwh_solar_usado,
        "kwh_rede": kwh_rede,
        "custo_energia_total": custo_energia_total,
        "litros_combustivel": litros_combustivel,
        "custo_combustivel_total": custo_combustivel_total,
        "custo_manutencao_corretiva_total": custo_manutencao_corretiva,
        "custo_pneus_total": custo_pneus,
        "custo_freios_total": custo_freios,
        "custo_depreciacao_total": custo_depreciacao_total,
        "componentes_km": componentes_km,
        "custo_total_por_km": custo_total_por_km,
        "receita_black": receita_black,
        "receita_comfort": receita_comfort,
        "cenario_misto": cenario_misto,
        "passe_info": passe_info,
        "custo_fixo_total": custo_fixo_total,
        "custo_plano": custo_plano,
        "taxas_ou_passe_mes": taxas_ou_passe_mes,
        "custo_variavel_total": custo_variavel_total,
        "custo_total_mes": custo_total_mes,
        "lucro_liquido": lucro_liquido,
        "lucro_hora": lucro_hora,
        "margem_liquida": margem_liquida,
    }


def aplicar_overrides(cfg: Dict[str, Any], args: argparse.Namespace) -> None:
    if args.veiculo:
        aplicar_veiculo_no_config(cfg, args.veiculo, atualizar_custos_sugeridos=True)
        cfg["depreciacao"]["valor_km"] = cfg["veiculo"]["depreciacao_km_sugerida"]
    if args.modelo_financeiro:
        cfg["modelo_financeiro"]["tipo"] = args.modelo_financeiro
    if args.plano:
        cfg["modelo_financeiro"]["passe"]["plano_selecionado"] = args.plano
    if args.mix_black is not None:
        cfg["mix_categoria"]["percentual_black"] = limitar(args.mix_black / 100.0, 0.0, 1.0)
    if args.comissao_black is not None:
        cfg["modelo_financeiro"]["comissao"]["black"]["percentual"] = args.comissao_black / 100.0
    if args.comissao_comfort is not None:
        cfg["modelo_financeiro"]["comissao"]["comfort"]["percentual"] = args.comissao_comfort / 100.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulador financeiro Uber/99 com modelos Comissão e Passe."
    )
    parser.add_argument("--veiculo", choices=modelos_veiculo_disponiveis())
    parser.add_argument("--modelo-financeiro", choices=["comissao", "passe"])
    parser.add_argument("--plano", choices=["24h", "72h"])
    parser.add_argument("--mix-black", type=float, help="Percentual de tempo em Black (0-100)")
    parser.add_argument("--comissao-black", type=float, help="Comissão Black em %%")
    parser.add_argument("--comissao-comfort", type=float, help="Comissão Comfort em %%")
    return parser.parse_args()


def imprimir(cfg: Dict[str, Any], res: Dict[str, Any]) -> None:
    print("=" * 76)
    print("SIMULAÇÃO FINANCEIRA - DRIVER SIMULATOR")
    print("=" * 76)
    print(f"Veículo: {cfg['veiculo']['modelo']} ({cfg['veiculo']['propulsao']})")
    print(
        f"Modelo financeiro: {cfg['modelo_financeiro']['tipo'].upper()} | "
        f"Mix BLACK {cfg['mix_categoria']['percentual_black']*100:.0f}% "
        f"/ COMFORT {(1-cfg['mix_categoria']['percentual_black'])*100:.0f}%"
    )
    if cfg["modelo_financeiro"]["tipo"] == "passe":
        info = res["passe_info"]
        print(
            f"Passe: {info['plano']} | qtd: {info['quantidade_passes']} | "
            f"valor unitário: {moeda(info['valor_unitario'])} | custo mensal: {moeda(res['custo_plano'])} "
            "(sem desconto por corrida)"
        )

    print("\nRESUMO MENSAL")
    print(f"  Receita bruta: {moeda(res['cenario_misto']['receita_bruta_mes'])}")
    print(f"  Taxas/Passe: {moeda(res['cenario_misto']['taxas_ou_passe_mes'])}")
    print(f"  Receita líquida: {moeda(res['cenario_misto']['receita_liquida_mes'])}")
    print(f"  Custos totais: {moeda(res['custo_total_mes'])}")
    print(f"  Lucro líquido: {moeda(res['lucro_liquido'])}")
    print(f"  Lucro por hora: {moeda(res['lucro_hora'])}")
    print(f"  Margem líquida: {percentual(res['margem_liquida'])}")


def main() -> None:
    args = parse_args()
    cfg = config_padrao()
    aplicar_overrides(cfg, args)
    resultado = calcular_simulacao(cfg)
    imprimir(cfg, resultado)


if __name__ == "__main__":
    main()

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           FIXNOW — SIMULAÇÃO DO ALGORITMO DE MATCHING                       ║
║           TCC MBA Engenharia de Dados — FIAP — Lucas Costa                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Simulação standalone do algoritmo de matching da plataforma FixNow.

Gera profissionais fictícios com métricas variadas, executa o algoritmo
e exibe o ranking visual no terminal — ideal para apresentação na banca.

Como rodar:
    python simulation/matching_simulation.py

Ou com especialidade específica:
    python simulation/matching_simulation.py --specialty encanador
"""

import sys
import os
import argparse
import random

# Adiciona o diretório raiz ao path para importar os módulos da aplicação
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.matching_service import (
    MatchingService,
    MatchRequest,
    ProfessionalCandidate,
)

# ── Configuração da simulação ────────────────────────────────────────────────

# Localização simulada do cliente (São Paulo - Av. Paulista)
CLIENT_LAT = -23.5614
CLIENT_LON = -46.6558
CLIENT_SPECIALTY = "eletricista"


# ── Dados fictícios dos profissionais ────────────────────────────────────────

PROFESSIONALS_DATA = [
    {
        "id": "PRO-001",
        "name": "Carlos Mendes",
        "specialty": "eletricista",
        "latitude": -23.5480,   # ~1.5 km do cliente
        "longitude": -46.6388,
        "avg_rating": 4.9,
        "trust_score": 92.0,
        "is_available": True,
        "avg_response_time_min": 3.0,
        "perfil": "Veterano, nota altíssima, muito próximo",
    },
    {
        "id": "PRO-002",
        "name": "Roberto Lima",
        "specialty": "eletricista",
        "latitude": -23.5420,   # ~2.1 km
        "longitude": -46.6280,
        "avg_rating": 4.5,
        "trust_score": 78.0,
        "is_available": True,
        "avg_response_time_min": 8.0,
        "perfil": "Bom profissional, um pouco mais lento",
    },
    {
        "id": "PRO-003",
        "name": "Marcos Oliveira",
        "specialty": "eletricista",
        "latitude": -23.5700,   # ~0.9 km — mais próximo
        "longitude": -46.6500,
        "avg_rating": 3.8,
        "trust_score": 55.0,
        "is_available": True,
        "avg_response_time_min": 5.0,
        "perfil": "Mais próximo, mas avaliação mediana",
    },
    {
        "id": "PRO-004",
        "name": "Fernando Costa",
        "specialty": "eletricista",
        "latitude": -23.6200,   # ~7 km
        "longitude": -46.7000,
        "avg_rating": 5.0,
        "trust_score": 98.0,
        "is_available": True,
        "avg_response_time_min": 2.0,
        "perfil": "Perfeito em tudo, mas mais distante",
    },
    {
        "id": "PRO-005",
        "name": "Paulo Souza",
        "specialty": "eletricista",
        "latitude": -23.5550,   # ~1.1 km
        "longitude": -46.6450,
        "avg_rating": 4.2,
        "trust_score": 68.0,
        "is_available": False,  # INDISPONÍVEL — será filtrado
        "avg_response_time_min": 10.0,
        "perfil": "Próximo, mas OFFLINE — eliminado no filtro",
    },
    {
        "id": "PRO-006",
        "name": "Ana Paula Rodrigues",
        "specialty": "encanador",  # Especialidade diferente — será filtrada
        "latitude": -23.5530,
        "longitude": -46.6430,
        "avg_rating": 4.8,
        "trust_score": 85.0,
        "is_available": True,
        "avg_response_time_min": 4.0,
        "perfil": "Ótima profissional, mas especialidade ERRADA — eliminada",
    },
    {
        "id": "PRO-007",
        "name": "José Santos",
        "specialty": "eletricista",
        "latitude": -23.8000,   # ~27 km — quase no limite
        "longitude": -46.9000,
        "avg_rating": 4.7,
        "trust_score": 80.0,
        "is_available": True,
        "avg_response_time_min": 6.0,
        "perfil": "Bom, mas muito distante",
    },
]


# ── Funções de formatação visual ─────────────────────────────────────────────

def print_header():
    print()
    print("═" * 70)
    print("  FIXNOW — SIMULAÇÃO DO ALGORITMO DE MATCHING")
    print("  TCC MBA Engenharia de Dados — FIAP — Lucas Costa")
    print("═" * 70)


def print_request_info(specialty: str):
    print()
    print("📍 SOLICITAÇÃO DO CLIENTE")
    print(f"   Serviço solicitado : {specialty.upper()}")
    print(f"   Localização        : Av. Paulista, São Paulo - SP")
    print(f"   Coordenadas        : {CLIENT_LAT}, {CLIENT_LON}")
    print(f"   Raio máximo        : 30 km")
    print()


def print_candidates_info(professionals):
    print("👥 PROFISSIONAIS DISPONÍVEIS NA PLATAFORMA")
    print(f"   Total cadastrados  : {len(professionals)}")
    print()
    for p in professionals:
        status = "✅ ONLINE" if p["is_available"] else "🔴 OFFLINE"
        print(f"   [{p['id']}] {p['name']:<22} | {p['specialty']:<12} | {status}")
        print(f"         Perfil: {p['perfil']}")
    print()


def print_filter_step(result):
    print("─" * 70)
    print("🔍 ETAPA 1 — FILTROS ELIMINATÓRIOS")
    print()
    print(f"   Candidatos avaliados    : {result.total_candidates_evaluated}")
    print(f"   Eliminados (filtros)    : {result.total_candidates_filtered}")
    print(f"   Passaram para o ranking : {len(result.ranked_candidates)}")
    print()
    print("   Motivos de eliminação:")
    print("   • Especialidade diferente da solicitada")
    print("   • Profissional offline/indisponível")
    print("   • Fora do raio de atendimento (> 30 km)")
    print()


def stars(rating: float) -> str:
    full = int(rating)
    return "★" * full + "☆" * (5 - full)


def trust_badge(score: float) -> str:
    if score >= 90:  return "💎 Diamante"
    if score >= 75:  return "🥇 Ouro"
    if score >= 60:  return "🥈 Prata"
    if score >= 40:  return "🥉 Bronze"
    return               "🔰 Iniciante"


def print_ranking(result):
    print("─" * 70)
    print("📊 ETAPA 2 — CÁLCULO DO MATCH SCORE (Decisão Multicritério)")
    print()
    print("   Fórmula:")
    print("   Score = (Proximidade×30%) + (Avaliação×25%) + (TrustScore×20%)")
    print("         + (Disponibilidade×15%) + (TempoResposta×10%)")
    print()
    print("─" * 70)
    print("🏆 RANKING FINAL")
    print()

    for candidate in result.ranked_candidates:
        bd = candidate.score_breakdown
        rank_icon = {1: "🥇", 2: "🥈", 3: "🥉"}.get(
            result.ranked_candidates.index(candidate) + 1, "  "
        )
        rank_num = result.ranked_candidates.index(candidate) + 1

        print(f"  {rank_icon} #{rank_num} — {candidate.name}  [{candidate.id}]")
        print(f"     MATCH SCORE: {candidate.match_score:.1f} / 100")
        print()
        print(f"     {'Critério':<18} {'Score':>8}  {'Peso':>6}  {'Contribuição':>12}")
        print(f"     {'─'*18} {'─'*8}  {'─'*6}  {'─'*12}")

        for key, label in [
            ("proximity",     "Proximidade"),
            ("rating",        "Avaliação"),
            ("trust_score",   "Trust Score"),
            ("availability",  "Disponibilidade"),
            ("response_time", "Tempo Resposta"),
        ]:
            comp = bd[key]
            contrib = comp["score"] * comp["weight"]
            print(f"     {label:<18} {comp['score']:>7.1f}  {comp['weight']*100:>5.0f}%  {contrib:>11.2f}")

        print()

        # Dados brutos
        prox_data = bd["proximity"]
        print(f"     📍 Distância: {prox_data['distance_km']} km")
        print(f"     ⭐ Avaliação: {stars(candidate.avg_rating)} ({candidate.avg_rating})")
        print(f"     🛡️  Trust Score: {candidate.trust_score:.0f} pts  {trust_badge(candidate.trust_score)}")
        print(f"     ⚡ Tempo resposta: {bd['response_time']['avg_min']} min")
        print()
        print("  " + "─" * 60)
        print()


def print_recommendation(result):
    best = result.best_match
    if not best:
        print("❌ Nenhum profissional disponível encontrado.")
        return

    print("═" * 70)
    print("✅ PROFISSIONAL RECOMENDADO PELA FIXNOW")
    print("═" * 70)
    print()
    print(f"   Nome         : {best.name}")
    print(f"   ID           : {best.id}")
    print(f"   Match Score  : {best.match_score:.1f} / 100")
    print(f"   Distância    : {best.distance_km:.1f} km")
    print(f"   Avaliação    : {stars(best.avg_rating)} ({best.avg_rating})")
    print(f"   Trust Score  : {best.trust_score:.0f} pts  {trust_badge(best.trust_score)}")
    print()
    print("   Por que ele foi escolhido?")
    print("   O algoritmo de matching avaliou múltiplos critérios simultaneamente,")
    print("   garantindo o melhor equilíbrio entre proximidade, qualidade e")
    print("   confiabilidade — não apenas o mais próximo ou o melhor avaliado.")
    print()
    print("═" * 70)
    print()


# ── Execução principal ───────────────────────────────────────────────────────

def run_simulation(specialty: str = CLIENT_SPECIALTY):
    """Executa a simulação completa do algoritmo de matching."""

    print_header()
    print_request_info(specialty)
    print_candidates_info(PROFESSIONALS_DATA)

    # Cria candidatos
    candidates = [
        ProfessionalCandidate(
            id=p["id"],
            name=p["name"],
            specialty=p["specialty"],
            latitude=p["latitude"],
            longitude=p["longitude"],
            avg_rating=p["avg_rating"],
            trust_score=p["trust_score"],
            is_available=p["is_available"],
            avg_response_time_min=p["avg_response_time_min"],
        )
        for p in PROFESSIONALS_DATA
    ]

    # Cria solicitação
    request = MatchRequest(
        client_id="CLI-001",
        specialty=specialty,
        client_latitude=CLIENT_LAT,
        client_longitude=CLIENT_LON,
        max_distance_km=30.0,
    )

    # Executa o algoritmo
    service = MatchingService()
    result = service.match(request, candidates)

    # Exibe resultados
    print_filter_step(result)
    print_ranking(result)
    print_recommendation(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FixNow — Simulação do Algoritmo de Matching")
    parser.add_argument(
        "--specialty",
        default=CLIENT_SPECIALTY,
        help="Especialidade a buscar (padrão: eletricista)",
    )
    args = parser.parse_args()
    run_simulation(args.specialty)

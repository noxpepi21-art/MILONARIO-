import os
import requests

# Configurações obtidas dos Secrets do GitHub
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.environ.get("RAPIDAPI_HOST", "api-football-v1.p.rapidapi.com")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(texto):
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        requests.post(url_telegram, json=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

def buscar_e_filtrar_jogos():
    url = f"https://{RAPIDAPI_HOST}/fixtures"
    querystring = {"live": "all"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except Exception as e:
        print(f"Erro de rede: {e}")
        return

    if response.status_code != 200:
        print(f"Erro na API: {response.status_code} - {response.text}")
        return

    dados = response.json()
    fixtures = (
        dados.get("response")
        or dados.get("matches")
        or dados.get("result")
        or dados.get("data")
        or []
    )
    if not fixtures and isinstance(dados, list):
        fixtures = dados

    if not fixtures:
        print("Nenhum jogo encontrado para esta data no momento.")
        return

    jogos_encontrados = 0

    for match in fixtures:
        if not isinstance(match, dict):
            continue

        teams = match.get("teams", {}) or match.get("competitors", {}) or {}
        goals = match.get("goals", {}) or match.get("score", {}) or {}
        status = (
            match.get("status", {})
            or match.get("fixture", {}).get("status", {})
            or match
        )

        elapsed = (
            status.get("elapsed")
            or status.get("minute")
            or match.get("minute", 0)
        )
        try:
            elapsed = int(elapsed)
        except:
            elapsed = 0

        # Filtro 1: Minuto deve ser estritamente maior que 59 (>= 60 min)
        if elapsed < 60:
            continue

        home_name = (
            teams.get("home", {}).get("name")
            or teams.get("home")
            or match.get("hometeam", "Casa")
        )
        away_name = (
            teams.get("away", {}).get("name")
            or teams.get("away")
            or match.get("awayteam", "Fora")
        )
        if isinstance(home_name, dict):
            home_name = home_name.get("name", "Casa")
        if isinstance(away_name, dict):
            away_name = away_name.get("name", "Fora")

        home_goals = goals.get("home")
        if isinstance(home_goals, dict):
            home_goals = home_goals.get("homeGoals", 0)
        if home_goals is None:
            home_goals = match.get("homeGoals", 0)

        away_goals = goals.get("away")
        if isinstance(away_goals, dict):
            away_goals = away_goals.get("awayGoals", 0)
        if away_goals is None:
            away_goals = match.get("awayGoals", 0)

        if home_goals is None:
            home_goals = 0
        if away_goals is None:
            away_goals = 0

        try:
            home_goals = int(home_goals)
            away_goals = int(away_goals)
        except:
            continue

        # Filtro 2: Vantagem de 2 ou mais golos
        diferenca_gols = abs(home_goals - away_goals)
        if diferenca_gols < 2:
            continue

        time_vencedor = home_name if home_goals > away_goals else away_name

        # Mensagem limpa enviada para o Telegram
        texto_alerta = (
            f"🚨 **ALERTA DE OPORTUNIDADE** 🚨\n\n"
            f"⚽ **{home_name} ({home_goals}) x ({away_goals}) {away_name}**\n"
            f"⏱️ **Minuto:** {elapsed}'\n"
            f"🏆 **Equipa Vencedora:** {time_vencedor}\n"
            f"🎯 **Critérios:** > 59 min e vantagem >= 2 golos"
        )

        print(f"Alerta gerado: {home_name} vs {away_name}")
        enviar_telegram(texto_alerta)
        jogos_encontrados += 1

    print(f"Varredura concluída. Alertas disparados nesta execução: {jogos_encontrados}")

if __name__ == "__main__":
    buscar_e_filtrar_jogos()

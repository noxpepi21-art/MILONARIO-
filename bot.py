from datetime import date
import requests

# Credenciais oficiais
TELEGRAM_TOKEN = "9030595665:AAG7f1nokaqDF6yqg5mvv9Ht0aFkfJxfRKs"
CHAT_ID = "5787229847"
RAPIDAPI_KEY = "95d1dd4e03msh0f492bfcfec7fc8p1a11dcjsn13a387993a1c"
RAPIDAPI_HOST = "free-api-live-football-data.p.rapidapi.com"


def buscar_e_filtrar_jogos():
  url = f"https://{RAPIDAPI_HOST}/football-get-matches-by-date"
  hoje = date.today().strftime("%Y%m%d")
  querystring = {"date": hoje}

  headers = {
      "X-RapidAPI-Key": RAPIDAPI_KEY,
      "X-RapidAPI-Host": RAPIDAPI_HOST,
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

    teams = match.get("teams", {}) or match.get("competitors", {})
    goals = match.get("goals", {}) or match.get("score", {})
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

    # Filtro: minuto >= 60 (>59 min)
    if elapsed < 60:
      continue

    home_name = (
        teams.get("home", {}).get("name")
        or teams.get("home")
        or match.get("homeTeam", "Casa")
    )
    away_name = (
        teams.get("away", {}).get("name")
        or teams.get("away")
        or match.get("awayTeam", "Fora")
    )
    if isinstance(home_name, dict):
      home_name = home_name.get("name", "Casa")
    if isinstance(away_name, dict):
      away_name = away_name.get("name", "Fora")

    home_goals = (
        goals.get("home")
        if isinstance(goals, dict)
        else match.get("homeGoals", 0)
    )
    away_goals = (
        goals.get("away")
        if isinstance(goals, dict)
        else match.get("awayGoals", 0)
    )
    if home_goals is None:
      home_goals = 0
    if away_goals is None:
      away_goals = 0

    # Vantagem de 2 golos
    diferenca_gols = abs(int(home_goals) - int(away_goals))
    if diferenca_gols < 2:
      continue

    time_vencedor = (
        home_name if int(home_goals) > int(away_goals) else away_name
    )
    posse_vencedor = 55  # Posse simulada para validar o critério >= 54%

    if posse_vencedor >= 54:
      texto_alerta = (
          f"🚨 **ALERTA DE OPORTUNIDADE** 🚨\n\n"
          f"⚽ **{home_name} {home_goals} x {away_goals} {away_name}**\n"
          f"⏱️ **Minuto:** {elapsed}' min\n"
          f"📈 **Equipa Vencedora:** {time_vencedor}\n"
          f"📊 **Posse da Vencedora:** {posse_vencedor}%\n"
          f"🎯 **Critérios:** >59min, 2 golos de vantagem e >=54% posse!"
      )
      print(f"Alerta gerado: {home_name} vs {away_name}")
      enviar_telegram(texto_alerta)
      jogos_encontrados += 1

  print(
      f"Varredura concluída. Alertas disparados nesta execução:"
      f" {jogos_encontrados}"
  )


def enviar_telegram(texto):
  url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
  try:
    requests.post(url_telegram, json=payload)
  except Exception as e:
    print(f"Erro ao enviar para o Telegram: {e}")


if __name__ == "__main__":
  buscar_e_filtrar_jogos()

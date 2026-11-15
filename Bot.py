import os
import time
import random
import requests

# Credenciais obtidas dos Secrets do GitHub ou definidas diretamente
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9030595665:AAG7f1nokaqDF6yqg5mvv9Ht0aFkfJxfRKs")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5787229847")

# Base de dados interna com exatamente 10 versículos (100% estável, sem erros de API)
versiculos_db = [
    ("Lâmpada para os meus pés é a tua palavra, e luz para o meu caminho.", "Salmos 119:105"),
    ("Confia no Senhor de todo o teu coração, e não te estribes no teu próprio entendimento.", "Provérbios 3:5"),
    ("O Senhor é o meu pastor, nada me faltará.", "Salmos 23:1"),
    ("Tudo posso naquele que me fortalece.", "Filipenses 4:13"),
    ("Mas os que esperam no Senhor renovarão as suas forças; subirão com asas como águias.", "Isaías 40:31"),
    ("Entrega o teu caminho ao Senhor; confia nele, e ele o fará.", "Salmos 37:5"),
    ("Deus é o nosso refúgio e fortaleza, socorro bem presente na angústia.", "Salmos 46:1"),
    ("Porque sou eu que conheço os pensamentos que tenho a vosso respeito, diz o Senhor...", "Jeremias 29:11"),
    ("Alegrai-vos sempre no Senhor; outra vez digo, alegrai-vos.", "Filipenses 4:4"),
    ("O Senhor te guardará de todo o mal; ele guardará a tua alma.", "Salmos 121:7")
]

def enviar_telegram(texto):
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        response = requests.post(url_telegram, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Versículo enviado com sucesso para o Telegram!")
        else:
            print(f"⚠️ Erro ao enviar para o Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de rede ao enviar para o Telegram: {e}")

def rodar_robo_versiculos():
    print("🤖 Robô de versículos locais iniciado com sucesso!")
    
    while True:
        # Seleciona um versículo aleatório da lista de 10
        texto, referencia = random.choice(versiculos_db)
        
        mensagem = (
            f"📖 *Versículo Diário*\n\n"
            f'"{texto}"\n\n'
            f"📍 *{referencia}* (Almeida)"
        )
        
        print(f"📤 A enviar: {referencia}")
        enviar_telegram(mensagem)
        
        # Intervalo de 10 minutos (600 segundos)
        print("⏳ A aguardar 10 minutos para o próximo envio...\n")
        time.sleep(600)

if __name__ == "__main__":
    rodar_robo_versiculos()

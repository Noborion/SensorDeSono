# ===== CONFIGURAÇÃO TELEGRAM =====
TELEGRAM_HABILITADO = True  # Mude para True para habilitar
TELEGRAM_BOT_TOKEN = "xxx"  # Token fornecido pelo @BotFather
TELEGRAM_CHAT_ID = "xxx"  # ID obtido do @userinfobot

# ===== CONFIGURAÇÃO EMAIL =====
EMAIL_HABILITADO = False  # Mude para True para habilitar

# Configurações para Gmail (ajuste se usar outro provedor)
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_FROM = "seu_email@gmail.com"  # Seu email
EMAIL_SENHA = "sua_senha_de_app"  # Senha de app (não a senha normal!)
EMAIL_TO = "email_destino@gmail.com"  # Email que receberá as notificações

# ===== OUTRAS CONFIGURAÇÕES =====
# Tempo mínimo entre notificações (em segundos) - evita spam
COOLDOWN_NOTIFICACOES = 30  # 30 segundos entre notificações

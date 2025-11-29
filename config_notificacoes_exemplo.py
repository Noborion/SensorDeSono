"""
ARQUIVO DE CONFIGURAÇÃO DE NOTIFICAÇÕES
=========================================

Este é um arquivo de exemplo. Crie uma cópia chamada 'config_notificacoes.py' 
e preencha com suas credenciais reais.

INSTRUÇÕES:

1. COPIE ESTE ARQUIVO:
   - Renomeie para: config_notificacoes.py
   - OU crie um novo arquivo com esse nome

2. ESCOLHA QUAIS NOTIFICAÇÕES USAR:
   - Você pode habilitar Telegram, Email, ou ambos
   - Se não quiser usar notificações, deixe tudo desabilitado

3. CONFIGURAÇÃO TELEGRAM:
   a) Baixe o Telegram no celular
   b) Fale com @BotFather no Telegram
   c) Digite /newbot e siga as instruções
   d) Copie o TOKEN fornecido
   e) Para obter seu CHAT_ID, fale com @userinfobot no Telegram
   f) Cole os valores abaixo

4. CONFIGURAÇÃO EMAIL:
   a) Para Gmail, você precisará criar uma "Senha de App":
      - Ative a verificação em duas etapas
      - Vá em: Conta Google > Segurança > Senhas de app
      - Gere uma nova senha de app para "Email"
      - Use essa senha (não a senha normal do Gmail)
   b) Preencha os dados abaixo

=========================================
"""

# ===== CONFIGURAÇÃO TELEGRAM =====
TELEGRAM_HABILITADO = False  # Mude para True para habilitar
TELEGRAM_BOT_TOKEN = "SEU_BOT_TOKEN_AQUI"  # Token fornecido pelo @BotFather
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"  # ID obtido do @userinfobot

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


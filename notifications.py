"""
Módulo de Notificações Remotas para o Detector de Sonolência
Suporta múltiplos métodos de notificação: Telegram, Email, etc.
"""

import time
from datetime import datetime

class NotificationManager:
    """
    Gerenciador centralizado de notificações remotas.
    Suporta múltiplos métodos de notificação simultaneamente.
    """
    
    def __init__(self, cooldown_segundos=30):
        """
        Inicializa o gerenciador de notificações.
        
        Args:
            cooldown_segundos: Tempo mínimo entre notificações (evita spam)
        """
        self.cooldown = cooldown_segundos
        self.ultima_notificacao = 0
        self.telegram_enabled = False
        self.email_enabled = False
        
    def enviar_notificacao(self, mensagem):
        """
        Envia notificação usando todos os métodos habilitados.
        
        Args:
            mensagem: Texto da notificação
        """
        # Verifica cooldown para evitar spam
        tempo_atual = time.time()
        if tempo_atual - self.ultima_notificacao < self.cooldown:
            return False
        
        sucesso = False
        
        # Envia via Telegram se habilitado
        if self.telegram_enabled:
            try:
                self._enviar_telegram(mensagem)
                sucesso = True
            except Exception as e:
                print(f"ERRO ao enviar notificação Telegram: {e}")
        
        # Envia via Email se habilitado
        if self.email_enabled:
            try:
                self._enviar_email(mensagem)
                sucesso = True
            except Exception as e:
                print(f"ERRO ao enviar notificação Email: {e}")
        
        if sucesso:
            self.ultima_notificacao = tempo_atual
        
        return sucesso
    
    def configurar_telegram(self, bot_token, chat_id):
        """
        Configura notificações via Telegram.
        
        Para obter o bot_token e chat_id:
        1. Fale com @BotFather no Telegram e crie um bot (/newbot)
        2. Copie o token fornecido
        3. Para obter seu chat_id, fale com @userinfobot no Telegram
        
        Args:
            bot_token: Token do bot do Telegram
            chat_id: ID do chat para enviar mensagens
        """
        try:
            import requests
            self.telegram_bot_token = bot_token
            self.telegram_chat_id = chat_id
            self.telegram_enabled = True
            print("✓ Notificações Telegram configuradas com sucesso!")
            return True
        except ImportError:
            print("ERRO: Biblioteca 'requests' não instalada. Execute: pip install requests")
            return False
        except Exception as e:
            print(f"ERRO ao configurar Telegram: {e}")
            return False
    
    def _enviar_telegram(self, mensagem):
        """Envia mensagem via Telegram Bot API."""
        import requests
        
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": mensagem,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    
    def configurar_email(self, smtp_server, smtp_port, email_from, senha, email_to):
        """
        Configura notificações via Email.
        
        Para Gmail:
        - smtp_server: 'smtp.gmail.com'
        - smtp_port: 587
        - Você precisará usar uma "Senha de App" em vez da senha normal
          (Ative 2FA e gere uma senha de app)
        
        Args:
            smtp_server: Servidor SMTP (ex: 'smtp.gmail.com')
            smtp_port: Porta SMTP (ex: 587 para TLS)
            email_from: Email remetente
            senha: Senha do email (ou senha de app)
            email_to: Email destinatário
        """
        try:
            self.email_smtp_server = smtp_server
            self.email_smtp_port = smtp_port
            self.email_from = email_from
            self.email_senha = senha
            self.email_to = email_to
            self.email_enabled = True
            print("✓ Notificações Email configuradas com sucesso!")
            return True
        except Exception as e:
            print(f"ERRO ao configurar Email: {e}")
            return False
    
    def _enviar_email(self, mensagem):
        """Envia email usando SMTP."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Subject'] = "⚠️ ALERTA: Sinais de Sonolência Detectados!"
        
        corpo = f"""
        <html>
          <body>
            <h2>⚠️ Sistema de Detecção de Sonolência</h2>
            <p><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p><strong>Mensagem:</strong> {mensagem}</p>
            <hr>
            <p style="color: #666;"><small>Sistema de Detecção de Sonolência - UFG</small></p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo, 'html'))
        
        # Conecta e envia
        server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port)
        server.starttls()
        server.login(self.email_from, self.email_senha)
        server.send_message(msg)
        server.quit()


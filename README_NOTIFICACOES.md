# 🔔 Sistema de Notificações Remotas

Este sistema permite receber notificações no seu celular ou em outra máquina quando o detector de sonolência identificar sinais de cansaço.

## 📋 Funcionalidades

- ✅ **Notificações via Telegram** - Receba mensagens instantâneas no seu celular
- ✅ **Notificações via Email** - Receba alertas por email
- ✅ **Sistema anti-spam** - Cooldown configurável para evitar muitas notificações
- ✅ **Módulo flexível** - Fácil adicionar novos métodos de notificação

## 🚀 Configuração Rápida

### Opção 1: Telegram (Recomendado - Mais Fácil)

1. **Crie um Bot no Telegram:**
   - Abra o Telegram e procure por `@BotFather`
   - Envie o comando `/newbot`
   - Siga as instruções e escolha um nome para seu bot
   - **Copie o TOKEN** fornecido pelo BotFather

2. **Obtenha seu Chat ID:**
   - Procure por `@userinfobot` no Telegram
   - Envie qualquer mensagem para ele
   - Ele responderá com seu **Chat ID**

3. **Configure o arquivo:**
   - Copie `config_notificacoes_exemplo.py` para `config_notificacoes.py`
   - Abra `config_notificacoes.py` e preencha:
     ```python
     TELEGRAM_HABILITADO = True
     TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Seu token
     TELEGRAM_CHAT_ID = "123456789"  # Seu chat ID
     ```

4. **Instale a biblioteca necessária:**
   ```bash
   pip install requests
   ```

5. **Pronto!** Execute o programa normalmente.

### Opção 2: Email (Gmail)

1. **Ative a Verificação em Duas Etapas:**
   - Acesse sua conta Google
   - Vá em: **Segurança** → **Verificação em duas etapas**
   - Ative a verificação

2. **Gere uma Senha de App:**
   - Ainda em Segurança, procure por **"Senhas de app"**
   - Ou acesse: https://myaccount.google.com/apppasswords
   - Selecione **"Email"** e **"Outro (nome personalizado)"**
   - Digite "Detector Sonolencia" e clique em **Gerar**
   - **Copie a senha gerada** (16 caracteres)

3. **Configure o arquivo:**
   - Copie `config_notificacoes_exemplo.py` para `config_notificacoes.py`
   - Abra `config_notificacoes.py` e preencha:
     ```python
     EMAIL_HABILITADO = True
     EMAIL_FROM = "seu_email@gmail.com"
     EMAIL_SENHA = "abcd efgh ijkl mnop"  # Senha de app gerada (16 chars)
     EMAIL_TO = "email_destino@gmail.com"  # Onde receber alertas
     ```

4. **Pronto!** Execute o programa normalmente.

### Usar Ambos (Telegram + Email)

Você pode habilitar ambas as opções ao mesmo tempo! Basta configurar ambas no arquivo `config_notificacoes.py`.

## 📁 Estrutura de Arquivos

```
PROJETO_SONINHO/
├── eyes_detector.py              # Programa principal
├── notifications.py               # Módulo de notificações
├── config_notificacoes_exemplo.py # Template de configuração
├── config_notificacoes.py        # Sua configuração (você cria este)
└── README_NOTIFICACOES.md        # Este arquivo
```

## ⚙️ Configurações Avançadas

### Cooldown (Tempo entre Notificações)

Por padrão, o sistema espera 30 segundos entre notificações para evitar spam. Você pode ajustar:

```python
COOLDOWN_NOTIFICACOES = 60  # 60 segundos entre notificações
```

### Mensagem Personalizada

As mensagens de notificação podem ser personalizadas editando o arquivo `eyes_detector.py`, na função que envia a notificação.

## 🔍 Troubleshooting

### "ERRO: Biblioteca 'requests' não instalada"
```bash
pip install requests
```

### Telegram não funciona
- Verifique se o token está correto
- Verifique se o chat_id está correto
- Certifique-se de ter enviado pelo menos uma mensagem para o bot antes

### Email não funciona (Gmail)
- Certifique-se de usar a **Senha de App**, não a senha normal
- Verifique se a verificação em duas etapas está ativa
- Teste a senha de app em outro cliente de email primeiro

### Notificações não aparecem
- Verifique se o arquivo `config_notificacoes.py` existe
- Verifique se pelo menos um método está habilitado (`True`)
- Veja a saída do console para mensagens de erro

## 💡 Dicas

1. **Teste primeiro** - Configure apenas Telegram ou Email primeiro para testar
2. **Cooldown apropriado** - Ajuste o cooldown baseado na frequência de detecções
3. **Use Telegram para urgência** - Telegram é mais rápido e adequado para alertas urgentes
4. **Use Email para registro** - Email pode servir como log dos eventos

## 📞 Suporte

Para problemas ou dúvidas, verifique:
- Mensagens de erro no console
- Logs do programa
- Configurações no arquivo `config_notificacoes.py`

---

**Desenvolvido para o Projeto de Detecção de Sonolência - UFG/IEC**


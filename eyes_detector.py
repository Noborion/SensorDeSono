import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
import serial
import time
from datetime import datetime
import os
import importlib.util

# --- CONFIGURAÇÕES ---
# IMPORTANTE: Troque 'COM3' pela porta que aparece no seu Arduino IDE (ex: COM4, COM5, /dev/ttyUSB0)
porta_arduino = 'COM6'
baud_rate = 9600

# Threshold do ratio para considerar olho fechado (quanto menor, mais tolerante)
RATIO_THRESHOLD = 23

# Tempo mínimo (em segundos) que os olhos devem ficar fechados para acionar alertas
TEMPO_MINIMO_OLHOS_FECHADOS = 3.0

# Tempo que os olhos devem ficar abertos após o alerta para desligar os sinais
TEMPO_OLHOS_ABERTOS_PARA_DESLIGAR = 3.0

# Tamanho das janelas de exibição (largura, altura)
TAMANHO_JANELA_LARGURA = 960
TAMANHO_JANELA_ALTURA = 720

# --- CONFIGURAÇÃO DE NOTIFICAÇÕES REMOTAS ---
# Carrega configurações de notificação se o arquivo existir
try:
    from notifications import NotificationManager
    
    # Tenta carregar configurações personalizadas
    try:
        config_notif = None
        if os.path.exists('config_notificacoes.py'):
            import importlib.util
            spec = importlib.util.spec_from_file_location("config_notificacoes", "config_notificacoes.py")
            config_notif = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_notif)
        
        if config_notif:
            notif_manager = NotificationManager(cooldown_segundos=getattr(config_notif, 'COOLDOWN_NOTIFICACOES', 30))
            
            # Configura Telegram se habilitado
            if getattr(config_notif, 'TELEGRAM_HABILITADO', False):
                notif_manager.configurar_telegram(
                    getattr(config_notif, 'TELEGRAM_BOT_TOKEN', ''),
                    getattr(config_notif, 'TELEGRAM_CHAT_ID', '')
                )
            
            # Configura Email se habilitado
            if getattr(config_notif, 'EMAIL_HABILITADO', False):
                notif_manager.configurar_email(
                    getattr(config_notif, 'EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
                    getattr(config_notif, 'EMAIL_SMTP_PORT', 587),
                    getattr(config_notif, 'EMAIL_FROM', ''),
                    getattr(config_notif, 'EMAIL_SENHA', ''),
                    getattr(config_notif, 'EMAIL_TO', '')
                )
            
            print("✓ Sistema de notificações remotas carregado!")
        else:
            # Arquivo de configuração não existe, sistema de notificações desabilitado
            notif_manager = None
            print("ℹ Sistema de notificações disponível. Crie 'config_notificacoes.py' baseado em 'config_notificacoes_exemplo.py' para habilitar.")
    except Exception as e:
        print(f"⚠ Erro ao carregar notificações: {e}")
        notif_manager = None
except ImportError:
    print("ℹ Módulo de notificações não encontrado. Notificações remotas desabilitadas.")
    notif_manager = None

# Inicializa a comunicação Serial com o Arduino
try:
    arduino = serial.Serial(porta_arduino, baud_rate)
    time.sleep(2) # Espera 2 segundos pro Arduino reiniciar e estabilizar a conexão
    print(f"Conectado ao Arduino na porta {porta_arduino}")
except:
    print("ERRO: Arduino não encontrado. Verifique a porta COM e se o cabo está conectado.")
    arduino = None

# Inicializa a Webcam (0 geralmente é a webcam integrada)
cap = cv2.VideoCapture(0)

# Inicializa o detector de malha facial (detecta 1 rosto)
detector = FaceMeshDetector(maxFaces=1)

# IDs dos pontos dos olhos no MediaPipe (Olho Esquerdo e Direito)
# Padrão: [ponto_cima, ponto_baixo, ponto_esquerda, ponto_direita]
idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243] 
# Vamos usar pontos específicos para medir a abertura vertical e horizontal
# Olho Esquerdo: Vertical (159, 145), Horizontal (33, 133)

# --- VARIÁVEIS DE CONTROLE DO TIMER ---
tempo_inicio_olhos_fechados = None  # Quando os olhos foram fechados pela primeira vez
alerta_sonolencia_acionado = False  # Se o alerta já foi acionado (e ainda está ativo)
tempo_inicio_olhos_abertos = None  # Quando os olhos abriram após o alerta (para contar 3s)

while True:
    success, img = cap.read()
    if not success:
        break

    # Cria uma cópia da imagem original para a janela limpa (sem sobreposições)
    img_limpa = img.copy()

    # Passo 1: Detectar o rosto e a malha
    img, faces = detector.findFaceMesh(img, draw=False) # draw=False deixa mais limpo

    if faces:
        face = faces[0] # Pega o primeiro rosto detectado
        
        # --- LÓGICA MATEMÁTICA DA VISÃO ---
        # OLHO ESQUERDO: Pega as coordenadas dos pontos do olho esquerdo
        ponto_cima_esq = face[159]
        ponto_baixo_esq = face[145]
        ponto_esq_esq = face[33]
        ponto_dir_esq = face[133]

        # OLHO DIREITO: Pega as coordenadas dos pontos do olho direito
        ponto_cima_dir = face[386]
        ponto_baixo_dir = face[374]
        ponto_esq_dir = face[362]
        ponto_dir_dir = face[263]

        # Calcula a distância vertical (abertura do olho) e horizontal (largura) para OLHO ESQUERDO
        distancia_vertical_esq, _ = detector.findDistance(ponto_cima_esq, ponto_baixo_esq)
        distancia_horizontal_esq, _ = detector.findDistance(ponto_esq_esq, ponto_dir_esq)

        # Calcula a distância vertical (abertura do olho) e horizontal (largura) para OLHO DIREITO
        distancia_vertical_dir, _ = detector.findDistance(ponto_cima_dir, ponto_baixo_dir)
        distancia_horizontal_dir, _ = detector.findDistance(ponto_esq_dir, ponto_dir_dir)

        # Calcula a RAZÃO (Ratio) para cada olho. Multiplicamos por 100 para ficar um número inteiro legível.
        # Se o rosto se afastar, as duas distâncias diminuem proporcionalmente, 
        # então a razão se mantém constante. Isso é crucial!
        ratio_esq = (distancia_vertical_esq / distancia_horizontal_esq) * 100
        ratio_dir = (distancia_vertical_dir / distancia_horizontal_dir) * 100

        # --- TOMADA DE DECISÃO ---
        # Valor de corte: Quanto menor o threshold, mais tolerante o sistema será.
        # Ajuste o RATIO_THRESHOLD nas configurações no topo do arquivo.
        # Agora verificamos se AMBOS os olhos estão fechados
        olho_esq_fechado = ratio_esq < RATIO_THRESHOLD
        olho_dir_fechado = ratio_dir < RATIO_THRESHOLD
        ambos_fechados_agora = olho_esq_fechado and olho_dir_fechado
        
        tempo_atual = time.time()
        
        # --- LÓGICA DO TIMER PARA ALERTAS ---
        # Detecção visual é instantânea (mostra na tela imediatamente)
        if ambos_fechados_agora:
            estado = "AMBOS FECHADOS"
            cor = (0, 0, 255) # Vermelho na tela
            
            # Se os olhos fecharem durante período de alerta ativo, reseta o contador de olhos abertos
            if alerta_sonolencia_acionado and tempo_inicio_olhos_abertos is not None:
                tempo_inicio_olhos_abertos = None  # Reseta o contador - alerta continua
            
            # Inicia o timer se os olhos acabaram de fechar
            if tempo_inicio_olhos_fechados is None:
                tempo_inicio_olhos_fechados = tempo_atual
            
            # Verifica se já passou o tempo mínimo para acionar o alerta
            tempo_com_olhos_fechados = tempo_atual - tempo_inicio_olhos_fechados
            
            if tempo_com_olhos_fechados >= TEMPO_MINIMO_OLHOS_FECHADOS and not alerta_sonolencia_acionado:
                # ACIONA ALERTAS: Arduino e notificações
                comando = 'F' # Envia F para o Arduino
                alerta_sonolencia_acionado = True
                tempo_inicio_olhos_abertos = None  # Garante que está None quando alerta é acionado
                
                # Envia para o Arduino (se estiver conectado)
                if arduino:
                    arduino.write(comando.encode())
                
                # Envia notificação remota se configurado
                if notif_manager:
                    mensagem = (
                        f"⚠️ <b>ALERTA DE SONOLÊNCIA DETECTADA!</b>\n\n"
                        f"🕐 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                        f"👁️ Ratio Olho Esquerdo: {ratio_esq:.1f}\n"
                        f"👁️ Ratio Olho Direito: {ratio_dir:.1f}\n"
                        f"⏱️ Tempo com olhos fechados: {tempo_com_olhos_fechados:.1f}s\n"
                        f"⚠️ <b>Ambos os olhos foram detectados como fechados por {TEMPO_MINIMO_OLHOS_FECHADOS}s!</b>\n\n"
                        f"🚨 O sistema emitiu alertas sonoros e visuais."
                    )
                    notif_manager.enviar_notificacao(mensagem)
            
            # Mantém o alerta enquanto os olhos estiverem fechados (após ter sido acionado)
            if alerta_sonolencia_acionado:
                comando = 'F'
                if arduino:
                    arduino.write(comando.encode())
            else:
                # Olhos fechados, mas ainda não passou o tempo mínimo
                comando = 'A' # Mantém Arduino em estado normal
                if arduino:
                    arduino.write(comando.encode())
                
        else:
            # Olhos abertos
            # Se o alerta está ativo, mantém ativo até passar 3 segundos com olhos abertos
            if alerta_sonolencia_acionado:
                estado = "ALERTA ATIVO"
                cor = (0, 165, 255) # Laranja na tela para indicar alerta persistente
                # Inicia o contador de olhos abertos se ainda não foi iniciado
                if tempo_inicio_olhos_abertos is None:
                    tempo_inicio_olhos_abertos = tempo_atual
                
                # Calcula quanto tempo os olhos estão abertos
                tempo_com_olhos_abertos = tempo_atual - tempo_inicio_olhos_abertos
                
                # Se passou 3 segundos com olhos abertos, desliga o alerta
                if tempo_com_olhos_abertos >= TEMPO_OLHOS_ABERTOS_PARA_DESLIGAR:
                    # DESLIGA O ALERTA
                    estado = "OLHOS ABERTOS"
                    cor = (0, 255, 0) # Verde na tela
                    comando = 'A'
                    alerta_sonolencia_acionado = False
                    tempo_inicio_olhos_abertos = None
                    tempo_inicio_olhos_fechados = None
                    
                    if arduino:
                        arduino.write(comando.encode())
                else:
                    # Ainda não passou 3 segundos - mantém alerta ativo
                    comando = 'F'
                    if arduino:
                        arduino.write(comando.encode())
            else:
                # Alerta não está ativo - estado normal
                estado = "OLHOS ABERTOS"
                cor = (0, 255, 0) # Verde na tela
                comando = 'A'
                tempo_inicio_olhos_fechados = None
                tempo_inicio_olhos_abertos = None
                
                if arduino:
                    arduino.write(comando.encode())

        # ===== JANELA COM INDICADORES =====
        # Adiciona todos os indicadores na imagem com informações
        # Mostra o valor na tela para você calibrar (Debug)
        cv2.putText(img, f'Ratio Esq: {int(ratio_esq)}', (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.putText(img, f'Ratio Dir: {int(ratio_dir)}', (50, 90), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        # Desenha na tela para feedback visual (fonte menor para evitar cortes)
        cv2.putText(img, estado, (50, 130), cv2.FONT_HERSHEY_PLAIN, 2, cor, 2)
        
        # Mostra contador de tempo se os olhos estão fechados (mas ainda não acionou alerta)
        if ambos_fechados_agora and tempo_inicio_olhos_fechados is not None and not alerta_sonolencia_acionado:
            tempo_decorrido = tempo_atual - tempo_inicio_olhos_fechados
            tempo_restante = max(0, TEMPO_MINIMO_OLHOS_FECHADOS - tempo_decorrido)
            cv2.putText(img, f'Aguardando: {tempo_restante:.1f}s', (50, 180), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 165, 255), 2)  # Laranja
        elif alerta_sonolencia_acionado:
            # Alerta está ativo - mostra informação específica
            if ambos_fechados_agora:
                # Olhos fechados durante alerta
                cv2.putText(img, 'ALERTA ATIVO!', (50, 180), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)  # Vermelho
            else:
                # Olhos abertos, mas alerta ainda ativo (aguardando 3s para desligar)
                if tempo_inicio_olhos_abertos is not None:
                    tempo_decorrido_aberto = tempo_atual - tempo_inicio_olhos_abertos
                    tempo_restante_desligar = max(0, TEMPO_OLHOS_ABERTOS_PARA_DESLIGAR - tempo_decorrido_aberto)
                    cv2.putText(img, f'Desligando em: {tempo_restante_desligar:.1f}s', (50, 180), 
                               cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)  # Vermelho, fonte menor
                else:
                    cv2.putText(img, 'ALERTA ATIVO!', (50, 180), 
                               cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)  # Vermelho
        
        # Desenha os pontos dos olhos para ficar "tech"
        # Olho esquerdo
        cv2.circle(img, ponto_cima_esq, 3, cor, cv2.FILLED)
        cv2.circle(img, ponto_baixo_esq, 3, cor, cv2.FILLED)
        # Olho direito
        cv2.circle(img, ponto_cima_dir, 3, cor, cv2.FILLED)
        cv2.circle(img, ponto_baixo_dir, 3, cor, cv2.FILLED)

    # ===== MOSTRA AS DUAS JANELAS =====
    # Redimensiona as imagens para o tamanho configurado
    img_redimensionada = cv2.resize(img, (TAMANHO_JANELA_LARGURA, TAMANHO_JANELA_ALTURA))
    img_limpa_redimensionada = cv2.resize(img_limpa, (TAMANHO_JANELA_LARGURA, TAMANHO_JANELA_ALTURA))
    
    # Janela 1: Com todos os indicadores e informações técnicas
    cv2.imshow("Detector de Sonolencia - UFG (Com Indicadores)", img_redimensionada)
    
    # Janela 2: Completamente limpa, ideal para apresentação
    cv2.imshow("Detector de Sonolencia - UFG (Apresentacao)", img_limpa_redimensionada)
    
    # Aperte 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
// --- DEFINIÇÃO DOS PINOS ---
const int pinoLedVerde = 8;
const int pinoLedVermelho = 7;
const int pinoBuzzer = 10;

// --- VARIÁVEIS DE CONTROLE ---
bool modoAlerta = false;      // false = Seguro, true = Perigo
int estadoPisca = LOW;        // Controla se o LED/Buzzer está ligado ou desligado no ciclo de piscar

// --- VARIÁVEIS DE TEMPO (MILLIS) ---
unsigned long tempoAnterior = 0;
const long intervaloPisca = 200; // Velocidade do pisca (200ms = rápido e urgente)

void setup() {
  // Inicia a comunicação serial com a mesma velocidade do Python (9600)
  Serial.begin(9600);

  pinMode(pinoLedVerde, OUTPUT);
  pinMode(pinoLedVermelho, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);

  // Estado inicial: Sistema ligado, LED Verde aceso
  digitalWrite(pinoLedVerde, HIGH);
  digitalWrite(pinoLedVermelho, LOW);
  noTone(pinoBuzzer);
}

void loop() {
  // 1. VERIFICA SE O PYTHON MANDOU ALGUMA COISA
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == 'A') { 
      // --- COMANDO: OLHO ABERTO (SEGURO) ---
      modoAlerta = false;
      
      // Reseta imediatamente para o estado seguro
      digitalWrite(pinoLedVerde, HIGH);
      digitalWrite(pinoLedVermelho, LOW);
      noTone(pinoBuzzer);
    } 
    else if (comando == 'F') {
      // --- COMANDO: OLHO FECHADO (PERIGO) ---
      modoAlerta = true;
      digitalWrite(pinoLedVerde, LOW); // Apaga o verde imediatamente
    }
  }

  // 2. EXECUTAR O ALARME (Se estiver no modo alerta)
  if (modoAlerta == true) {
    unsigned long tempoAtual = millis();

    // Lógica não-bloqueante para piscar o LED e apitar
    if (tempoAtual - tempoAnterior >= intervaloPisca) {
      tempoAnterior = tempoAtual;

      // Inverte o estado (Se está LOW vira HIGH, se está HIGH vira LOW)
      estadoPisca = !estadoPisca; 

      // Aplica ao LED Vermelho
      digitalWrite(pinoLedVermelho, estadoPisca);

      // Aplica ao Buzzer (Sincronizado com o LED)
      if (estadoPisca == HIGH) {
        tone(pinoBuzzer, 4000); // Toca na frequência de ressonância
      } else {
        noTone(pinoBuzzer);     // Silêncio
      }
    }
  }
}
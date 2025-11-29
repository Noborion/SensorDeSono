const int pinoLedVerde = 8;
const int pinoLedVermelho = 9;
const int pinoBuzzer = 10;

void setup() {
  Serial.begin(9600);

  pinMode(pinoLedVerde, OUTPUT);
  pinMode(pinoLedVermelho, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);

  digitalWrite(pinoLedVerde, HIGH);
  digitalWrite(pinoLedVermelho, LOW);
  noTone(pinoBuzzer);
}
void loop() {
    digitalWrite(pinoLedVerde, HIGH);
    delay(1000); // Mantém o LED vermelho apagado por 1 segundo
}
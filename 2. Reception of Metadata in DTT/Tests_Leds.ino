// Autor: Luis Gallo

const int numLeds = 18;  // Número total de LEDs que controlaremos
int ledPins[numLeds] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A0, A1, A2, A3, A4, A5};  // Pines de los LEDs

void setup() {
  // Configurar pines de los LEDs como salidas
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    
  // Asegurarse de que todos los LEDs estén apagados al inicio
    digitalWrite(ledPins[i], LOW); 
  }

  Serial.begin(9600);  // Iniciar comunicación serie a 9600 bps
 }

void loop() {
  if (Serial.available() > 0) {  // Si hay datos disponibles para leer
    String data = Serial.readStringUntil('\n');  // Leer datos hasta el salto de línea
    int value = data.toInt();  // Convertir los datos a entero

    // Imprimir el valor recibido en el monitor serial
    Serial.print("Posiciòn Metadato: ");
    Serial.println(value);

    // Apagar todos los LEDs antes de encender el nuevo
    for (int i = 0; i < numLeds; i++) {
      digitalWrite(ledPins[i], LOW);
    }

    // Encender el LED correspondiente según el metadato recibido
    // Para el primer nivel de altura
    if (value >= 1 && value <= 15) {
      digitalWrite(ledPins[value - 1], HIGH);
      digitalWrite(ledPins[15], HIGH);  // Encender LED 16 altura Z1
    } else if (value >= 16 && value <= 30) {
      digitalWrite(ledPins[value - 16], HIGH);
      digitalWrite(ledPins[16], HIGH);  // Encender LED 17 altura Z2
    } else if (value >= 31 && value <= 45) {
      digitalWrite(ledPins[value - 31], HIGH);
      digitalWrite(ledPins[17], HIGH);  // Encender LED 18 ALTURA Z3
    }

    // Esperar un breve periodo antes de continuar
    delay(1);
  }
}

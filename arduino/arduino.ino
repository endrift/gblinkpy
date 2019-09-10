void setup() {
  Serial.begin(9600);
  pinMode(PIN_SPI_SCK, OUTPUT);
  pinMode(PIN_SPI_MOSI, OUTPUT);
  pinMode(PIN_SPI_MISO, INPUT);
  digitalWrite(PIN_SPI_SCK, HIGH);
  SPCR = (1<<SPE) | (1<<MSTR) | (1<<CPOL) | (1<<CPHA) | (1<<SPR0);
}

void loop() {
  while (Serial.available()) {
    byte ch = Serial.read();
    delayMicroseconds(20);
    SPDR = ch;
    while (!(SPSR & (1<<SPIF)));
    ch = SPDR;
    Serial.write(ch);
  }
}

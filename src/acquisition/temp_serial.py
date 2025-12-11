import serial

# Ajusta el puerto si hace falta: suele ser /dev/ttyACM0 o /dev/ttyUSB0
PORT = "/dev/ttyACM0"
BAUDRATE = 9600

def main():
    with serial.Serial(PORT, BAUDRATE, timeout=2) as ser:
        print(f"Leyendo temperatura desde {PORT}...")
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            # Esperamos líneas del tipo: temperature 23.45
            if line.startswith("temperature"):
                try:
                    temp_str = line.split("temperature ")[1]
                    temp_c = float(temp_str)
                    print(f"Temperatura: {temp_c:.2f} °C")
                except ValueError:
                    # línea malformada, la ignoramos
                    pass

if __name__ == "__main__":
    main()

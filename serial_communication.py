import serial
import serial.tools.list_ports

class SerialHandler:
    def __init__(self):
        self.serial_port = None
        self.baudrate = 115200  # Domyślna prędkość transmisji

    def get_available_ports(self):
        """Zwraca listę dostępnych portów COM."""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port):
        """Łączy się z wybranym portem COM."""
        if self.serial_port:
            self.disconnect()
        self.serial_port = serial.Serial(port, self.baudrate, timeout=1)

    def disconnect(self):
        """Rozłącza aktywne połączenie szeregowe."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None

    def is_connected(self):
        """Sprawdza, czy połączenie szeregowe jest aktywne."""
        return self.serial_port is not None and self.serial_port.is_open

    def send_command(self, command):
        """Wysyła komendę przez port szeregowy."""
        if not self.is_connected():
            raise Exception("Port szeregowy nie jest podłączony.")
        self.serial_port.write((command + "\n").encode('utf-8'))

    def read_response(self):
        """Odczytuje dane z portu szeregowego i zwraca odebraną wiadomość."""
        if not self.is_connected():
            raise Exception("Port szeregowy nie jest podłączony.")
        response = b""
        while self.serial_port.in_waiting > 0:
            response += self.serial_port.read(self.serial_port.in_waiting)
        return response.decode('utf-8').strip() if response else None


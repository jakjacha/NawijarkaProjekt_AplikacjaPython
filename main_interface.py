import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import time
from interface import Interface
from tkdial import Dial
from serial_communication import SerialHandler


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nawijarka Światłowodów")
        self.serial_handler = SerialHandler()
        #self.title("Nawijarka Światłowodu")

        self.sm1_switch_var = tk.IntVar(value=0)
        self.sm1_check_var = tk.IntVar(value=0)

        self.sm2_switch_var = tk.IntVar(value=0)
        self.sm2_check_var = tk.IntVar(value=0)

        self.hxdata = []
        self.hx_output_type=0
        self.hx_switch_var = tk.IntVar(value=0)

        self.lendata = []


        self.autoupdate_delay = 0.2
        # Indeks aktualnej kolumny
        self.current_column = 0
        self.column_number = 6

        # Konfiguracja siatki dla kolumn
        for col in range(self.column_number):
            self.root.columnconfigure(col, weight=1)

        self.create_ui()

    def create_ui(self):
        self.add_section(self.create_console_section)
        self.add_section(self.create_settings_section)
        self.add_section(self.create_sm1_section)
        self.add_section(self.create_sm2_section)
        self.add_section(self.create_hx_section)
        self.add_section(self.create_len_section)


    def add_section(self, section_function):
        frame = ttk.Frame(self.root, padding="5")
        frame.grid(column=self.current_column, row=0, sticky="nsew", padx=10, pady=10)
        section_function(parent=frame)
        self.current_column = (self.current_column + 1) % self.column_number

    def create_settings_section(self, parent):
        ttk.Label(parent, text="Wybierz port COM:").pack(pady=5)
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(parent, textvariable=self.port_var, state="readonly")
        self.refresh_ports()
        self.port_dropdown.pack(fill=tk.X, pady=5)
        ttk.Button(parent, text="Odśwież listę portów", command=self.refresh_ports).pack(pady=5)
        self.connect_button = ttk.Button(parent, text="Połącz", command=self.toggle_connection)
        self.connect_button.pack(pady=5)

        # Dodanie przycisku Debug
        ttk.Button(parent, text="Debug", command=lambda: self.open_interface_window(self.root)).pack(pady=5)

    def open_interface_window(self, parent):
        new_window = tk.Toplevel(parent)
        new_window.title("Debug")
        new_window.geometry("1700x900")

        # Dodaj zawartość interfejsu Debug
        #ttk.Label(new_window, text="Debug Interface").pack(pady=10)
        Interface(new_window)

    def create_console_section(self, parent):
        self.console_frame = ttk.Frame(parent)
        self.console_frame.pack(fill=tk.BOTH, expand=True)

        self.toggle_console_button = ttk.Button(
            self.console_frame,
            text="~",
            command=self.toggle_console
        )
        self.toggle_console_button.pack(anchor="w", pady=5)

        self.console_inner_frame = ttk.Frame(self.console_frame)
        self.console_visible = False  # Flaga widoczności konsoli

        ttk.Label(self.console_inner_frame, text="Konsola").pack(anchor="w", pady=5)
        self.console_output = tk.Text(self.console_inner_frame, height=15, state="disabled")
        self.console_output.pack(fill=tk.BOTH, expand=True, pady=5)

    def toggle_console(self):
        if self.console_visible:
            # Ukryj konsolę
            self.console_inner_frame.pack_forget()
            self.toggle_console_button.config(text="~")
        else:
            # Pokaż konsolę
            self.console_inner_frame.pack(fill=tk.BOTH, expand=True)
            self.toggle_console_button.config(text="~")
        self.console_visible = not self.console_visible

    def refresh_ports(self):
        ports = self.serial_handler.get_available_ports()  # Implementacja w SerialHandler
        self.port_dropdown['values'] = ports

    def toggle_connection(self):
        if self.serial_handler.is_connected():
            self.serial_handler.disconnect()
            self.connect_button.config(text="Połącz")
        else:
            port = self.port_var.get()
            try:
                self.serial_handler.connect(port)
                self.connect_button.config(text="Rozłącz")
                self.log_output(f"Połączono z {port}.")
                self.init_after_connection()
            except Exception as e:
                self.log_output(f"Błąd połączenia: {e}")

    def init_after_connection(self):
        self.send_write_command(f"pot_wp", 1)

    def log_output(self, message):
        if not hasattr(self, 'console_output') or self.console_output is None:
            print(f"Brak konsoli: {message}")  # Jeśli konsola nie istnieje, wyświetlamy w terminalu
            return

        self.console_output.config(state="normal")
        self.console_output.insert(tk.END, message + "\n")
        self.console_output.config(state="disabled")
        self.console_output.see(tk.END)

    def create_sm1_section(self, parent):
        # Stworzenie sekcji sterowania silnikiem 1
        ttk.Label(parent, text="SM1").pack()
        sm_number = 1
        pot_number = 1
        # Tworzenie Dial
        dial = Dial(master=parent, color_gradient=("green", "red"),
                    text_color="black", text="Prędkość: ", unit_length=10, radius=50,
                    scroll=True, scroll_steps=10, start=0, end=255)
        dial.pack()

        # Monitorowanie Dial dla SM1
        self.monitor_dial(dial, sm_number, pot_number)

        # Pozostałe elementy
        self.create_checkbutton(parent, text="SD", var=self.sm1_check_var, sm=sm_number)
        self.create_radiobutton(parent, text="CW", value=1, var=self.sm1_switch_var, sm=sm_number)
        self.create_radiobutton(parent, text="Stop", value=3, var=self.sm1_switch_var, sm=sm_number)
        self.create_radiobutton(parent, text="CCW", value=2, var=self.sm1_switch_var, sm=sm_number)

    def create_sm2_section(self, parent):
        # Stworzenie sekcji sterowania silnikiem 2
        ttk.Label(parent, text="SM2").pack()
        sm_number = 2
        pot_number = 2
        # Tworzenie Dial
        dial = Dial(master=parent, color_gradient=("green", "red"),
                    text_color="black", text="Prędkość: ", unit_length=10, radius=50,
                    scroll=True, scroll_steps=10, start=0, end=255)
        dial.pack()

        # Monitorowanie Dial dla SM2
        self.monitor_dial(dial, sm_number, pot_number)

        # Pozostałe elementy
        self.create_checkbutton(parent, text="SD", var=self.sm2_check_var, sm=sm_number)
        self.create_radiobutton(parent, text="CW", value=1, var=self.sm2_switch_var, sm=sm_number)
        self.create_radiobutton(parent, text="Stop", value=3, var=self.sm2_switch_var, sm=sm_number)
        self.create_radiobutton(parent, text="CCW", value=2, var=self.sm2_switch_var, sm=sm_number)

    def monitor_dial(self, dial, sm, pot):
        # Obsługa pokrętła
        current_value = dial.get()  # Pobranie aktualnej wartości
        if not hasattr(dial, "_last_value"):
            dial._last_value = current_value
        if not hasattr(dial, "_last_sent_value"):
            dial._last_sent_value = None  # Śledzenie ostatniej wysłanej wartości

        if dial._last_value == current_value:
            # Jeśli wartość się nie zmienia i nie została jeszcze wysłana
            if dial._last_sent_value != current_value:
                self.on_dial_stop(current_value, pot=pot)
                dial._last_sent_value = current_value  # Aktualizacja ostatniej wysłanej wartości
        else:
            # Aktualizujemy ostatnią wartość
            dial._last_value = current_value

        self.root.after(500, lambda: self.monitor_dial(dial, sm, pot))

    def on_dial_stop(self, value, pot):
        # Wysłanie wiadomości po zatrzymaniu pokrętła
        self.send_write_command(f"pot_{pot}", value)

    def create_radiobutton(self, parent, text, value, var, sm):
        switch = ttk.Radiobutton(
            parent,
            text=text,
            variable=var,
            value=value,
            command=lambda: self.update_radio_status(var, sm)
        )
        switch.pack()

    def create_checkbutton(self, parent, text, var, sm):
        check = ttk.Checkbutton(
            parent,
            text=text,
            variable=var,
            command=lambda: self.update_check_status(var, sm)
        )
        check.pack()



    def update_check_status(self, var, sm):
        value = var.get()
        self.send_write_command(f"sm{sm}_sd", value)

    def update_radio_status(self, var, sm):
        selected_value = var.get()
        if selected_value == 1:
            self.send_write_command(f"sm{sm}_ccw", 0)
            self.send_write_command(f"sm{sm}_cw", 1)
        elif selected_value == 2:
            self.send_write_command(f"sm{sm}_cw", 0)
            self.send_write_command(f"sm{sm}_ccw", 1)
        elif selected_value == 3:
            self.send_write_command(f"sm{sm}_ccw", 0)
            self.send_write_command(f"sm{sm}_cw", 0)

    def create_dial(self, parent, sm):
        ttk.Label(parent, text=f"Prędkość SM{sm}").pack()
        dial = ttk.Scale(parent, from_=0, to=255, orient="horizontal")
        dial.pack(fill="x", pady=5)

    def create_hx_section(self, parent):
        ttk.Label(parent, text="Belka tensometryczna").pack()
        self.number_var_hx = tk.StringVar(value=False)
        self.create_number_window(parent, "Wartość", number_var=self.number_var_hx)
        delay = self.autoupdate_delay
        self.check_vars_hx = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            parent,
            text=f"Automatyczny odczyt interwał",
            variable=self.check_vars_hx,
            command=lambda: self.start_queue_automatic_update(var1=self.check_vars_hx ,command1="hx_read", delay=self.autoupdate_delay, window_var1=self.number_var_hx, command2="encoder_1", window_var2=self.number_var_len)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            parent,
            text="RAW",
            variable=self.hx_switch_var,
            value=1,
            command=lambda: self.update_hx_output_type(self.hx_switch_var)
        ).pack()

        ttk.Radiobutton(
            parent,
            text="5AVG",
            variable=self.hx_switch_var,
            value=2,
            command=lambda: self.update_hx_output_type(self.hx_switch_var)
        ).pack()

        ttk.Radiobutton(
            parent,
            text="10AVG",
            variable=self.hx_switch_var,
            value=3,
            command=lambda: self.update_hx_output_type(self.hx_switch_var)
        ).pack()

    def update_hx_output_type(self, var):
        selected_value = var.get()
        if selected_value == 1:
            self.hx_output_type=0
        elif selected_value == 2:
            self.hx_output_type=1
        elif selected_value == 3:
            self.hx_output_type=2


    def update_number_window(self, value, number_var):
        try:
            value_avg = float(value) if value else 0  # Konwersja wartości na float
        except ValueError:
            value_avg = self.hxdata[-1] if self.hxdata else 0  # Pobranie ostatniego elementu zamiast listy

        self.hxdata.append(value_avg)
        self.hxdata = self.hxdata[-10:]  # Ograniczenie historii do 10 wartości

        output_type = self.hx_output_type
        value = ""

        try:
            if output_type == 1 and len(self.hxdata) >= 5:
                avg_5 = sum(self.hxdata[-5:]) / len(self.hxdata[-5:])
                value = f"{avg_5:.2f}"
            elif output_type == 2 and len(self.hxdata) >= 10:
                avg_10 = sum(self.hxdata) / len(self.hxdata)
                value = f"{avg_10:.2f}"
        except TypeError:
            print(f"Błąd: hxdata={self.hxdata}")  # Debugowanie wartości listy
        number_var.set(value)

    def stop_automatic_update(self, var):
        var.set(False)  # Resetuje stan checkboxa

    def create_number_window(self, parent, text, number_var):
        ttk.Label(parent, text=text).pack()
        number_entry = ttk.Entry(parent, textvariable=number_var, font=("Courier", 14))
        number_entry.pack(fill="x", pady=5)

    def create_len_section(self, parent):
        ttk.Label(parent, text="Długość światłowodu").pack()
        self.len_translate = 200/1000
        self.number_var_len = tk.StringVar(value=False)
        self.create_number_window(parent, "Wartość [mm]", number_var=self.number_var_len)
        delay = 0.2
        self.check_vars_len = tk.BooleanVar(value=False)
        self.cmd = "encoder_1_0"
        ttk.Button(parent, text="Zeruj wartość", command=lambda: self.send_and_update(self.cmd)).pack(fill="x", pady=5)

    def start_queue_automatic_update(self, delay, command1,  window_var1, command2, window_var2, var1):
        def update():
            while var1.get():
                    response1 = self.send_and_update(command1)
                    self.update_number_window(response1, window_var1)
                    time.sleep(delay)
                    response2 = self.send_and_update(command2)
                    self.update_len_number_window(response2, window_var2)
                    time.sleep(delay)
        # Uruchamia wątek
        threading.Thread(target=update, daemon=True).start()

    def update_len_number_window(self, value, number_var):
        try:
            value_len = float(value) if value else 0  # Konwersja wartości na float
        except ValueError:
            if len(self.lendata) > 2:
                value_len = self.lendata[-1]  # Pobranie ostatniej wartości zamiast listy
            else:
                value_len = 0
        self.lendata.append(value_len)

        try:
            number_var.set(float(value_len * self.len_translate))
        except TypeError:
            print(f"Błąd konwersji: value_len={value_len}, len_translate={self.len_translate}")
            number_var.set(0)  # Ustawienie wartości domyślnej w razie błędu

    def send_write_command(self, command, value):
        if not self.serial_handler.is_connected():
            self.log_output("Błąd: Brak połączenia z portem szeregowym.")
            #self.log_to_file("Błąd: Brak połączenia z portem szeregowym.", is_error=True)
            return None

        full_command = f"{command}_{value}"  # Tworzenie pełnej komendy
        try:
            self.serial_handler.send_command(full_command)
            for attempt in range(3):
                response = self.serial_handler.read_response()
                if response:
                    # Weryfikacja odpowiedzi
                    if command in response and f"{value}" in response:
                        return response
                    else:
                        self.log_output(f"Nieprawidłowa odpowiedź: {response}")
                        return response
                self.log_output(f"Próba {attempt + 1} dla komendy {full_command} nie powiodła się.")
            self.log_output(f"Nie otrzymano odpowiedzi na komendę: {full_command}")
            return None
        except Exception as e:
            self.log_output(f"Błąd wysyłania: {e}")
            return None

    def send_and_update(self, command):
        response = self.send_command(command)
        self.log_output(f"Wysłano: {command}")
        value = self.extract_value(response) if response else "Brak odpowiedzi"
        self.log_output(f"Otrzymano: {response}")
        return value

    def send_command(self, command):
        if not self.serial_handler.is_connected():
            self.log_output("Błąd: Brak połączenia z portem szeregowym.")
            return None

        try:
            self.serial_handler.send_command(command)
            for attempt in range(3):
                response = self.serial_handler.read_response()
                if response:
                    if command.split('_')[0] in response and command in response:
                        return response
                    else:
                        self.log_output(f"Nieprawidłowa odpowiedź: {response}")
                        return response
                self.log_output(f"Próba {attempt + 1} dla komendy {command} nie powiodła się.")
            self.log_output(f"Nie otrzymano odpowiedzi na komendę: {command}")
            return None
        except Exception as e:
            self.log_output(f"Błąd wysyłania: {e}")
            return None

    def extract_value(self, response):
        try:
            if "val=" in response:
                return response.split("val=")[1].split()[0]
        except IndexError:
            return "Błąd parsowania"
        return "Brak wartości"
import tkinter as tk
import os
import threading
import time
from datetime import datetime
from tkinter import ttk, messagebox
from serial_communication import SerialHandler


class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Nawijarka Światłowodów")
        self.serial_handler = SerialHandler()

        # Inicjalizacja logów
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs", exist_ok=True)
        self.log_file = f"logs/log_{timestamp}.txt"
        self.error_file = f"logs/errors_{timestamp}.txt"

        with open(self.log_file, 'w') as log:
            log.write(f"Log aplikacji rozpoczęty: {datetime.now()}\n")
        with open(self.error_file, 'w') as err_log:
            err_log.write(f"Log błędów rozpoczęty: {datetime.now()}\n")

        # Lista komend odczytu
        self.read_commands = [
            "smc124_clk", "smc124_dir", "smc124_en", "sm2_sd", "sm2_ccw", "sm2_cw",
            "sm1_sd", "sm1_ccw", "sm1_cw", "led_blue", "led_green", "zero_1",
            "zero_2", "pot_1", "pot_2", "pot_3", "pot_4", "pot_wp", "hx_gain",
            "hx_read", "encoder_1", "encoder_2"
        ]

        self.write_commands = {
            "smc124_clk": {"type": "spinbox", "min": 0, "max": 100, "default": 50},
            "smc124_dir": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "smc124_en": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "pot_wp": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "pot_1": {"type": "spinbox", "min": 0, "max": 255, "default": 255},
            "pot_2": {"type": "spinbox", "min": 0, "max": 255, "default": 255},
            "sm1_sd": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "sm1_ccw": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "sm1_cw": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "pot_3": {"type": "spinbox", "min": 0, "max": 255, "default": 255},
            "pot_4": {"type": "spinbox", "min": 0, "max": 255, "default": 255},
            "sm2_sd": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "sm2_ccw": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "sm2_cw": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "hx_gain": {"type": "spinbox_set", "Option1": 32, "Option2": 64, "Option3": 128, "default": 64},
            "led_green": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "led_blue": {"type": "spinbox", "min": 0, "max": 1, "default": 0},
            "encoder_1": {"type": "spinbox", "min": 0, "max": 255255, "default": 0},
            "encoder_2": {"type": "spinbox", "min": 0, "max": 255255, "default": 0}
        }


        # Indeks aktualnej kolumny
        self.current_column = 0
        self.column_number = 5

        # Konfiguracja siatki dla kolumn
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=5)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=2)
        self.root.columnconfigure(4, weight=2)

        # Tworzenie interfejsu
        self.create_ui()

    def create_ui(self):
        self.add_section(self.create_port_section)
        self.add_section(self.create_buttons_section)
        self.add_section(self.create_write_buttons_section)
        self.add_section(self.create_table_section)
        self.add_section(self.create_console_section)

    def add_section(self, section_function):
        frame = ttk.Frame(self.root, padding="5")
        frame.grid(column=self.current_column, row=0, sticky="nsew")  # Umieszcza w bieżącej kolumnie
        section_function(parent=frame)  # Przekazuje kontener do funkcji tworzącej sekcję
        self.current_column = (self.current_column + 1) % self.column_number  # Przechodzi do następnej kolumny

    def create_scale_control(self, parent, command, config):
        value = tk.IntVar(value=config["default"])
        scale = ttk.Scale(
            parent,
            from_=config["min"],
            to=config["max"],
            orient="horizontal",
            variable=value,
        )
        scale.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            parent, text="Wyślij", command=lambda: self.send_write_and_update(command, value.get())
        ).pack(pady=5)

    def create_switch_control(self, parent, command, config):
        value = tk.IntVar(value=config["values"][0])
        switch = ttk.Checkbutton(
            parent, text="ON/OFF", variable=value, onvalue=config["values"][1], offvalue=config["values"][0]
        )
        switch.pack(pady=5)

        ttk.Button(
            parent, text=command, command=lambda: self.send_write_and_update(command, value.get())
        ).pack(pady=5)

    def create_spinbox_control(self, parent, command, config):
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, padx=5, pady=5)
        value = tk.IntVar(value=config["default"])
        spinbox = ttk.Spinbox(
            container,
            from_=config["min"],
            to=config["max"],
            textvariable=value,
            width=10
        )
        spinbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Button(
            container, text=command, command=lambda: self.send_write_and_update(command, value.get())
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    def create_spinbox_set_control(self, parent, command, config):
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, padx=5, pady=5)
        value = tk.IntVar(value=config["default"])
        spinbox = ttk.Spinbox(
            container,
            values=(config["Option1"],config["Option2"],config["Option3"]),
            textvariable=value,
            width=10
        )
        spinbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Button(
            container, text=command, command=lambda: self.send_write_and_update(command, value.get())
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    def create_port_section(self, parent):
        ttk.Label(parent, text="Wybierz port COM:").pack(pady=5)
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(parent, textvariable=self.port_var, state="readonly")
        self.refresh_ports()
        self.port_dropdown.pack(fill=tk.X, pady=5)
        ttk.Button(parent, text="Odśwież listę portów", command=self.refresh_ports).pack(pady=5)
        self.connect_button = ttk.Button(parent, text="Połącz", command=self.toggle_connection)
        self.connect_button.pack(pady=5)

    def create_console_section(self, parent):
        ttk.Label(parent, text="Konsola").pack(anchor="w", pady=5)
        self.console_output = tk.Text(parent, height=15, state="disabled")
        self.console_output.pack(fill=tk.BOTH, expand=True, pady=5)
        self.console_entry = ttk.Entry(parent)
        self.console_entry.pack(fill=tk.X, pady=5)
        self.console_entry.bind("<Return>", self.on_enter_command)

    def create_table_section(self, parent):
        ttk.Label(parent, text="Parametry").pack(anchor="w", pady=4)

        # Tworzenie Treeview z dodatkowymi kolumnami
        self.tree = ttk.Treeview(
            parent,
            columns=("lp", "nazwa_typ", "wartosc", "srednia_5", "srednia_10"),
            show="headings",
        )
        self.tree.heading("lp", text="Lp")
        self.tree.heading("nazwa_typ", text="Nazwa Typ")
        self.tree.heading("wartosc", text="Wartość")
        self.tree.heading("srednia_5", text="Średnia (5)")
        self.tree.heading("srednia_10", text="Średnia (10)")

        # Automatyczne dopasowanie szerokości kolumn
        for col in ("lp", "nazwa_typ", "wartosc", "srednia_5", "srednia_10"):
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Inicjalizacja danych dla tabeli
        self.command_data = {cmd: [] for cmd in self.read_commands}
        for i, command in enumerate(self.read_commands, start=1):
            self.tree.insert("", "end", values=(i, command, "", "", ""))

    def create_buttons_section(self, parent):
        ttk.Label(parent, text="Odczyt").pack(anchor="w", pady=5)
        ttk.Button(parent, text="Wyślij wszystkie", command=self.send_all_commands).pack(fill=tk.X, pady=5)

        # Zmienna słownikowa do przechowywania stanu checkboxów
        self.check_vars = {}

        # Dodawanie przycisków z checkboxami
        for command in self.read_commands:
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=2, anchor="w")

            # Przycisk do ręcznego wysłania komendy
            ttk.Button(frame, text=command, command=lambda cmd=command: self.send_and_update(cmd)).pack(side=tk.LEFT,
                                                                                                        padx=5)

            # Checkbox
            self.check_vars[command] = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                frame,
                text="Autoupdate",
                variable=self.check_vars[command],
                command=lambda cmd=command: self.toggle_automatic_update(cmd)
            ).pack(side=tk.LEFT, padx=5)

    def toggle_automatic_update(self, command):
        if self.check_vars[command].get():  # Jeśli checkbox jest zaznaczony
            self.start_automatic_update(command)
        else:  # Jeśli checkbox został odznaczony
            self.stop_automatic_update(command)

    def start_automatic_update(self, command):
        def update():
            delay = 100  # Pierwsze opóźnienie
            command_index = self.read_commands.index(command)  # Pobranie indeksu komendy
            while self.check_vars[command].get():
                self.send_and_update(command)
                time.sleep(delay / 1000)  # Opóźnienie w sekundach
                delay += 50  # Zwiększenie opóźnienia o 50 ms dla każdej iteracji

                # Zresetowanie opóźnienia, jeśli przekroczy 1000 ms
                if delay > 1000:
                    delay = 100

        # Rozpoczęcie wątku
        threading.Thread(target=update, daemon=True).start()

    def stop_automatic_update(self, command):
        self.check_vars[command].set(False)  # Resetuje stan checkboxa

    def create_write_buttons_section(self, parent):

        ttk.Label(parent, text="Zapis").pack(anchor="w", pady=5)
        for command, config in self.write_commands.items():
            # Kontener dla pojedynczej komendy
            cmd_frame = ttk.LabelFrame(parent, text=command, padding="5")
            cmd_frame.pack(fill=tk.X, padx=5, pady=5)

            # Dodaj kontrolkę w zależności od typu
            if config["type"] == "scale":
                self.create_scale_control(parent, command, config)
            elif config["type"] == "switch":
                self.create_switch_control(parent, command, config)
            elif config["type"] == "spinbox":
                self.create_spinbox_control(parent, command, config)
            elif config["type"] == "spinbox_set":
                self.create_spinbox_set_control(parent, command, config)

    def refresh_ports(self):
        ports = self.serial_handler.get_available_ports()
        self.port_dropdown['values'] = ports

    def toggle_connection(self):
        if self.serial_handler.is_connected():
            self.serial_handler.disconnect()
            self.connect_button.config(text="Połącz")
            self.log_output("Rozłączono z portem szeregowym.")
        else:
            port = self.port_var.get()
            try:
                self.serial_handler.connect(port)
                self.connect_button.config(text="Rozłącz")
                self.log_output(f"Połączono z {port} przy prędkości {self.serial_handler.baudrate} baud.")
            except Exception as e:
                messagebox.showerror("Błąd połączenia", f"Nie udało się połączyć: {e}")

    def send_command(self, command):
        if not self.serial_handler.is_connected():
            self.log_output("Błąd: Brak połączenia z portem szeregowym.")
            self.log_to_file("Błąd: Brak połączenia z portem szeregowym.", is_error=True)
            return None

        try:
            self.serial_handler.send_command(command)
            self.log_to_file(f"Wysłano komendę: {command}")
            for attempt in range(3):
                response = self.serial_handler.read_response()
                if response:
                    self.log_to_file(f"Odebrano wiadomość: {response}")
                    if command.split('_')[0] in response and command in response:
                        return response
                    else:
                        self.log_output(f"Nieprawidłowa odpowiedź: {response}")
                        self.log_to_file(f"Nieprawidłowa odpowiedź dla komendy {command}: {response}", is_error=True)
                        return response
                self.log_output(f"Próba {attempt + 1} dla komendy {command} nie powiodła się.")
            self.log_output(f"Nie otrzymano odpowiedzi na komendę: {command}")
            self.log_to_file(f"Nie otrzymano odpowiedzi na komendę: {command}. Odpowiedź: Brak", is_error=True)
            return None
        except Exception as e:
            self.log_output(f"Błąd wysyłania: {e}")
            self.log_to_file(f"Błąd wysyłania: {e}", is_error=True)
            return None

    def send_write_command(self, command, value):
        if not self.serial_handler.is_connected():
            self.log_output("Błąd: Brak połączenia z portem szeregowym.")
            self.log_to_file("Błąd: Brak połączenia z portem szeregowym.", is_error=True)
            return None

        full_command = f"{command}_{value}"  # Tworzenie pełnej komendy
        try:
            self.serial_handler.send_command(full_command)
            self.log_to_file(f"Wysłano komendę: {full_command}")
            for attempt in range(3):
                response = self.serial_handler.read_response()
                if response:
                    self.log_to_file(f"Odebrano wiadomość: {response}")
                    # Weryfikacja odpowiedzi
                    if command in response and f"{value}" in response:
                        return response
                    else:
                        self.log_output(f"Nieprawidłowa odpowiedź: {response}")
                        self.log_to_file(f"Nieprawidłowa odpowiedź dla komendy {full_command}: {response}",
                                         is_error=True)
                        return response
                self.log_output(f"Próba {attempt + 1} dla komendy {full_command} nie powiodła się.")
            self.log_output(f"Nie otrzymano odpowiedzi na komendę: {full_command}")
            self.log_to_file(f"Nie otrzymano odpowiedzi na komendę: {full_command}. Odpowiedź: Brak", is_error=True)
            return None
        except Exception as e:
            self.log_output(f"Błąd wysyłania: {e}")
            self.log_to_file(f"Błąd wysyłania: {e}", is_error=True)
            return None

    def send_write_and_update(self, command, value):
        response = self.send_write_command(command, value)
        self.log_output(f"Wysłano: {command}_{value}")
        if "done ok" in response:
            self.update_table(command, value)
        else: self.update_table(command, "Błąd")
        self.log_output(f"Otrzymano: {response}")



    def send_and_update(self, command):
        response = self.send_command(command)
        self.log_output(f"Wysłano: {command}")
        value = self.extract_value(response) if response else "Brak odpowiedzi"
        self.log_output(f"Otrzymano: {response}")
        self.update_table(command, value)

    def send_all_commands(self):
        for command in self.read_commands:
            self.send_and_update(command)

    def update_table(self, command, value):
        try:
            if command == "encoder_1" or command == "encoder_2":
                value = float(200/1000)*int(value)
            value_avg = float(value) if value else 0  # Konwersja wartości na float
            self.command_data[command].append(value_avg)
            self.command_data[command] = self.command_data[command][-10:]

            # Obliczenie średnich
            avg_5 = sum(self.command_data[command][-5:]) / len(self.command_data[command][-5:]) if len(
                self.command_data[command]) >= 5 else ""
            avg_10 = sum(self.command_data[command]) / len(self.command_data[command]) if len(
                self.command_data[command]) >= 10 else ""
        except ValueError:
            avg_5= ""
            avg_10= ""

        # Aktualizacja danych w tabeli
        for child in self.tree.get_children():
            item = self.tree.item(child)
            if item["values"][1] == command:
                self.tree.item(
                    child,
                    values=(
                        item["values"][0],  # lp
                        command,  # nazwa_typ
                        value,  # wartosc
                        f"{avg_5:.2f}" if avg_5 else "",  # srednia_5
                        f"{avg_10:.2f}" if avg_10 else "",  # srednia_10
                    ),
                )
                return

    def extract_value(self, response):
        try:
            if "val=" in response:
                return response.split("val=")[1].split()[0]
        except IndexError:
            return "Błąd parsowania"
        return "Brak wartości"

    def log_output(self, message):
        self.console_output.config(state="normal")
        self.console_output.insert(tk.END, message + "\n")
        self.console_output.config(state="disabled")
        self.console_output.see(tk.END)

    def on_enter_command(self, event):
        command = self.console_entry.get()
        if command.strip():
            self.console_entry.delete(0, tk.END)
            self.send_and_update(command)

    def log_to_file(self, message, is_error=False):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        if is_error:
            with open(self.error_file, 'a') as err_log:
                err_log.write(f"[{timestamp}] {message}\n")
        with open(self.log_file, 'a') as log:
            log.write(f"[{timestamp}] {message}\n")
import sys
import os
import subprocess
import platform
import threading
import customtkinter as ctk  

# Настройка темы интерфейса (Темная тема и стильный сине-голубой акцент)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ServerPingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dev-Инструмент: Проверка скорости ответа серверов")
        self.geometry("700x500")
        self.resizable(False, False)

        # Список пустой при старте, чтобы приложение открывалось мгновенно
        self.servers = [
            {"url": "google.com", "time": "Ожидание..."},
            {"url": "github.com", "time": "Ожидание..."},
            {"url": "yandex.ru", "time": "Ожидание..."},
            {"url": "8.8.8.8", "time": "Ожидание..."},
            {"url": "1.1.1.1", "time": "Ожидание..."}
        ]

        self.setup_ui()
        self.update_table()

    def setup_ui(self):
        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Пингование и проверка скорости серверов", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(pady=15)

        # Блок добавления нового сервера
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, fill="x", padx=20)

        self.server_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ведите адрес сайта или IP (например, amazon.com)", width=400)
        self.server_entry.pack(side="left", padx=10, pady=10)

        self.add_btn = ctk.CTkButton(self.input_frame, text="Добавить в список", command=self.add_server, width=120)
        self.add_btn.pack(side="left", padx=5, pady=10)

        # Контейнер для таблицы
        self.table_frame = ctk.CTkScrollableFrame(self, width=640, height=260)
        self.table_frame.pack(pady=10, padx=20)

        # Панель управления (Кнопки внизу)
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.pack(pady=15, fill="x", padx=20)

        self.ping_btn = ctk.CTkButton(self.control_frame, text="⚡ Проверить скорость", command=self.start_ping_thread, fg_color="#228B22", hover_color="#006400")
        self.ping_btn.pack(side="left", padx=10)

        self.sort_btn = ctk.CTkButton(self.control_frame, text="⇅ Сортировать по скорости", command=self.sort_servers)
        self.sort_btn.pack(side="left", padx=10)

        self.clear_btn = ctk.CTkButton(self.control_frame, text="Очистить список", command=self.clear_list, fg_color="#8B0000", hover_color="#550000")
        self.clear_btn.pack(side="right", padx=10)

    def update_table(self):
        # Очищаем старые элементы из виджета таблицы
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Шапка таблицы
        hdr_url = ctk.CTkLabel(self.table_frame, text="Адрес сервера / IP", font=ctk.CTkFont(weight="bold"), anchor="w")
        hdr_url.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        
        hdr_time = ctk.CTkLabel(self.table_frame, text="Время отклика", font=ctk.CTkFont(weight="bold"), anchor="e")
        hdr_time.grid(row=0, column=1, padx=20, pady=5, sticky="ew")

        self.table_frame.grid_columnconfigure(0, weight=3)
        self.table_frame.grid_columnconfigure(1, weight=1)

        # Заполнение данными
        for idx, server in enumerate(self.servers, start=1):
            bg_color = "#2B2B2B" if idx % 2 == 0 else "#202020"
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color, corner_radius=0)
            row_frame.grid(row=idx, column=0, columnspan=2, sticky="ew", pady=2)
            row_frame.grid_columnconfigure(0, weight=3)
            row_frame.grid_columnconfigure(1, weight=1)

            lbl_name = ctk.CTkLabel(row_frame, text=server["url"], anchor="w")
            lbl_name.grid(row=0, column=0, padx=20, pady=6, sticky="w")

            time_text = server["time"]
            if "мс" in time_text:
                ms_val = int(time_text.replace(" мс", ""))
                text_color = "#32CD32" if ms_val < 50 else ("#FF8C00" if ms_val < 150 else "#FF4500")
            elif time_text == "Не доступен":
                text_color = "#FF4500"
            else:
                text_color = "#888888"

            lbl_val = ctk.CTkLabel(row_frame, text=time_text, text_color=text_color, anchor="e", font=ctk.CTkFont(weight="bold"))
            lbl_val.grid(row=0, column=1, padx=20, pady=6, sticky="e")

    def add_server(self):
        url = self.server_entry.get().strip()
        if url:
            self.servers.append({"url": url, "time": "Ожидание..."})
            self.server_entry.delete(0, 'end')
            self.update_table()

    def clear_list(self):
        self.servers = []
        self.update_table()

    def ping_server(self, host):
        # Настройка параметров под Windows (-n 1) или Unix (-c 1)
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        
        try:
            startupinfo = None
            if platform.system().lower() == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Запускаем пинг и принудительно декодируем вывод в правильном формате Windows (cp866)
            raw_output = subprocess.check_output(command, startupinfo=startupinfo, stderr=subprocess.STDOUT)
            output = raw_output.decode('cp866', errors='ignore').lower()
            
            # Ищем время отклика в русском или английском выводе
            if "время=" in output:
                time_part = output.split("время=")[1].split("мс")[0].strip()
                return f"{time_part} мс"
            elif "time=" in output:
                time_part = output.split("time=")[1].split("ms")[0].strip()
                # Если пинг вернулся с точкой (например, 12.5), округляем
                return f"{int(float(time_part))} мс"
                
        except Exception as e:
            return "Не доступен"
        return "Не доступен"
    
    def run_pings(self):
        self.ping_btn.configure(state="disabled", text="⏳ Проверка...")
        for server in self.servers:
            server["time"] = self.ping_server(server["url"])
            self.update_table()
        self.ping_btn.configure(state="normal", text="⚡ Проверить скорость")

    def start_ping_thread(self):
        threading.Thread(target=self.run_pings, daemon=True).start()

    def sort_servers(self):
        def sort_key(server):
            t = server["time"]
            if "мс" in t:
                return int(t.replace(" мс", ""))
            return 999999
            
        self.servers.sort(key=sort_key)
        self.update_table()

if __name__ == "__main__":
    app = ServerPingApp()
    app.mainloop()
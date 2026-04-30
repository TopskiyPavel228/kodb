import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary (Дневник погоды)")
        self.root.geometry("800x600")

        # Список записей
        self.entries = []

        # --- Интерфейс ввода ---
        input_frame = ttk.LabelFrame(root, text="Новая запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.temp_entry = ttk.Entry(input_frame)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=2)

        # Описание
        ttk.Label(input_frame, text="Описание погоды:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=2)

        # Осадки
        ttk.Label(input_frame, text="Осадки:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.precip_var = tk.BooleanVar(value=False)
        self.precip_check = ttk.Checkbutton(input_frame, text="Да", variable=self.precip_var)
        self.precip_check.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить запись", command=self.add_entry)
        add_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Интерфейс фильтрации ---
        filter_frame = ttk.LabelFrame(root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Мин. температура (°C):").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_temp_entry = ttk.Entry(filter_frame)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)

        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=0, column=4, padx=10)

        reset_btn = ttk.Button(filter_frame, text="Сброс", command=self.reset_filter)
        reset_btn.grid(row=0, column=5, padx=5)

        # --- Таблица записей ---
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")

        self.tree.column("date", width=100)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=300)
        self.tree.column("precip", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # --- Кнопки сохранения/загрузки ---
        file_frame = ttk.Frame(root)
        file_frame.pack(fill="x", padx=10, pady=5)

        save_btn = ttk.Button(file_frame, text="Сохранить в JSON", command=self.save_to_json)
        save_btn.pack(side=tk.LEFT, padx=5)

        load_btn = ttk.Button(file_frame, text="Загрузить из JSON", command=self.load_from_json)
        load_btn.pack(side=tk.LEFT, padx=5)

    def validate_input(self, date_str, temp_str, desc_str):
        """Проверка корректности ввода"""
        # Проверка даты
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            return False

        # Проверка температуры
        try:
            float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return False

        # Проверка описания
        if not desc_str.strip():
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
            return False

        return True

    def add_entry(self):
        date_str = self.date_entry.get()
        temp_str = self.temp_entry.get()
        desc_str = self.desc_entry.get()
        precip = self.precip_var.get()

        if not self.validate_input(date_str, temp_str, desc_str):
            return

        entry = {
            "date": date_str,
            "temperature": float(temp_str),
            "description": desc_str,
            "precipitation": precip
        }

        self.entries.append(entry)
        self.refresh_table()

        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def refresh_table(self, data=None):
        """Обновление таблицы"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data is None:
            data = self.entries

        for entry in data:
            precip_str = "Да" if entry["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                precip_str
            ))

    def apply_filter(self):
        date_filter = self.filter_date_entry.get().strip()
        temp_filter = self.filter_temp_entry.get().strip()

        filtered = self.entries

        # Фильтр по дате
        if date_filter:
            try:
                datetime.strptime(date_filter, "%d.%m.%Y")
                filtered = [e for e in filtered if e["date"] == date_filter]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Неверный формат даты в фильтре")
                return

        # Фильтр по температуре
        if temp_filter:
            try:
                min_temp = float(temp_filter)
                filtered = [e for e in filtered if e["temperature"] > min_temp]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Температура в фильтре должна быть числом")
                return

        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()

    def save_to_json(self):
        filename = "weather_data.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_from_json(self):
        filename = "weather_data.json"
        if not os.path.exists(filename):
            messagebox.showwarning("Предупреждение", "Файл weather_data.json не найден")
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            self.refresh_table()
            messagebox.showinfo("Успех", "Данные загружены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()

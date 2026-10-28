import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime

class IndustrialSCADA:
    def __init__(self, root):
        self.root = root
        self.root.title("System SCADA & DBMS v7.0")
        self.root.geometry("1200x800")
        
        self.db_name = "przemyslowa_baza.db"
        self.conn = None
        self.cursor = None
        self.init_db()

        # --- GÓRA: TYTUŁ ---
        top_frame = tk.Frame(root, bg="#2c3e50", height=60)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="🏭 SYSTEM NADZORU PRODUKCJI (SCADA)", 
                 bg="#2c3e50", fg="white", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=20, pady=10)

        # --- ZAKŁADKI (TABS) ---
        # To jest kluczowe dla wymogu "Aplikacja SCADA"
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tworzymy dwie główne zakładki
        self.tab_db = tk.Frame(self.notebook)
        self.tab_scada = tk.Frame(self.notebook)

        self.notebook.add(self.tab_db, text="📁 BAZA DANYCH (REJESTR)")
        self.notebook.add(self.tab_scada, text="🖥️ WIZUALIZACJA PROCESU (SCADA)")

        # === BUDOWANIE ZAKŁADKI 1: BAZA DANYCH ===
        self.build_db_tab()

        # === BUDOWANIE ZAKŁADKI 2: WIZUALIZACJA ===
        self.build_scada_tab()

        # Załaduj dane na start
        self.load_data()

    def init_db(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS Pomiary (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    czujnik TEXT,
                                    wartosc REAL,
                                    jednostka TEXT,
                                    status TEXT,
                                    data_czas TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Błąd Bazy", f"Nie można połączyć z bazą danych:\n{e}")

    # ------------------------------------------------------------------
    # BUDOWA ZAKŁADKI 1 (Tabela i Formularze - to co było wcześniej)
    # ------------------------------------------------------------------
    def build_db_tab(self):
        # Układ
        main_split = tk.Frame(self.tab_db)
        main_split.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # LEWA STRONA (TABELA)
        left_panel = tk.Frame(main_split)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Pasek szukania
        search_frame = tk.Frame(left_panel)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(search_frame, text="🔍 Filtruj (Czujnik):", font=("Arial", 10)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_data)
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)

        # Tabela
        columns = ("ID", "Czujnik", "Wartość", "Jednostka", "Status", "Data/Czas")
        self.tree = ttk.Treeview(left_panel, columns=columns, show='headings', selectmode='browse')
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID": self.tree.column(col, width=50, anchor="center")
            else: self.tree.column(col, width=110, anchor="center")

        self.tree.tag_configure('ALARM', background='#ffcccc', foreground='red')
        self.tree.tag_configure('WARNING', background='#fff4cc')
        self.tree.tag_configure('OK', background='white')

        scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # PRAWA STRONA (STATYSTYKI)
        right_panel = tk.Frame(main_split, width=280, bg="#ecf0f1", relief=tk.RAISED, borderwidth=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)

        tk.Label(right_panel, text="📊 STATYSTYKI", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=10)
        self.lbl_total = tk.Label(right_panel, text="Liczba wpisów: 0", bg="white", width=30, pady=5)
        self.lbl_total.pack(pady=5)
        self.lbl_alarms = tk.Label(right_panel, text="Błędy (ALARM): 0", bg="white", fg="red", width=30, pady=5)
        self.lbl_alarms.pack(pady=5)
        self.lbl_avg = tk.Label(right_panel, text="Średnia: 0.0", bg="white", fg="blue", width=30, pady=5)
        self.lbl_avg.pack(pady=5)

        tk.Label(right_panel, text="📂 PLIKI", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=(30, 10))
        tk.Button(right_panel, text="📥 IMPORT CSV", command=self.import_csv, bg="#2980b9", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=10, pady=5)
        tk.Button(right_panel, text="💾 EXPORT CSV", command=self.export_csv, bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, padx=10, pady=5)
        tk.Button(right_panel, text="🗑 WYCZYŚĆ BAZĘ", command=self.clear_all_data, bg="#7f8c8d", fg="white").pack(fill=tk.X, padx=10, pady=20)

        # DÓŁ (FORMULARZ)
        control_frame = tk.LabelFrame(self.tab_db, text="Edycja Danych", padx=10, pady=10, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(control_frame, text="Czujnik:", bg="#f0f0f0").grid(row=0, column=0)
        self.entry_czujnik = tk.Entry(control_frame)
        self.entry_czujnik.grid(row=0, column=1, padx=5)

        tk.Label(control_frame, text="Wartość:", bg="#f0f0f0").grid(row=0, column=2)
        self.entry_wartosc = tk.Entry(control_frame, width=10)
        self.entry_wartosc.grid(row=0, column=3, padx=5)

        tk.Label(control_frame, text="Jednostka:", bg="#f0f0f0").grid(row=0, column=4)
        self.combo_jednostka = ttk.Combobox(control_frame, values=["C", "Bar", "RPM", "%", "V"], width=5)
        self.combo_jednostka.current(0)
        self.combo_jednostka.grid(row=0, column=5, padx=5)

        tk.Label(control_frame, text="Status:", bg="#f0f0f0").grid(row=0, column=6)
        self.combo_status = ttk.Combobox(control_frame, values=["OK", "WARNING", "ALARM"], width=10)
        self.combo_status.current(0)
        self.combo_status.grid(row=0, column=7, padx=5)

        tk.Button(control_frame, text="➕ DODAJ", command=self.add_record, bg="#333", fg="white", width=15).grid(row=0, column=8, padx=20)
        tk.Button(control_frame, text="❌ USUŃ ZAZNACZONY", command=self.delete_selected, bg="#c0392b", fg="white").grid(row=0, column=9, padx=5)

    # ------------------------------------------------------------------
    # BUDOWA ZAKŁADKI 2 (WIZUALIZACJA SCADA)
    # ------------------------------------------------------------------
    def build_scada_tab(self):
        # Tło w kolorze przemysłowym (ciemnoszary)
        self.canvas = tk.Canvas(self.tab_scada, bg="#2c3e50", width=1100, height=650)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Rysowanie tła hali / rur
        # Rura dolotowa
        self.canvas.create_rectangle(50, 100, 300, 140, fill="#7f8c8d", outline="black")
        self.canvas.create_text(100, 80, text="DOPŁYW MEDIÓW", fill="white", font=("Arial", 10))

        # ZBIORNIK GŁÓWNY (Ramka)
        self.tank_x, self.tank_y, self.tank_w, self.tank_h = 300, 100, 600, 400
        self.canvas.create_rectangle(self.tank_x, self.tank_y, 
                                     self.tank_x + self.tank_w, self.tank_y + self.tank_h, 
                                     outline="white", width=4)
        
        # WODA W ZBIORNIKU (Zmienna wysokość) - ID=tag_water
        # Początkowo pusty
        self.water_rect = self.canvas.create_rectangle(self.tank_x+5, self.tank_y + self.tank_h, 
                                                       self.tank_x + self.tank_w - 5, self.tank_y + self.tank_h, 
                                                       fill="#3498db", outline="")
        
        # Podpisy zbiornika
        self.canvas.create_text(self.tank_x + 150, self.tank_y - 20, text="ZBIORNIK PROCESOWY ZB-01", fill="white", font=("Arial", 14, "bold"))

        # WIZUALIZACJA STATUSU (LAMPKA)
        self.canvas.create_oval(700, 50, 750, 100, fill="gray", outline="white", width=2, tags="status_light")
        self.canvas.create_text(725, 120, text="STATUS PRACY", fill="white", font=("Arial", 10))

        # WYSWIETLACZ CYFROWY (Ostatni pomiar)
        self.canvas.create_rectangle(700, 200, 900, 300, fill="black", outline="#27ae60", width=3)
        self.display_text = self.canvas.create_text(800, 230, text="---", fill="#2ecc71", font=("Courier New", 24, "bold"))
        self.display_label = self.canvas.create_text(800, 270, text="OSTATNI ODCZYT", fill="white", font=("Arial", 10))

        # Opis
        self.canvas.create_text(580, 550, text="Wizualizacja SCADA odświeża się automatycznie na podstawie ostatniego rekordu w bazie.", 
                                fill="#bdc3c7", font=("Arial", 10, "italic"))

    # ------------------------------------------------------------------
    # LOGIKA (Backend)
    # ------------------------------------------------------------------
    def update_scada_view(self, last_row):
        """Aktualizuje grafikę na podstawie ostatniego wiersza z bazy"""
        if not last_row:
            return

        # Rozpakuj dane: ID, Czujnik, Wartość, Jednostka, Status, Data
        try:
            val = float(last_row[2])
            status = last_row[4]
            unit = last_row[3]
            sensor_name = last_row[1]
        except:
            return

        # 1. Animacja poziomu cieczy (Symulacja na podstawie wartości)
        # Zakładamy że max wartość to np. 250 (dla celów wizualizacji)
        max_val = 300.0 
        percent = min(val / max_val, 1.0) # max 100%
        fill_height = self.tank_h * percent
        
        # Aktualizacja koordynatów wody (x0, y0, x1, y1)
        # Woda rośnie od dołu (y + h) w górę (y + h - fill)
        self.canvas.coords(self.water_rect, 
                           self.tank_x+5, self.tank_y + self.tank_h - fill_height, 
                           self.tank_x + self.tank_w - 5, self.tank_y + self.tank_h)

        # Zmiana koloru cieczy w zależności od statusu
        color = "#3498db" # Niebieski (OK)
        if status == "WARNING": color = "#f1c40f" # Żółty
        if status in ["ALARM", "CRITICAL"]: color = "#e74c3c" # Czerwony
        self.canvas.itemconfig(self.water_rect, fill=color)

        # 2. Aktualizacja Lampki
        light_color = "#2ecc71" # Zielony
        if status != "OK": light_color = "#e74c3c" # Czerwony
        self.canvas.itemconfig("status_light", fill=light_color)

        # 3. Aktualizacja Wyświetlacza
        self.canvas.itemconfig(self.display_text, text=f"{val} {unit}")
        self.canvas.itemconfig(self.display_label, text=f"{sensor_name} ({status})")

    def load_data(self, filter_text=""):
        # Czyszczenie tabeli
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Zapytanie do bazy
        try:
            if filter_text:
                query = "SELECT * FROM Pomiary WHERE czujnik LIKE ? ORDER BY id DESC"
                self.cursor.execute(query, (f'%{filter_text}%',))
            else:
                self.cursor.execute("SELECT * FROM Pomiary ORDER BY id DESC")
            
            rows = self.cursor.fetchall()
        except Exception as e:
            return # Błąd bazy przy starcie

        # Statystyki
        alarm_cnt = 0
        total_val = 0.0
        
        for row in rows:
            status = row[4]
            val = row[2]
            
            tag = 'OK'
            if status in ['ALARM', 'CRITICAL']: tag = 'ALARM'
            elif status == 'WARNING': tag = 'WARNING'
            
            self.tree.insert("", tk.END, values=row, tags=(tag,))
            
            if status in ['ALARM', 'CRITICAL']: alarm_cnt += 1
            total_val += val

        # Aktualizacja etykiet
        count = len(rows)
        avg = round(total_val / count, 2) if count > 0 else 0.0
        
        self.lbl_total.config(text=f"Liczba wpisów: {count}")
        self.lbl_alarms.config(text=f"Błędy (ALARM): {alarm_cnt}")
        self.lbl_avg.config(text=f"Średnia: {avg}")

        # AKTUALIZACJA SCADA (Bierzemy najnowszy wpis - pierwszy na liście)
        if rows:
            self.update_scada_view(rows[0])

    def filter_data(self, *args):
        self.load_data(self.search_var.get())

    def add_record(self):
        try:
            c, w, j, s = self.entry_czujnik.get(), self.entry_wartosc.get(), self.combo_jednostka.get(), self.combo_status.get()
            if not c: return
            self.cursor.execute("INSERT INTO Pomiary (czujnik, wartosc, jednostka, status) VALUES (?, ?, ?, ?)", (c, float(w), j, s))
            self.conn.commit()
            self.load_data()
            self.entry_czujnik.delete(0, tk.END)
            self.entry_wartosc.delete(0, tk.END)
        except ValueError: messagebox.showerror("Błąd", "Wartość musi być liczbą!")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        if not messagebox.askyesno("Potwierdzenie", "Usunąć wpis?"): return
        try:
            rid = self.tree.item(sel[0])['values'][0]
            self.cursor.execute("DELETE FROM Pomiary WHERE id=?", (rid,))
            self.conn.commit()
            self.load_data()
        except Exception as e: messagebox.showerror("Błąd", str(e))

    def clear_all_data(self):
        if messagebox.askyesno("Uwaga", "Wyczyścić całą bazę?"):
            self.cursor.execute("DELETE FROM Pomiary")
            self.conn.commit()
            self.load_data()

    def export_csv(self):
        # POPRAWIONA FUNKCJA EKSPORTU
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Pliki CSV", "*.csv")])
            if not filename: return # Anulowano

            # Pobierz aktualne dane z bazy (świeży kursor)
            self.cursor.execute("SELECT * FROM Pomiary")
            rows = self.cursor.fetchall()

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["ID", "Czujnik", "Wartość", "Jednostka", "Status", "Data"])
                writer.writerows(rows)
            
            messagebox.showinfo("Sukces", "Dane zapisane poprawnie!")
            
        except PermissionError:
            messagebox.showerror("Błąd Pliku", "Nie można zapisać pliku!\nSprawdź czy nie jest otwarty w Excelu.")
        except Exception as e:
            messagebox.showerror("Błąd Krytyczny", str(e))

    def import_csv(self):
        try:
            filename = filedialog.askopenfilename(filetypes=[("Pliki CSV", "*.csv")])
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    next(reader, None)
                    data = []
                    for row in reader:
                        if len(row) >= 4:
                            c, w, j, s = (row[1], row[2], row[3], row[4]) if len(row)==6 else (row[0], row[1], row[2], row[3])
                            data.append((c, float(w), j, s))
                    if data:
                        self.cursor.executemany("INSERT INTO Pomiary (czujnik, wartosc, jednostka, status) VALUES (?, ?, ?, ?)", data)
                        self.conn.commit()
                        self.load_data()
                        messagebox.showinfo("Sukces", f"Zaimportowano {len(data)} rekordów")
        except Exception as e: messagebox.showerror("Błąd", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = IndustrialSCADA(root)
    root.mainloop()
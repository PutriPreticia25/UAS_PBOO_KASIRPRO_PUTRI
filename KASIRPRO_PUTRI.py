import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


class KasirProFixed:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 KASIR PRO - FIXED VERSION")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1a1a2e')

        # =====================
        # INISIALISASI DATA (WAJIB)
        # =====================
        self.cart = []
        self.total = 0
        self.use_json = False

        self.init_database()
        self.create_widgets()
        self.refresh_produk()

    # =====================
    # DATABASE
    # =====================
    def init_database(self):
        try:
            self.conn = sqlite3.connect('kasir_pro.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS produk (
                    id INTEGER PRIMARY KEY,
                    barcode TEXT UNIQUE,
                    nama TEXT,
                    harga INTEGER,
                    stok INTEGER
                )
            ''')

            sample_data = [
                ('001', 'Beras Premium 5kg', 45000, 50),
                ('002', 'Minyak Fortuna 1L', 22000, 30),
                ('003', 'Telur Ayam 1kg', 28000, 20),
                ('004', 'Gula Putih 1kg', 15000, 40),
                ('005', 'Sabun Lifebuoy', 8000, 100),
                ('007', 'Indomie Goreng', 3500, 200),
                ('008', 'Susu Ultra Milk', 10000, 80)
            ]

            self.cursor.executemany(
                'INSERT OR IGNORE INTO produk (barcode, nama, harga, stok) VALUES (?, ?, ?, ?)',
                sample_data
            )
            self.conn.commit()

        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            self.use_json = True

    # =====================
    # GUI
    # =====================
    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="💰 KASIR PRO - SISTEM KASIR MODERN",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        title.pack(pady=10)

        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill='both', expand=True, padx=20)

        # LEFT
        left = tk.Frame(main, bg='#162447')
        left.pack(side='left', fill='both', expand=True, padx=5)

        input_frame = tk.LabelFrame(left, text="SCAN BARCODE", bg='#162447', fg='white')
        input_frame.pack(fill='x', padx=10, pady=10)

        self.barcode_entry = tk.Entry(input_frame, font=('Arial', 14))
        self.barcode_entry.pack(side='left', padx=5)
        self.barcode_entry.bind('<Return>', self.add_barcode)

        tk.Button(input_frame, text="TAMBAH", command=self.add_barcode).pack(side='left')

        self.produk_listbox = tk.Listbox(left, height=15, font=('Consolas', 11))
        self.produk_listbox.pack(fill='both', expand=True, padx=10)
        self.produk_listbox.bind('<Double-1>', self.add_from_list)

        # RIGHT
        right = tk.Frame(main, bg='#162447')
        right.pack(side='right', fill='both', expand=True, padx=5)

        self.cart_listbox = tk.Listbox(right, height=15, font=('Consolas', 11))
        self.cart_listbox.pack(fill='both', expand=True, padx=10, pady=10)

        self.total_label = tk.Label(
            right,
            text="TOTAL: Rp 0",
            font=('Arial', 18, 'bold'),
            bg='#162447',
            fg='#00ff88'
        )
        self.total_label.pack(pady=10)

        tk.Button(right, text="BAYAR TUNAI", command=self.bayar_tunai).pack(fill='x', padx=10)
        tk.Button(right, text="BAYAR DEBIT", command=self.bayar_debit).pack(fill='x', padx=10)
        tk.Button(right, text="LAPORAN", command=self.laporan).pack(fill='x', padx=10)

    # =====================
    # LOGIC
    # =====================
    def refresh_produk(self):
        self.produk_listbox.delete(0, tk.END)
        self.cursor.execute('SELECT barcode, nama, harga FROM produk')
        for b, n, h in self.cursor.fetchall():
            self.produk_listbox.insert(tk.END, f"{b} | {n} | Rp {h:,}")

    def add_barcode(self, event=None):
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return

        self.cursor.execute(
            'SELECT nama, harga FROM produk WHERE barcode=?',
            (barcode,)
        )
        result = self.cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Produk tidak ditemukan")
            return

        nama, harga = result
        self.add_to_cart(barcode, nama, harga)
        self.barcode_entry.delete(0, tk.END)

    def add_from_list(self, event):
        item = self.produk_listbox.get(self.produk_listbox.curselection())
        barcode = item.split('|')[0].strip()
        self.add_barcode_manual(barcode)

    def add_barcode_manual(self, barcode):
        self.barcode_entry.insert(0, barcode)
        self.add_barcode()

    def add_to_cart(self, barcode, nama, harga):
        for item in self.cart:
            if item['barcode'] == barcode:
                item['qty'] += 1
                item['subtotal'] = item['qty'] * harga
                break
        else:
            self.cart.append({
                'barcode': barcode,
                'nama': nama,
                'harga': harga,
                'qty': 1,
                'subtotal': harga
            })
        self.refresh_cart()
        self.update_total()

    def refresh_cart(self):
        self.cart_listbox.delete(0, tk.END)
        for i, item in enumerate(self.cart, 1):
            self.cart_listbox.insert(
                tk.END,
                f"{i}. {item['nama']} x{item['qty']} = Rp {item['subtotal']:,}"
            )

    def update_total(self):
        subtotal = sum(i['subtotal'] for i in self.cart)
        ppn = int(subtotal * 0.11)
        self.total = subtotal + ppn
        self.total_label.config(text=f"TOTAL: Rp {self.total:,}")

    def bayar_tunai(self):
        if not self.cart:
            messagebox.showwarning("Kosong", "Keranjang kosong")
            return
        messagebox.showinfo("Sukses", f"Bayar Tunai Rp {self.total:,}")
        self.cart.clear()
        self.refresh_cart()
        self.update_total()

    def bayar_debit(self):
        if not self.cart:
            messagebox.showwarning("Kosong", "Keranjang kosong")
            return
        messagebox.showinfo("Sukses", f"Bayar Debit Rp {self.total:,}")
        self.cart.clear()
        self.refresh_cart()
        self.update_total()

    def laporan(self):
        messagebox.showinfo(
            "Laporan",
            f"Total Transaksi Terakhir\nRp {self.total:,}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = KasirProFixed(root)
    root.mainloop()

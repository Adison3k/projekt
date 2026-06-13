"""
Moduł gui - graficzny interfejs użytkownika księgarni Bookstore (Tkinter).

Zawiera klasy i funkcje budujące wielozakładkowy interfejs dla:
- Administratora: zarządzanie katalogiem i klientami
- Klienta: przeglądanie, zakup i historia zakupów

Klasy:
    BookstoreApp: Główna klasa aplikacji GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ADMIN_LOGIN, ADMIN_PASSWORD
from book_manager import add_book, remove_book, get_all_books, find_book
from customer_manager import register_customer, remove_customer, get_all_customers, authenticate_customer, get_customer_by_id
from purchase_manager import buy_books, get_purchase_history
from stats_manager import get_bookstore_summary, get_books_by_genre, get_customer_purchase_counts


# ─────────────────────────────────────────────
#  Kolory i styl
# ─────────────────────────────────────────────
COLORS = {
    "bg": "#1a1a2e",
    "surface": "#16213e",
    "card": "#0f3460",
    "accent": "#e94560",
    "accent2": "#533483",
    "text": "#eaeaea",
    "text_dim": "#a8a8b3",
    "success": "#4caf50",
    "warning": "#ff9800",
    "entry_bg": "#1e2a45",
}

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 9)


def styled_button(parent, text, command, color=None, **kwargs):
    """Tworzy stylowany przycisk."""
    c = color or COLORS["accent"]
    btn = tk.Button(
        parent, text=text, command=command,
        bg=c, fg="white", activebackground=COLORS["accent2"],
        activeforeground="white", relief="flat", cursor="hand2",
        font=FONT_BODY, padx=12, pady=6, bd=0, **kwargs
    )
    return btn


def styled_entry(parent, width=25, show=None):
    """Tworzy stylowane pole tekstowe."""
    e = tk.Entry(
        parent, width=width, bg=COLORS["entry_bg"], fg=COLORS["text"],
        insertbackground=COLORS["text"], relief="flat",
        font=FONT_BODY, bd=4
    )
    if show:
        e["show"] = show
    return e


def styled_label(parent, text, font=None, color=None):
    return tk.Label(
        parent, text=text, bg=COLORS["surface"],
        fg=color or COLORS["text"], font=font or FONT_BODY
    )


# ─────────────────────────────────────────────
#  Główna klasa aplikacji
# ─────────────────────────────────────────────

class BookstoreApp:
    """
    Główna klasa graficznego interfejsu użytkownika Bookstore.

    Zarządza ekranami logowania, panelem administratora
    i panelem klienta.

    Args:
        root (tk.Tk): Główne okno Tkinter.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📚 Bookstore – System Obsługi Księgarni")
        self.root.geometry("960x680")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        self.current_user_id = None
        self.is_admin = False

        self._show_login_screen()

    # ── Ekran logowania ────────────────────────

    def _show_login_screen(self):
        self._clear_window()
        frame = tk.Frame(self.root, bg=COLORS["bg"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="📚 BOOKSTORE", font=("Segoe UI", 28, "bold"),
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(0, 4))
        tk.Label(frame, text="Twoja internetowa księgarnia e-booków",
                 font=("Segoe UI", 11), bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(pady=(0, 30))

        card = tk.Frame(frame, bg=COLORS["surface"], padx=40, pady=30)
        card.pack()

        tk.Label(card, text="Login", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONT_BODY).grid(row=0, column=0, sticky="w", pady=4)
        self._login_entry = styled_entry(card, width=28)
        self._login_entry.grid(row=1, column=0, pady=(0, 12))

        tk.Label(card, text="Hasło", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONT_BODY).grid(row=2, column=0, sticky="w", pady=4)
        self._pass_entry = styled_entry(card, width=28, show="●")
        self._pass_entry.grid(row=3, column=0, pady=(0, 20))

        styled_button(card, "  Zaloguj się  ", self._handle_login).grid(row=4, column=0, pady=4, sticky="ew")

        sep = tk.Frame(card, bg=COLORS["card"], height=1)
        sep.grid(row=5, column=0, sticky="ew", pady=14)

        tk.Label(card, text="Nie masz konta?", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONT_BODY).grid(row=6, column=0)
        styled_button(card, "  Zarejestruj się  ", self._show_register_screen,
                      color=COLORS["card"]).grid(row=7, column=0, pady=4, sticky="ew")

        self._login_entry.focus()
        self.root.bind("<Return>", lambda e: self._handle_login())

    def _handle_login(self):
        login = self._login_entry.get().strip()
        pwd = self._pass_entry.get().strip()

        if login == ADMIN_LOGIN and pwd == ADMIN_PASSWORD:
            self.is_admin = True
            self._show_admin_panel()
            return

        cid = authenticate_customer(login, pwd)
        if cid:
            self.current_user_id = cid
            self.is_admin = False
            self._show_customer_panel()
        else:
            messagebox.showerror("Błąd logowania", "Nieprawidłowy login lub hasło.")

    # ── Ekran rejestracji ──────────────────────

    def _show_register_screen(self):
        self._clear_window()
        frame = tk.Frame(self.root, bg=COLORS["bg"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="📋 Rejestracja konta", font=FONT_TITLE,
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(0, 20))

        card = tk.Frame(frame, bg=COLORS["surface"], padx=40, pady=30)
        card.pack()

        fields = [
            ("Imię", False), ("Nazwisko", False), ("E-mail", False),
            ("Login", False), ("Hasło", True),
            ("Ulica", False), ("Miasto", False), ("Kod pocztowy", False),
        ]
        self._reg_entries = {}
        for i, (label, is_pwd) in enumerate(fields):
            tk.Label(card, text=label, bg=COLORS["surface"],
                     fg=COLORS["text_dim"], font=FONT_BODY).grid(
                row=i * 2, column=0, sticky="w", pady=2)
            e = styled_entry(card, width=30, show="●" if is_pwd else None)
            e.grid(row=i * 2 + 1, column=0, pady=(0, 8))
            self._reg_entries[label] = e

        btn_frame = tk.Frame(card, bg=COLORS["surface"])
        btn_frame.grid(row=len(fields) * 2 + 1, column=0, pady=10, sticky="ew")
        styled_button(btn_frame, "  Zarejestruj  ", self._handle_register).pack(side="left", padx=4)
        styled_button(btn_frame, "  Powrót  ", self._show_login_screen,
                      color=COLORS["card"]).pack(side="left", padx=4)

    def _handle_register(self):
        e = self._reg_entries
        try:
            address = {
                "street": e["Ulica"].get(),
                "city": e["Miasto"].get(),
                "postal_code": e["Kod pocztowy"].get(),
                "country": "Polska"
            }
            cid = register_customer(
                e["Imię"].get(), e["Nazwisko"].get(), e["E-mail"].get(),
                e["Login"].get(), e["Hasło"].get(), address
            )
            messagebox.showinfo("Sukces", f"Konto założone!\nTwoje ID klienta: {cid}")
            self._show_login_screen()
        except Exception as ex:
            messagebox.showerror("Błąd rejestracji", str(ex))

    # ── Panel administratora ───────────────────

    def _show_admin_panel(self):
        self._clear_window()

        # Pasek górny
        header = tk.Frame(self.root, bg=COLORS["accent"], height=50)
        header.pack(fill="x")
        tk.Label(header, text="📚 Bookstore  |  Panel Administratora",
                 font=FONT_SUBTITLE, bg=COLORS["accent"], fg="white").pack(side="left", padx=20, pady=12)
        styled_button(header, "Wyloguj", self._show_login_screen,
                      color=COLORS["bg"]).pack(side="right", padx=10, pady=8)

        # Zakładki
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORS["card"], foreground=COLORS["text"],
                        padding=[14, 6], font=FONT_BODY)
        style.map("TNotebook.Tab", background=[("selected", COLORS["accent"])])

        self._build_books_tab(nb)
        self._build_customers_tab(nb)
        self._build_stats_tab(nb)

    def _build_books_tab(self, nb):
        frame = tk.Frame(nb, bg=COLORS["surface"])
        nb.add(frame, text="📖  Katalog e-booków")

        # Formularz dodawania
        form = tk.LabelFrame(frame, text=" Dodaj nową książkę ", bg=COLORS["surface"],
                             fg=COLORS["text_dim"], font=FONT_BODY)
        form.pack(fill="x", padx=12, pady=10)

        fields = ["Tytuł", "Autor", "Gatunek", "Cena (zł)", "Rok"]
        self._book_entries = {}
        for i, f in enumerate(fields):
            tk.Label(form, text=f, bg=COLORS["surface"],
                     fg=COLORS["text_dim"], font=FONT_BODY).grid(row=0, column=i * 2, padx=6, pady=8)
            e = styled_entry(form, width=14)
            e.grid(row=0, column=i * 2 + 1, padx=4)
            self._book_entries[f] = e

        styled_button(form, "+ Dodaj", self._handle_add_book).grid(
            row=0, column=len(fields) * 2, padx=10)

        # Usuwanie
        del_frame = tk.Frame(frame, bg=COLORS["surface"])
        del_frame.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(del_frame, text="Usuń (ID lub tytuł):", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONT_BODY).pack(side="left")
        self._del_book_entry = styled_entry(del_frame, width=20)
        self._del_book_entry.pack(side="left", padx=8)
        styled_button(del_frame, "Usuń", self._handle_remove_book,
                      color=COLORS["accent"]).pack(side="left")

        # Tabela
        self._books_tree = self._build_treeview(
            frame, ["ID", "Tytuł", "Autor", "Gatunek", "Cena", "Rok"]
        )
        self._refresh_books_tree()

        styled_button(frame, "🔄 Odśwież", self._refresh_books_tree,
                      color=COLORS["card"]).pack(pady=6)

    def _handle_add_book(self):
        e = self._book_entries
        try:
            add_book(e["Tytuł"].get(), e["Autor"].get(), e["Gatunek"].get(),
                     e["Cena (zł)"].get(), e["Rok"].get())
            messagebox.showinfo("OK", "Książka dodana.")
            for entry in e.values():
                entry.delete(0, tk.END)
            self._refresh_books_tree()
        except Exception as ex:
            messagebox.showerror("Błąd", str(ex))

    def _handle_remove_book(self):
        val = self._del_book_entry.get().strip()
        if not val:
            return
        identifier = int(val) if val.isdigit() else val
        try:
            ok = remove_book(identifier)
            if ok:
                messagebox.showinfo("OK", "Usunięto książkę.")
            else:
                messagebox.showwarning("Nie znaleziono", "Brak książki o podanym identyfikatorze.")
            self._refresh_books_tree()
        except Exception as ex:
            messagebox.showerror("Błąd", str(ex))

    def _refresh_books_tree(self):
        df = get_all_books()
        self._books_tree.delete(*self._books_tree.get_children())
        for _, row in df.iterrows():
            self._books_tree.insert("", "end", values=(
                row["id"], row["title"], row["author"],
                row["genre"], f"{row['price']} zł", row["year"]
            ))

    def _build_customers_tab(self, nb):
        frame = tk.Frame(nb, bg=COLORS["surface"])
        nb.add(frame, text="👥  Klienci")

        del_frame = tk.Frame(frame, bg=COLORS["surface"])
        del_frame.pack(fill="x", padx=12, pady=12)
        tk.Label(del_frame, text="Usuń klienta (ID lub nazwisko):", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONT_BODY).pack(side="left")
        self._del_cust_entry = styled_entry(del_frame, width=22)
        self._del_cust_entry.pack(side="left", padx=8)
        styled_button(del_frame, "Usuń", self._handle_remove_customer,
                      color=COLORS["accent"]).pack(side="left")

        self._customers_tree = self._build_treeview(
            frame, ["ID", "Imię", "Nazwisko", "E-mail", "Login", "Data rejestracji"]
        )
        self._refresh_customers_tree()

        styled_button(frame, "🔄 Odśwież", self._refresh_customers_tree,
                      color=COLORS["card"]).pack(pady=6)

    def _handle_remove_customer(self):
        val = self._del_cust_entry.get().strip()
        if not val:
            return
        identifier = int(val) if val.isdigit() else val
        try:
            ok = remove_customer(identifier)
            if ok:
                messagebox.showinfo("OK", "Usunięto klienta.")
            else:
                messagebox.showwarning("Nie znaleziono", "Brak klienta o podanym identyfikatorze.")
            self._refresh_customers_tree()
        except Exception as ex:
            messagebox.showerror("Błąd", str(ex))

    def _refresh_customers_tree(self):
        df = get_all_customers()
        self._customers_tree.delete(*self._customers_tree.get_children())
        for _, row in df.iterrows():
            self._customers_tree.insert("", "end", values=(
                row["id"], row["first_name"], row["last_name"],
                row["email"], row["login"], row["registration_date"]
            ))

    def _build_stats_tab(self, nb):
        frame = tk.Frame(nb, bg=COLORS["surface"])
        nb.add(frame, text="📊  Statystyki")

        self._stats_text = tk.Text(frame, bg=COLORS["entry_bg"], fg=COLORS["text"],
                                   font=FONT_MONO, relief="flat", state="disabled", height=30)
        self._stats_text.pack(fill="both", expand=True, padx=12, pady=12)
        styled_button(frame, "🔄 Odśwież statystyki", self._refresh_stats,
                      color=COLORS["card"]).pack(pady=6)
        self._refresh_stats()

    def _refresh_stats(self):
        s = get_bookstore_summary()
        genre_df = get_books_by_genre()
        purchases = get_customer_purchase_counts()

        lines = [
            "═" * 50,
            "       STATYSTYKI KSIĘGARNI BOOKSTORE",
            "═" * 50,
            f"  Łączna liczba e-booków:    {s['total_books']}",
            f"  Dostępnych e-booków:       {s['available_books']}",
            f"  Liczba klientów:           {s['total_customers']}",
            f"  Średnia cena e-booka:      {s['avg_price']} zł",
            f"  Najtańszy e-book:          {s['min_price']} zł",
            f"  Najdroższy e-book:         {s['max_price']} zł",
            f"  Liczba gatunków:           {s['genres']}",
            "",
            "─" * 50,
            "  E-BOOKI WG GATUNKU:",
            "─" * 50,
        ]

        if not genre_df.empty:
            for _, row in genre_df.iterrows():
                lines.append(f"  {row['genre']:<20} {int(row['liczba'])} szt.  "
                             f"śr. {row['srednia_cena']} zł")
        else:
            lines.append("  Brak danych.")

        lines += ["", "─" * 50, "  ZAKUPY KLIENTÓW:", "─" * 50]
        if purchases:
            for cid, cnt in sorted(purchases.items(), key=lambda x: -x[1]):
                lines.append(f"  Klient ID {cid:<8}  {cnt} zakupów")
        else:
            lines.append("  Brak danych o zakupach.")

        lines.append("═" * 50)

        self._stats_text.config(state="normal")
        self._stats_text.delete("1.0", tk.END)
        self._stats_text.insert(tk.END, "\n".join(lines))
        self._stats_text.config(state="disabled")

    # ── Panel klienta ──────────────────────────

    def _show_customer_panel(self):
        self._clear_window()
        customer = get_customer_by_id(self.current_user_id)
        name = f"{customer['first_name']} {customer['last_name']}" if customer is not None else "Klient"

        header = tk.Frame(self.root, bg=COLORS["card"], height=50)
        header.pack(fill="x")
        tk.Label(header, text=f"📚 Bookstore  |  Witaj, {name}  (ID: {self.current_user_id})",
                 font=FONT_SUBTITLE, bg=COLORS["card"], fg=COLORS["text"]).pack(side="left", padx=20, pady=12)
        styled_button(header, "Wyloguj", self._show_login_screen,
                      color=COLORS["accent"]).pack(side="right", padx=10, pady=8)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_shop_tab(nb)
        self._build_history_tab(nb)

    def _build_shop_tab(self, nb):
        frame = tk.Frame(nb, bg=COLORS["surface"])
        nb.add(frame, text="🛒  Sklep")

        # Wyszukiwarka
        search_frame = tk.Frame(frame, bg=COLORS["surface"])
        search_frame.pack(fill="x", padx=12, pady=10)
        tk.Label(search_frame, text="Szukaj:", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONT_BODY).pack(side="left")
        self._search_entry = styled_entry(search_frame, width=28)
        self._search_entry.pack(side="left", padx=8)
        styled_button(search_frame, "Szukaj", self._handle_search,
                      color=COLORS["card"]).pack(side="left")
        styled_button(search_frame, "Pokaż wszystkie", self._refresh_shop_tree,
                      color=COLORS["card"]).pack(side="left", padx=6)

        self._shop_tree = self._build_treeview(
            frame, ["ID", "Tytuł", "Autor", "Gatunek", "Cena"]
        )
        self._refresh_shop_tree()

        # Zakup
        buy_frame = tk.Frame(frame, bg=COLORS["surface"])
        buy_frame.pack(fill="x", padx=12, pady=8)
        tk.Label(buy_frame, text="ID do kupienia (oddziel spacją):", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONT_BODY).pack(side="left")
        self._buy_entry = styled_entry(buy_frame, width=24)
        self._buy_entry.pack(side="left", padx=8)
        styled_button(buy_frame, "🛒 Kup", self._handle_buy).pack(side="left")

    def _handle_search(self):
        query = self._search_entry.get().strip()
        if not query:
            self._refresh_shop_tree()
            return
        df = find_book(query)
        self._shop_tree.delete(*self._shop_tree.get_children())
        for _, row in df.iterrows():
            self._shop_tree.insert("", "end", values=(
                row["id"], row["title"], row["author"], row["genre"], f"{row['price']} zł"
            ))

    def _refresh_shop_tree(self):
        df = get_all_books()
        self._shop_tree.delete(*self._shop_tree.get_children())
        for _, row in df.iterrows():
            self._shop_tree.insert("", "end", values=(
                row["id"], row["title"], row["author"], row["genre"], f"{row['price']} zł"
            ))

    def _handle_buy(self):
        val = self._buy_entry.get().strip()
        if not val:
            messagebox.showwarning("Brak danych", "Podaj ID książek do zakupu.")
            return
        try:
            ids = [int(x) for x in val.split()]
            result = buy_books(self.current_user_id, *ids)
            msg = f"Zakupiono {len(result['purchased'])} książkę/i.\n"
            msg += f"Tytuły: {', '.join(result['purchased'])}\n"
            msg += f"Łączna kwota: {result['total_price']} zł"
            if result["not_found"]:
                msg += f"\nNie znaleziono ID: {result['not_found']}"
            messagebox.showinfo("Zakup zrealizowany", msg)
            self._buy_entry.delete(0, tk.END)
        except Exception as ex:
            messagebox.showerror("Błąd zakupu", str(ex))

    def _build_history_tab(self, nb):
        frame = tk.Frame(nb, bg=COLORS["surface"])
        nb.add(frame, text="📋  Historia zakupów")

        self._history_text = tk.Text(frame, bg=COLORS["entry_bg"], fg=COLORS["text"],
                                     font=FONT_MONO, relief="flat", state="disabled")
        self._history_text.pack(fill="both", expand=True, padx=12, pady=12)
        styled_button(frame, "🔄 Odśwież", self._refresh_history,
                      color=COLORS["card"]).pack(pady=6)
        self._refresh_history()

    def _refresh_history(self):
        history = get_purchase_history(self.current_user_id)
        self._history_text.config(state="normal")
        self._history_text.delete("1.0", tk.END)
        self._history_text.insert(tk.END, history)
        self._history_text.config(state="disabled")

    # ── Pomocnicze ────────────────────────────

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _build_treeview(self, parent, columns: list) -> ttk.Treeview:
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background=COLORS["entry_bg"], foreground=COLORS["text"],
                        fieldbackground=COLORS["entry_bg"], rowheight=26,
                        font=FONT_BODY)
        style.configure("Custom.Treeview.Heading",
                        background=COLORS["card"], foreground=COLORS["text"],
                        font=("Segoe UI", 10, "bold"))
        style.map("Custom.Treeview", background=[("selected", COLORS["accent2"])])

        container = tk.Frame(parent, bg=COLORS["surface"])
        container.pack(fill="both", expand=True, padx=12, pady=6)

        scrollbar = ttk.Scrollbar(container, orient="vertical")
        tree = ttk.Treeview(container, columns=columns, show="headings",
                            yscrollcommand=scrollbar.set, style="Custom.Treeview")
        scrollbar.config(command=tree.yview)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")

        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return tree

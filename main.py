"""
Moduł main - główny moduł administracyjny księgarni Bookstore.

Uruchamia graficzny interfejs użytkownika (GUI) oraz dostarcza
interfejs CLI do zarządzania zasobami księgarni.

Uruchomienie:
    python main.py

Administracja przez CLI (tryb bez GUI):
    Ustaw USE_GUI = False aby uruchomić tryb tekstowy.
"""

import sys
import os

# Upewnij się, że katalog projektu jest w ścieżce
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ADMIN_LOGIN, ADMIN_PASSWORD
from book_manager import add_book, remove_book, get_all_books, find_book
from customer_manager import register_customer, remove_customer, get_all_customers, authenticate_customer
from purchase_manager import buy_books, get_purchase_history
from stats_manager import print_summary, get_bookstore_summary


# ─────────────────────────────────────────────
#  Tryb CLI (fallback bez GUI)
# ─────────────────────────────────────────────

def _admin_menu_cli():
    """Tekstowe menu administratora."""
    while True:
        print("\n=== PANEL ADMINISTRATORA ===")
        print("1. Dodaj książkę")
        print("2. Usuń książkę")
        print("3. Lista książek")
        print("4. Dodaj klienta")
        print("5. Usuń klienta")
        print("6. Lista klientów")
        print("7. Statystyki")
        print("0. Wyjście")
        choice = input("Wybór: ").strip()

        if choice == "1":
            title = input("Tytuł: ")
            author = input("Autor: ")
            genre = input("Gatunek: ")
            price = input("Cena: ")
            year = input("Rok: ")
            try:
                add_book(title, author, genre, price, year)
            except Exception as e:
                print(f"Błąd: {e}")

        elif choice == "2":
            q = input("Podaj ID (liczba) lub tytuł: ")
            identifier = int(q) if q.isdigit() else q
            try:
                remove_book(identifier)
            except Exception as e:
                print(f"Błąd: {e}")

        elif choice == "3":
            df = get_all_books()
            print(df.to_string(index=False))

        elif choice == "4":
            fn = input("Imię: ")
            ln = input("Nazwisko: ")
            email = input("E-mail: ")
            login = input("Login: ")
            pwd = input("Hasło: ")
            try:
                cid = register_customer(fn, ln, email, login, pwd)
                print(f"Klient zarejestrowany, ID: {cid}")
            except Exception as e:
                print(f"Błąd: {e}")

        elif choice == "5":
            q = input("Podaj ID (liczba) lub nazwisko: ")
            identifier = int(q) if q.isdigit() else q
            try:
                remove_customer(identifier)
            except Exception as e:
                print(f"Błąd: {e}")

        elif choice == "6":
            df = get_all_customers()
            print(df.to_string(index=False))

        elif choice == "7":
            print_summary()

        elif choice == "0":
            break


def _client_menu_cli(customer_id: int):
    """Tekstowe menu klienta."""
    while True:
        print(f"\n=== MENU KLIENTA (ID: {customer_id}) ===")
        print("1. Przeglądaj katalog e-booków")
        print("2. Kup e-booki")
        print("3. Historia zakupów")
        print("0. Wyloguj")
        choice = input("Wybór: ").strip()

        if choice == "1":
            df = get_all_books()
            print(df[["id", "title", "author", "genre", "price"]].to_string(index=False))

        elif choice == "2":
            ids_input = input("Podaj ID książek (oddzielone spacją): ").strip()
            try:
                book_ids = [int(x) for x in ids_input.split()]
                result = buy_books(customer_id, *book_ids)
                print(f"Zakupiono: {result['purchased']}")
                print(f"Łączna kwota: {result['total_price']} zł")
            except Exception as e:
                print(f"Błąd: {e}")

        elif choice == "3":
            history = get_purchase_history(customer_id)
            print(history)

        elif choice == "0":
            break


def __main__():
    """
    Główna funkcja uruchamiająca program Bookstore.

    Najpierw próbuje uruchomić GUI (Tkinter).
    Jeśli Tkinter jest niedostępny, uruchamia tryb CLI.
    """
    print("=" * 50)
    print("   Witaj w systemie Bookstore!")
    print("=" * 50)

    # Próba uruchomienia GUI
    try:
        from gui import BookstoreApp
        import tkinter as tk
        root = tk.Tk()
        app = BookstoreApp(root)
        root.mainloop()
        return
    except ImportError:
        pass
    except Exception as e:
        print(f"GUI niedostępne ({e}), uruchamiam tryb CLI...")

    # Tryb CLI
    print("\n1. Logowanie jako administrator")
    print("2. Logowanie jako klient")
    print("0. Wyjście")
    mode = input("Wybór: ").strip()

    if mode == "1":
        login = input("Login admina: ")
        pwd = input("Hasło admina: ")
        if login == ADMIN_LOGIN and pwd == ADMIN_PASSWORD:
            print("Zalogowano jako administrator.")
            _admin_menu_cli()
        else:
            print("Nieprawidłowe dane logowania.")

    elif mode == "2":
        login = input("Login klienta: ")
        pwd = input("Hasło klienta: ")
        cid = authenticate_customer(login, pwd)
        if cid:
            print(f"Zalogowano. Twoje ID: {cid}")
            _client_menu_cli(cid)
        else:
            print("Nieprawidłowe dane logowania.")

    elif mode == "0":
        print("Do widzenia!")


if __name__ == "__main__":
    __main__()

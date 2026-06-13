"""
Moduł purchase_manager - obsługa zakupów e-booków przez klientów.

Zawiera funkcje zakupu jednej lub wielu książek naraz,
zapis historii zakupów do pliku klienta oraz
odczyt historii zakupów.

Funkcje:
    buy_books(customer_id, *book_ids)  - zakup dowolnej liczby e-booków (z dekoratorem)
    get_purchase_history(customer_id)  - odczyt historii zakupów klienta
    apply_discount(func)               - funkcja wyższego rzędu (dekorator rabatowy)
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from config import BOOK_CSV, DATABASE_DIR, ACCESS_DAYS
from customer_manager import customer_exists
from book_manager import get_all_books


# ─────────────────────────────────────────────
#  Funkcja wyższego rzędu – dekorator rabatowy
# ─────────────────────────────────────────────

def apply_discount(discount_percent: float):
    """
    Funkcja wyższego rzędu – fabryka dekoratorów rabatowych.

    Zwraca dekorator, który automatycznie stosuje procentowy rabat
    na całkowitą kwotę zakupu.

    Args:
        discount_percent (float): Procent rabatu (0–100).

    Returns:
        decorator: Dekorator modyfikujący cenę zakupu.

    Example:
        >>> @apply_discount(10)
        ... def buy_books(customer_id, *book_ids):
        ...     ...
    """
    def decorator(func):
        def wrapper(customer_id, *book_ids, **kwargs):
            print(f"  [RABAT] Stosowanie rabatu {discount_percent}% na zakup.")
            result = func(customer_id, *book_ids, **kwargs)
            if result and "total_price" in result:
                original = result["total_price"]
                discounted = round(original * (1 - discount_percent / 100), 2)
                result["total_price"] = discounted
                result["discount_applied"] = f"{discount_percent}% (-{round(original - discounted, 2)} zł)"
                print(f"  [RABAT] Cena po rabacie: {discounted} zł (było: {original} zł)")
            return result
        return wrapper
    return decorator


# ─────────────────────────────────────────────
#  Dekorator weryfikujący klienta przed zakupem
# ─────────────────────────────────────────────

def require_valid_customer(func):
    """
    Dekorator sprawdzający istnienie klienta przed zakupem.

    Raises:
        ValueError: Gdy klient o podanym ID nie istnieje w bazie.
    """
    def wrapper(customer_id, *args, **kwargs):
        if not customer_exists(customer_id):
            raise ValueError(f"Klient o ID {customer_id} nie istnieje w bazie.")
        return func(customer_id, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────
#  Główna funkcja zakupu
# ─────────────────────────────────────────────

@require_valid_customer
def buy_books(customer_id: int, *book_ids: int):
    """
    Realizuje zakup dowolnej liczby e-booków przez klienta.

    Funkcja wielu zmiennych wejściowych (*book_ids) –
    klient może kupić jedną lub wiele książek w jednym wywołaniu.

    Dla każdej zakupionej książki zapisywany jest wpis w pliku historii
    klienta (DATABASE/{customer_id}.txt) zawierający:
    - tytuł i autora książki
    - datę zakupu
    - datę wygaśnięcia dostępu (zakup + ACCESS_DAYS dni)

    Args:
        customer_id (int): ID klienta dokonującego zakupu.
        *book_ids (int): Jeden lub więcej ID książek do zakupu.

    Returns:
        dict: Słownik z wynikiem zakupu:
            - 'purchased': lista tytułów zakupionych książek
            - 'not_found': lista ID, których nie znaleziono
            - 'total_price': łączna kwota zakupu (float)

    Raises:
        ValueError: Gdy nie podano żadnych ID książek.
        FileNotFoundError: Gdy plik historii zakupów klienta nie istnieje.

    Example:
        >>> result = buy_books(1234, 1001, 1002, 1003)
        >>> print(result["total_price"])
    """
    if not book_ids:
        raise ValueError("Należy podać co najmniej jeden ID książki.")

    df_books = get_all_books()
    purchase_file = os.path.join(DATABASE_DIR, f"{customer_id}.txt")

    if not os.path.exists(purchase_file):
        raise FileNotFoundError(f"Brak pliku historii dla klienta ID={customer_id}.")

    purchased = []
    not_found = []
    total_price = 0.0

    purchase_date = datetime.now()
    expiry_date = purchase_date + timedelta(days=ACCESS_DAYS)

    def _format_purchase_entry(title, author, price, p_date, e_date):
        """Funkcja zagnieżdżona formatująca wpis do pliku historii."""
        return (
            f"Tytuł:          {title}\n"
            f"Autor:          {author}\n"
            f"Cena:           {price} zł\n"
            f"Data zakupu:    {p_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Dostęp do:      {e_date.strftime('%Y-%m-%d')}\n"
            f"{'-' * 40}\n"
        )

    with open(purchase_file, "a", encoding="utf-8") as f:
        for book_id in book_ids:
            book_row = df_books[df_books["id"] == book_id]
            if book_row.empty:
                not_found.append(book_id)
                continue

            book = book_row.iloc[0]
            title = book["title"]
            author = book["author"]
            price = float(book["price"])

            entry = _format_purchase_entry(title, author, price, purchase_date, expiry_date)
            f.write(entry)

            purchased.append(title)
            total_price += price

    total_price = round(total_price, 2)

    if purchased:
        print(f"  Klient {customer_id} zakupił {len(purchased)} książkę/i za {total_price} zł.")
    if not_found:
        print(f"  Nie znaleziono książek o ID: {not_found}")

    return {
        "purchased": purchased,
        "not_found": not_found,
        "total_price": total_price
    }


def get_purchase_history(customer_id: int) -> str:
    """
    Odczytuje i zwraca historię zakupów klienta.

    Args:
        customer_id (int): ID klienta.

    Returns:
        str: Zawartość pliku historii zakupów lub komunikat o braku pliku.
    """
    filepath = os.path.join(DATABASE_DIR, f"{customer_id}.txt")
    if not os.path.exists(filepath):
        return f"Brak historii zakupów dla klienta ID={customer_id}."
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────────
#  Wersja z rabatem (dekorator wyższego rzędu)
# ─────────────────────────────────────────────

@apply_discount(10)
@require_valid_customer
def buy_books_with_discount(customer_id: int, *book_ids: int):
    """
    Wersja funkcji zakupowej z 10% rabatem.
    Działa identycznie jak buy_books, ale stosuje rabat.
    """
    return buy_books.__wrapped__(customer_id, *book_ids) if hasattr(buy_books, '__wrapped__') else buy_books(customer_id, *book_ids)

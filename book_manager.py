"""
Moduł book_manager - zarządzanie katalogiem e-booków księgarni.

Zawiera funkcje do dodawania i usuwania e-booków z bazy danych (book.csv).
Wszystkie operacje wykonywane są przy użyciu biblioteki pandas.

Funkcje:
    add_book(*args, **kwargs)  - dodaje nową książkę do katalogu
    remove_book(identifier)    - usuwa książkę według ID lub tytułu
    get_all_books()            - zwraca DataFrame ze wszystkimi książkami
    find_book(query)           - wyszukuje książki wg frazy
"""

import pandas as pd
import os
from config import BOOK_CSV


# ─────────────────────────────────────────────
#  Pomocnicze funkcje wewnętrzne
# ─────────────────────────────────────────────

def _load_books() -> pd.DataFrame:
    """Wczytuje plik book.csv do DataFrame."""
    if not os.path.exists(BOOK_CSV):
        return pd.DataFrame(columns=["id", "title", "author", "genre", "price", "year", "available"])
    return pd.read_csv(BOOK_CSV)


def _save_books(df: pd.DataFrame) -> None:
    """Zapisuje DataFrame do pliku book.csv."""
    df.to_csv(BOOK_CSV, index=False)


def _generate_book_id(df: pd.DataFrame) -> int:
    """Generuje unikalny ID dla nowej książki (funkcja zagnieżdżona wewnątrz add_book)."""
    if df.empty:
        return 1001
    return int(df["id"].max()) + 1


# ─────────────────────────────────────────────
#  Dekorator logujący operacje na książkach
# ─────────────────────────────────────────────

def log_book_operation(func):
    """
    Dekorator logujący wykonywane operacje na katalogu książek.

    Wypisuje nazwę wykonywanej funkcji oraz informację o sukcesie
    lub błędzie operacji.

    Args:
        func: Dekorowana funkcja.

    Returns:
        Wrapper z logiką logowania.
    """
    def wrapper(*args, **kwargs):
        print(f"[LOG] Wykonywanie operacji: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            print(f"[LOG] Operacja '{func.__name__}' zakończona sukcesem.")
            return result
        except Exception as e:
            print(f"[LOG] Błąd w operacji '{func.__name__}': {e}")
            raise
    return wrapper


# ─────────────────────────────────────────────
#  Funkcje publiczne modułu
# ─────────────────────────────────────────────

@log_book_operation
def add_book(*args, **kwargs):
    """
    Dodaje nową książkę do bazy danych (book.csv).

    Funkcja wielu zmiennych wejściowych – przyjmuje dane książki
    jako argumenty pozycyjne lub nazwane.

    Kolejność argumentów pozycyjnych:
        title, author, genre, price, year

    Args pozycyjne (*args):
        args[0] (str): Tytuł książki.
        args[1] (str): Autor.
        args[2] (str): Gatunek.
        args[3] (float): Cena.
        args[4] (int): Rok wydania.

    Args nazwane (**kwargs):
        title (str): Tytuł książki.
        author (str): Autor.
        genre (str): Gatunek.
        price (float): Cena.
        year (int): Rok wydania.

    Returns:
        int: Nadany ID nowej książki.

    Raises:
        ValueError: Gdy brakuje wymaganych danych lub cena/rok są nieprawidłowe.

    Example:
        >>> add_book("Hobbit", "Tolkien", "Fantasy", 24.99, 1937)
        >>> add_book(title="Hobbit", author="Tolkien", genre="Fantasy", price=24.99, year=1937)
    """
    # Obsługa zarówno args pozycyjnych jak i kwargs
    fields = ["title", "author", "genre", "price", "year"]
    data = {}

    for i, field in enumerate(fields):
        if i < len(args):
            data[field] = args[i]
        elif field in kwargs:
            data[field] = kwargs[field]
        else:
            raise ValueError(f"Brakujące pole: '{field}'")

    # Walidacja
    try:
        data["price"] = float(data["price"])
        data["year"] = int(data["year"])
    except (ValueError, TypeError):
        raise ValueError("Cena musi być liczbą dziesiętną, a rok liczbą całkowitą.")

    if data["price"] <= 0:
        raise ValueError("Cena musi być większa od zera.")
    if not (1000 <= data["year"] <= 2100):
        raise ValueError("Rok wydania jest nieprawidłowy.")

    df = _load_books()

    def _build_new_row(book_id, title, author, genre, price, year):
        """Funkcja zagnieżdżona – buduje słownik nowego wiersza."""
        return {
            "id": book_id,
            "title": title,
            "author": author,
            "genre": genre,
            "price": price,
            "year": year,
            "available": True
        }

    new_id = _generate_book_id(df)
    new_row = _build_new_row(new_id, data["title"], data["author"],
                              data["genre"], data["price"], data["year"])

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    _save_books(df)
    print(f"  Dodano książkę: '{data['title']}' (ID: {new_id})")
    return new_id


@log_book_operation
def remove_book(identifier):
    """
    Usuwa książkę z bazy danych (book.csv).

    Obsługuje usuwanie według ID (int) lub tytułu (str).

    Args:
        identifier (int | str): ID książki (int) lub fragment/pełny tytuł (str).

    Returns:
        bool: True jeśli usunięto, False jeśli nie znaleziono.

    Raises:
        FileNotFoundError: Gdy plik book.csv nie istnieje.
        ValueError: Gdy identifier jest nieprawidłowego typu.

    Example:
        >>> remove_book(1001)          # po ID
        >>> remove_book("Hobbit")      # po tytule
    """
    if not os.path.exists(BOOK_CSV):
        raise FileNotFoundError("Plik book.csv nie istnieje.")

    df = _load_books()
    original_len = len(df)

    if isinstance(identifier, int):
        df_filtered = df[df["id"] != identifier]
        label = f"ID={identifier}"
    elif isinstance(identifier, str):
        df_filtered = df[~df["title"].str.contains(identifier, case=False, na=False)]
        label = f"tytuł zawierający '{identifier}'"
    else:
        raise ValueError("Identifier musi być int (ID) lub str (tytuł).")

    if len(df_filtered) == original_len:
        print(f"  Nie znaleziono książki: {label}")
        return False

    _save_books(df_filtered)
    removed = original_len - len(df_filtered)
    print(f"  Usunięto {removed} książkę/i: {label}")
    return True


def get_all_books() -> pd.DataFrame:
    """
    Zwraca wszystkie książki z bazy jako DataFrame.

    Returns:
        pd.DataFrame: Tabela ze wszystkimi e-bookami.
    """
    return _load_books()


def find_book(query: str) -> pd.DataFrame:
    """
    Wyszukuje książki zawierające podaną frazę w tytule lub autorze.

    Args:
        query (str): Fraza do wyszukania.

    Returns:
        pd.DataFrame: Pasujące wyniki.
    """
    df = _load_books()
    mask = (
        df["title"].str.contains(query, case=False, na=False) |
        df["author"].str.contains(query, case=False, na=False)
    )
    return df[mask]

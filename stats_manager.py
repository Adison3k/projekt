"""
Moduł stats_manager - monitoring i statystyki zasobów księgarni.

Dostarcza funkcje analityczne oparte na pandas:
liczba klientów, dostępnych e-booków, średnia/min/max cena,
oraz zestawienia zakupów.
"""

import pandas as pd
import os
from config import BOOK_CSV, CUSTOMER_CSV, ADDRESS_CSV, DATABASE_DIR
from book_manager import get_all_books
from customer_manager import get_all_customers


def get_bookstore_summary() -> dict:
    """
    Zwraca pełne podsumowanie statystyk księgarni.

    Returns:
        dict: Słownik ze statystykami:
            - total_books: liczba e-booków w katalogu
            - available_books: liczba dostępnych e-booków
            - total_customers: liczba zarejestrowanych klientów
            - avg_price: średnia cena e-booka
            - min_price: minimalna cena e-booka
            - max_price: maksymalna cena e-booka
            - genres: liczba unikalnych gatunków
    """
    df_books = get_all_books()
    df_customers = get_all_customers()

    summary = {
        "total_books": len(df_books),
        "available_books": int(df_books["available"].sum()) if not df_books.empty else 0,
        "total_customers": len(df_customers),
        "avg_price": round(df_books["price"].mean(), 2) if not df_books.empty else 0.0,
        "min_price": round(df_books["price"].min(), 2) if not df_books.empty else 0.0,
        "max_price": round(df_books["price"].max(), 2) if not df_books.empty else 0.0,
        "genres": df_books["genre"].nunique() if not df_books.empty else 0,
    }
    return summary


def get_books_by_genre() -> pd.DataFrame:
    """Zwraca zestawienie liczby e-booków według gatunku."""
    df = get_all_books()
    if df.empty:
        return pd.DataFrame()
    return df.groupby("genre").agg(
        liczba=("id", "count"),
        srednia_cena=("price", "mean"),
        min_cena=("price", "min"),
        max_cena=("price", "max")
    ).round(2).reset_index()


def get_customer_purchase_counts() -> dict:
    """
    Zlicza liczbę zakupów każdego klienta na podstawie plików .txt.

    Returns:
        dict: {customer_id: liczba_zakupow}
    """
    counts = {}
    for filename in os.listdir(DATABASE_DIR):
        if filename.endswith(".txt"):
            cid = filename.replace(".txt", "")
            filepath = os.path.join(DATABASE_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # Liczymy wpisy po wystąpieniu "Tytuł:"
            count = content.count("Tytuł:")
            counts[cid] = count
    return counts


def get_top_customers(n: int = 3) -> list:
    """Zwraca n klientów z największą liczbą zakupów."""
    counts = get_customer_purchase_counts()
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts[:n]


def print_summary():
    """Wypisuje podsumowanie statystyk w czytelnej formie."""
    s = get_bookstore_summary()
    print("\n" + "=" * 45)
    print("       STATYSTYKI KSIĘGARNI BOOKSTORE")
    print("=" * 45)
    print(f"  Łączna liczba e-booków:     {s['total_books']}")
    print(f"  Dostępnych e-booków:        {s['available_books']}")
    print(f"  Liczba klientów:            {s['total_customers']}")
    print(f"  Średnia cena e-booka:       {s['avg_price']} zł")
    print(f"  Najtańszy e-book:           {s['min_price']} zł")
    print(f"  Najdroższy e-book:          {s['max_price']} zł")
    print(f"  Liczba gatunków:            {s['genres']}")
    print("=" * 45)

    top = get_top_customers()
    if top:
        print("  TOP klienci (wg zakupów):")
        for cid, cnt in top:
            print(f"    Klient ID {cid}: {cnt} zakupów")
    print("=" * 45 + "\n")

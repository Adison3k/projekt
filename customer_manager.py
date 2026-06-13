"""
Moduł customer_manager - rejestracja i zarządzanie klientami księgarni.

Obsługuje dodawanie nowych klientów, usuwanie istniejących
oraz zapis danych do plików customer.csv, address.csv i indywidualnych
plików historii zakupów w folderze DATABASE.

Funkcje:
    register_customer(first_name, last_name, email, login, password, address_data)
    remove_customer(identifier)
    get_all_customers()
    get_customer_by_id(customer_id)
    customer_exists(customer_id)
"""

import pandas as pd
import hashlib
import random
import os
from datetime import datetime
from config import CUSTOMER_CSV, ADDRESS_CSV, DATABASE_DIR, ID_MIN, ID_MAX


# ─────────────────────────────────────────────
#  Pomocnicze funkcje wewnętrzne
# ─────────────────────────────────────────────

def _load_customers() -> pd.DataFrame:
    if not os.path.exists(CUSTOMER_CSV):
        return pd.DataFrame(columns=["id", "first_name", "last_name", "email",
                                     "login", "password_hash", "registration_date"])
    return pd.read_csv(CUSTOMER_CSV)


def _load_addresses() -> pd.DataFrame:
    if not os.path.exists(ADDRESS_CSV):
        return pd.DataFrame(columns=["customer_id", "street", "city", "postal_code", "country"])
    return pd.read_csv(ADDRESS_CSV)


def _save_customers(df: pd.DataFrame) -> None:
    df.to_csv(CUSTOMER_CSV, index=False)


def _save_addresses(df: pd.DataFrame) -> None:
    df.to_csv(ADDRESS_CSV, index=False)


def _hash_password(password: str) -> str:
    """Hashuje hasło użytkownika algorytmem SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_customer_id(df: pd.DataFrame) -> int:
    """
    Generuje unikalny 4-cyfrowy ID klienta.

    Losuje numer z zakresu ID_MIN–ID_MAX i upewnia się,
    że nie koliduje z istniejącymi ID w bazie.

    Args:
        df (pd.DataFrame): Aktualna baza klientów.

    Returns:
        int: Unikalny ID klienta.
    """
    existing_ids = set(df["id"].tolist()) if not df.empty else set()
    while True:
        new_id = random.randint(ID_MIN, ID_MAX)
        if new_id not in existing_ids:
            return new_id


def _create_purchase_file(customer_id: int) -> None:
    """Tworzy plik historii zakupów dla nowego klienta."""
    filepath = os.path.join(DATABASE_DIR, f"{customer_id}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"=== Historia zakupów klienta ID: {customer_id} ===\n")
        f.write(f"Konto założone: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")


# ─────────────────────────────────────────────
#  Dekorator walidujący dane klienta
# ─────────────────────────────────────────────

def validate_customer_data(func):
    """
    Dekorator sprawdzający poprawność danych wejściowych klienta.

    Weryfikuje, że imię, nazwisko i e-mail nie są puste
    oraz że adres e-mail zawiera znak '@'.
    """
    def wrapper(first_name, last_name, email, *args, **kwargs):
        if not first_name or not first_name.strip():
            raise ValueError("Imię nie może być puste.")
        if not last_name or not last_name.strip():
            raise ValueError("Nazwisko nie może być puste.")
        if not email or "@" not in email:
            raise ValueError("Nieprawidłowy adres e-mail.")
        return func(first_name, last_name, email, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────
#  Funkcje publiczne modułu
# ─────────────────────────────────────────────

@validate_customer_data
def register_customer(first_name, last_name, email, login, password, address_data=None):
    """
    Rejestruje nowego klienta w bazie danych.

    Dodaje klienta do customer.csv, jego adres do address.csv
    oraz tworzy indywidualny plik historii zakupów w folderze DATABASE.

    Args:
        first_name (str): Imię klienta.
        last_name (str): Nazwisko klienta.
        email (str): Adres e-mail (unikalny).
        login (str): Login do konta.
        password (str): Hasło (zostanie zahashowane SHA-256).
        address_data (dict, optional): Słownik z kluczami:
            'street', 'city', 'postal_code', 'country'.

    Returns:
        int: Nadany ID nowego klienta.

    Raises:
        ValueError: Gdy e-mail lub login już istnieje w bazie.

    Example:
        >>> cid = register_customer(
        ...     "Jan", "Kowalski", "jan@email.com",
        ...     "jkowalski", "haslo123",
        ...     {"street": "ul. Kwiatowa 1", "city": "Warszawa",
        ...      "postal_code": "00-001", "country": "Polska"}
        ... )
    """
    df_customers = _load_customers()

    # Sprawdzenie unikalności e-maila i loginu
    if not df_customers.empty:
        if email in df_customers["email"].values:
            raise ValueError(f"E-mail '{email}' jest już zarejestrowany.")
        if login in df_customers["login"].values:
            raise ValueError(f"Login '{login}' jest już zajęty.")

    new_id = _generate_customer_id(df_customers)
    today = datetime.now().strftime("%Y-%m-%d")

    new_customer = {
        "id": new_id,
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip(),
        "login": login.strip(),
        "password_hash": _hash_password(password),
        "registration_date": today
    }

    df_customers = pd.concat([df_customers, pd.DataFrame([new_customer])], ignore_index=True)
    _save_customers(df_customers)

    # Zapis adresu
    if address_data:
        df_addresses = _load_addresses()
        new_address = {
            "customer_id": new_id,
            "street": address_data.get("street", ""),
            "city": address_data.get("city", ""),
            "postal_code": address_data.get("postal_code", ""),
            "country": address_data.get("country", "Polska")
        }
        df_addresses = pd.concat([df_addresses, pd.DataFrame([new_address])], ignore_index=True)
        _save_addresses(df_addresses)

    # Tworzenie pliku historii zakupów
    _create_purchase_file(new_id)

    print(f"  Zarejestrowano klienta: {first_name} {last_name} (ID: {new_id})")
    return new_id


def remove_customer(identifier):
    """
    Usuwa klienta z bazy danych.

    Usuwa rekordy z customer.csv, address.csv oraz plik historii zakupów.
    Obsługuje usuwanie po ID (int) lub nazwisku/imieniu (str).

    Args:
        identifier (int | str): ID klienta (int) lub fragment imienia/nazwiska (str).

    Returns:
        bool: True jeśli usunięto, False jeśli nie znaleziono.

    Raises:
        ValueError: Gdy identifier jest nieprawidłowego typu.
    """
    df_customers = _load_customers()
    original_len = len(df_customers)

    if isinstance(identifier, int):
        to_remove = df_customers[df_customers["id"] == identifier]
        df_customers = df_customers[df_customers["id"] != identifier]
        label = f"ID={identifier}"
    elif isinstance(identifier, str):
        mask = (
            df_customers["first_name"].str.contains(identifier, case=False, na=False) |
            df_customers["last_name"].str.contains(identifier, case=False, na=False)
        )
        to_remove = df_customers[mask]
        df_customers = df_customers[~mask]
        label = f"NAME='{identifier}'"
    else:
        raise ValueError("Identifier musi być int (ID) lub str (nazwisko/imię).")

    if len(df_customers) == original_len:
        print(f"  Nie znaleziono klienta: {label}")
        return False

    # Usuń adresy
    removed_ids = to_remove["id"].tolist()
    df_addresses = _load_addresses()
    df_addresses = df_addresses[~df_addresses["customer_id"].isin(removed_ids)]
    _save_addresses(df_addresses)

    # Usuń pliki historii zakupów
    for cid in removed_ids:
        filepath = os.path.join(DATABASE_DIR, f"{cid}.txt")
        if os.path.exists(filepath):
            os.remove(filepath)

    _save_customers(df_customers)
    print(f"  Usunięto klienta: {label}")
    return True


def get_all_customers() -> pd.DataFrame:
    """Zwraca wszystkich klientów bez kolumny password_hash."""
    df = _load_customers()
    if "password_hash" in df.columns:
        return df.drop(columns=["password_hash"])
    return df


def get_customer_by_id(customer_id: int) -> pd.Series | None:
    """Zwraca dane klienta o podanym ID lub None."""
    df = _load_customers()
    result = df[df["id"] == customer_id]
    if result.empty:
        return None
    return result.iloc[0]


def customer_exists(customer_id: int) -> bool:
    """Sprawdza czy klient o podanym ID istnieje."""
    df = _load_customers()
    return int(customer_id) in df["id"].values


def authenticate_customer(login: str, password: str):
    """
    Weryfikuje dane logowania klienta.

    Args:
        login (str): Login klienta.
        password (str): Hasło w postaci jawnej.

    Returns:
        int | None: ID klienta jeśli dane poprawne, None w przeciwnym razie.
    """
    df = _load_customers()
    hashed = _hash_password(password)
    match = df[(df["login"] == login) & (df["password_hash"] == hashed)]
    if match.empty:
        return None
    return int(match.iloc[0]["id"])

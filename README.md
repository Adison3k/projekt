# System Obsługi Księgarni Internetowej

Pakiet w Pythonie (paradygmat funkcyjny + pandas) do obsługi klientów,
katalogu e-booków oraz zakupów internetowej księgarni.

## Struktura projektu

```
bookstore/
├── main.py              # Punkt wejścia (__main__), GUI + CLI
├── gui.py                # Graficzny interfejs użytkownika (Tkinter)
├── config.py             # Ścieżki plików i ustawienia globalne
├── book_manager.py       # Dodawanie/usuwanie e-booków (book.csv)
├── customer_manager.py   # Rejestracja/usuwanie klientów (customer.csv, address.csv)
├── purchase_manager.py   # Zakup e-booków, historia zakupów
├── stats_manager.py       # Statystyki i monitoring zasobów
├── __init__.py
└── DATABASE/
    ├── book.csv
    ├── customer.csv
    ├── address.csv
    └── <ID_klienta>.txt  # historia zakupów każdego klienta
```

## Wymagania

```
pip install pandas
```

(Tkinter wchodzi w standardową instalację Pythona)

## Uruchomienie

```
python main.py
```

Program najpierw próbuje uruchomić GUI. Jeśli Tkinter jest niedostępny,
przełącza się na tryb tekstowy (CLI).

## Konta

- **Administrator**: login `admin`, hasło `admin123` (zob. `config.py`)
- **Klienci**: rejestracja przez ekran "Zarejestruj się" w GUI lub
  funkcję `register_customer()`.

## Najważniejsze funkcje

### book_manager.py
- `add_book(title, author, genre, price, year)` – dodaje e-book do `book.csv`, nadaje nowy ID.
- `remove_book(identifier)` – usuwa e-book po ID (`int`) lub tytule (`str`).
- `find_book(query)` – wyszukuje e-booki po tytule/autorze.
- `get_all_books()` – zwraca cały katalog jako DataFrame.

### customer_manager.py
- `register_customer(first_name, last_name, email, login, password, address_data)`
  – tworzy nowego klienta, losuje 4-cyfrowy ID, zapisuje dane do `customer.csv`
  i `address.csv`, tworzy plik historii `DATABASE/<ID>.txt`.
- `remove_customer(identifier)` – usuwa klienta po ID (`int`) lub nazwisku/imieniu (`str`),
  usuwa adres i plik historii.
- `authenticate_customer(login, password)` – logowanie, zwraca ID lub `None`.

### purchase_manager.py
- `buy_books(customer_id, *book_ids)` – zakup **dowolnej liczby** e-booków jednocześnie;
  zapisuje wpisy (tytuł, autor, cena, data zakupu, data wygaśnięcia dostępu)
  do `DATABASE/<ID>.txt`.
- `buy_books_with_discount(customer_id, *book_ids)` – wersja z 10% rabatem
  (przykład dekoratora `apply_discount` – funkcji wyższego rzędu).
- `get_purchase_history(customer_id)` – zwraca treść pliku historii zakupów.

### stats_manager.py
- `get_bookstore_summary()` – liczba książek/klientów, ceny min/max/śr., liczba gatunków.
- `get_books_by_genre()` – zestawienie e-booków według gatunku.
- `get_top_customers(n)` – ranking klientów wg liczby zakupów.
- `print_summary()` – wypisuje statystyki w konsoli.

## Elementy wymagane przez specyfikację

| Wymaganie | Lokalizacja |
|---|---|
| Funkcja wyższego rzędu | `apply_discount()` w `purchase_manager.py` |
| Funkcja wielu zmiennych wejściowych | `add_book(*args, **kwargs)`, `buy_books(customer_id, *book_ids)` |
| Funkcja zagnieżdżona | `_build_new_row()` w `add_book`, `_format_purchase_entry()` w `buy_books` |
| Dekoratory | `log_book_operation`, `validate_customer_data`, `require_valid_customer`, `apply_discount` |
| Dokumentacja (docstringi) | wszystkie moduły + min. 3 funkcje na moduł |
| Obsługa wyjątków | `add_book`, `remove_book`, `register_customer`, `buy_books` |
| GUI | `gui.py` (Tkinter, panele admina i klienta) |
| Zakup wielu książek | `buy_books(customer_id, *book_ids)` (zaktualizowana wersja) |

## Przepływ danych

1. Admin loguje się (`admin` / `admin123`) → zarządza katalogiem i klientami.
2. Klient rejestruje się → otrzymuje losowe 4-cyfrowe ID i plik `DATABASE/<ID>.txt`.
3. Klient loguje się → przegląda katalog, kupuje e-booki (jeden lub wiele naraz).
4. Każdy zakup dopisuje wpis do `DATABASE/<ID>.txt` z datą zakupu i datą wygaśnięcia
   dostępu (`ACCESS_DAYS` w `config.py`, domyślnie 365 dni).
5. Admin może w każdej chwili sprawdzić statystyki (zakładka "Statystyki").



"""
Moduł konfiguracyjny pakietu Bookstore.
Przechowuje ścieżki do plików i stałe konfiguracyjne.
"""

import os

# Ścieżka bazowa projektu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "DATABASE")

# Ścieżki do plików CSV
BOOK_CSV = os.path.join(DATABASE_DIR, "book.csv")
CUSTOMER_CSV = os.path.join(DATABASE_DIR, "customer.csv")
ADDRESS_CSV = os.path.join(DATABASE_DIR, "address.csv")

# Konfiguracja dostępu do e-booka (dni)
ACCESS_DAYS = 365

# Zakres ID klientów
ID_MIN = 1000
ID_MAX = 9999

# Dane administratora
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123"

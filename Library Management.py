#!/usr/bin/env python3
"""
Library Management System (File-based)

• Console, menu–driven interface
• OOP design with single & multilevel inheritance
• storage in CSV files (books, users, loans)

CSV schema
──────────
books.csv   →  id,title,author,total,available
users.csv   →  id,name
loans.csv   →  user_id,book_id,borrow_date,return_date
"""
from __future__ import annotations
import csv
import datetime as dt
import os
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).with_suffix('')  # folder where script resides
BOOKS_FILE  = DATA_DIR / "books.csv"
USERS_FILE  = DATA_DIR / "users.csv"
LOANS_FILE  = DATA_DIR / "loans.csv"


# ────────────────────────────────────────────────────────────
# DATA MODELS
# ────────────────────────────────────────────────────────────
class Entity:                       # ← base class
    """Generic object that owns a numeric id."""
    _id_counter = 1

    def __init__(self, entity_id: Optional[int] = None):
        self.id = entity_id or Entity._id_counter
        Entity._id_counter = max(Entity._id_counter, self.id + 1)


class Book(Entity):                 # ← single inheritance
    def __init__(self, title: str, author: str,
                 total: int, available: int | None = None,
                 entity_id: Optional[int] = None):
        super().__init__(entity_id)
        self.title, self.author = title, author
        self.total = total
        self.available = available if available is not None else total

    # convenience helpers
    def to_row(self) -> List[str]:
        return [str(self.id), self.title, self.author,
                str(self.total), str(self.available)]

    @classmethod
    def from_row(cls, row: List[str]) -> "Book":
        bid, title, author, total, avail = row
        return cls(title, author, int(total), int(avail), int(bid))


class User(Entity):                 # ← single inheritance
    def __init__(self, name: str, entity_id: Optional[int] = None):
        super().__init__(entity_id)
        self.name = name

    def to_row(self) -> List[str]:
        return [str(self.id), self.name]

    @classmethod
    def from_row(cls, row: List[str]) -> "User":
        uid, name = row
        return cls(name, int(uid))


class Loan:                         # plain record (→ composition)
    DATE_FMT = "%Y-%m-%d"

    def __init__(self, user_id: int, book_id: int,
                 borrow_date: dt.date, return_date: Optional[dt.date]=None):
        self.user_id, self.book_id = user_id, book_id
        self.borrow_date, self.return_date = borrow_date, return_date

    def is_returned(self) -> bool:
        return self.return_date is not None

    def to_row(self) -> List[str]:
        rdate = self.return_date.strftime(self.DATE_FMT) if self.return_date else ''
        return [str(self.user_id), str(self.book_id),
                self.borrow_date.strftime(self.DATE_FMT), rdate]

    @classmethod
    def from_row(cls, row: List[str]) -> "Loan":
        uid, bid, bdate, rdate = row
        borrow_date = dt.datetime.strptime(bdate, cls.DATE_FMT).date()
        return_date = (dt.datetime.strptime(rdate, cls.DATE_FMT).date()
                       if rdate else None)
        return cls(int(uid), int(bid), borrow_date, return_date)


# ────────────────────────────────────────────────────────────
# PERSISTENCE LAYER
# ────────────────────────────────────────────────────────────
class CSVRepository:                # ← parent class
    """Abstract CSV persistence ; subclasses specify filename & model."""
    file: Path  = NotImplemented
    model      = NotImplemented     # Book / User / Loan

    @classmethod
    def load_all(cls) -> Dict[int, object]:
        if not cls.file.exists():
            return {}
        with cls.file.open(newline='', encoding='utf8') as fh:
            reader = csv.reader(fh)
            return {item.id: item
                    for item in (cls.model.from_row(r) for r in reader)}

    @classmethod
    def save_all(cls, objects: Dict[int, object]) -> None:
        cls.file.parent.mkdir(exist_ok=True)
        with cls.file.open('w', newline='', encoding='utf8') as fh:
            writer = csv.writer(fh)
            for obj in objects.values():
                writer.writerow(obj.to_row())


class BookRepo(CSVRepository):      # ← multilevel inheritance
    file, model = BOOKS_FILE, Book


class UserRepo(CSVRepository):
    file, model = USERS_FILE, User


class LoanRepo(CSVRepository):
    file, model = LOANS_FILE, Loan


# ────────────────────────────────────────────────────────────
# LIBRARY FACADE
# ────────────────────────────────────────────────────────────
class Library:
    def __init__(self) -> None:
        self.books: Dict[int, Book] = BookRepo.load_all()
        self.users: Dict[int, User] = UserRepo.load_all()
        self.loans: List[Loan]      = list(LoanRepo.load_all().values())

    # CRUD - BOOKS ───────────────────────
    def add_book(self, title: str, author: str, copies: int) -> None:
        book = Book(title, author, copies)
        self.books[book.id] = book
        BookRepo.save_all(self.books)

    def delete_book(self, book_id: int) -> bool:
        if book_id in self.books and self.books[book_id].available == self.books[book_id].total:
            self.books.pop(book_id)
            BookRepo.save_all(self.books)
            return True
        return False        # reject if copies issued

    # USERS ──────────────────────────────
    def add_user(self, name: str) -> None:
        user = User(name)
        self.users[user.id] = user
        UserRepo.save_all(self.users)

    # ISSUE / RETURN ─────────────────────
    def issue_book(self, user_id: int, book_id: int) -> bool:
        if (user_id in self.users and
                book_id in self.books and
                self.books[book_id].available > 0):
            self.books[book_id].available -= 1
            self.loans.append(
                Loan(user_id, book_id, dt.date.today()))
            BookRepo.save_all(self.books)
            LoanRepo.save_all({i: l for i, l in enumerate(self.loans)})
            return True
        return False

    def return_book(self, user_id: int, book_id: int) -> bool:
        for loan in self.loans:
            if (loan.user_id == user_id and loan.book_id == book_id
                    and not loan.is_returned()):
                loan.return_date = dt.date.today()
                self.books[book_id].available += 1
                BookRepo.save_all(self.books)
                LoanRepo.save_all({i: l for i, l in enumerate(self.loans)})
                return True
        return False

    # REPORTING ──────────────────────────
    def list_books(self) -> List[Book]:
        return sorted(self.books.values(), key=lambda b: b.id)

    def list_users(self) -> List[User]:
        return sorted(self.users.values(), key=lambda u: u.id)

    def user_loans(self, user_id: int) -> List[Loan]:
        return [l for l in self.loans if l.user_id == user_id and not l.is_returned()]


# ────────────────────────────────────────────────────────────
# CLI MENUS
# ────────────────────────────────────────────────────────────
def pause() -> None:
    input("\nPress <Enter> to continue...")

def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def header(text: str) -> None:
    print("=" * 60)
    print(text.center(60))
    print("=" * 60)

def main_menu(lib: Library) -> None:
    while True:
        clear()
        header("Library Management System")
        print(dedent("""\
            1. Add Book
            2. View Books
            3. Delete Book
            4. Register User
            5. View Users
            6. Issue Book
            7. Return Book
            8. View User Loans
            9. Exit"""))
        choice = input("Select option: ").strip()
        if choice == '1':
            add_book_menu(lib)
        elif choice == '2':
            list_books_menu(lib)
        elif choice == '3':
            del_book_menu(lib)
        elif choice == '4':
            add_user_menu(lib)
        elif choice == '5':
            list_users_menu(lib)
        elif choice == '6':
            issue_menu(lib)
        elif choice == '7':
            return_menu(lib)
        elif choice == '8':
            loans_menu(lib)
        elif choice == '9':
            break
        else:
            print("Invalid option!")
            pause()

# individual menu helpers (brevity - simple input validation)
def add_book_menu(lib: Library):
    clear(); header("Add Book")
    title  = input("Title : ")
    author = input("Author: ")
    copies = int(input("Total copies: "))
    lib.add_book(title, author, copies)
    print("Book added successfully!")
    pause()

def list_books_menu(lib: Library):
    clear(); header("Available Books")
    print(f"{'ID':<5}{'Title':<30}{'Author':<20}{'Avail/Total'}")
    for b in lib.list_books():
        print(f"{b.id:<5}{b.title:<30}{b.author:<20}{b.available}/{b.total}")
    pause()

def del_book_menu(lib: Library):
    clear(); header("Delete Book")
    bid = int(input("Enter Book ID to delete: "))
    if lib.delete_book(bid):
        print("Book deleted.")
    else:
        print("Cannot delete (inexistent or copies issued).")
    pause()

def add_user_menu(lib: Library):
    clear(); header("Register User")
    name = input("User name: ")
    lib.add_user(name)
    print("User registered.")
    pause()

def list_users_menu(lib: Library):
    clear(); header("Registered Users")
    print(f"{'ID':<5}{'Name'}")
    for u in lib.list_users():
        print(f"{u.id:<5}{u.name}")
    pause()

def issue_menu(lib: Library):
    clear(); header("Issue Book")
    uid = int(input("User ID : "))
    bid = int(input("Book ID : "))
    if lib.issue_book(uid, bid):
        print("Book issued.")
    else:
        print("Error issuing book (check IDs / availability).")
    pause()

def return_menu(lib: Library):
    clear(); header("Return Book")
    uid = int(input("User ID : "))
    bid = int(input("Book ID : "))
    if lib.return_book(uid, bid):
        print("Book returned. Thank you!")
    else:
        print("Error processing return.")
    pause()

def loans_menu(lib: Library):
    clear(); header("User Loans")
    uid = int(input("User ID : "))
    loans = lib.user_loans(uid)
    if loans:
        print(f"\nBooks currently borrowed by user {uid}:")
        for loan in loans:
            book = lib.books[loan.book_id]
            print(f"• {book.title} (since {loan.borrow_date})")
    else:
        print("No active loans.")
    pause()


# ────────────────────────────────────────────────────────────
# ENTRY POINT
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    library = Library()
    try:
        main_menu(library)
    finally:
        # Persist again on exit (safety)
        BookRepo.save_all(library.books)
        UserRepo.save_all(library.users)
        LoanRepo.save_all({i: l for i, l in enumerate(library.loans)})

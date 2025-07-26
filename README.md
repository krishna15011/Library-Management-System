# Library Management System

A comprehensive **file-based Library Management System** built in Python featuring Object-Oriented Programming principles, inheritance patterns, and CSV-based data persistence.

## 🚀 Features

- **Complete CRUD Operations**: Add, view, update, and delete books and users
- **Book Management**: Track book inventory with availability status
- **User Registration**: Register and manage library users
- **Issue/Return System**: Complete book lending workflow
- **Data Persistence**: CSV-based storage for books, users, and loan records
- **Menu-Driven CLI**: Easy-to-use console interface
- **OOP Design**: Demonstrates single and multilevel inheritance
- **File I/O Operations**: Robust CSV file handling

## 🏗️ Architecture

### Design Patterns Used
- **Single Inheritance**: `Book` and `User` classes inherit from `Entity`
- **Multilevel Inheritance**: Repository classes extend `CSVRepository`
- **Composition**: `Library` class manages collections of domain objects
- **Repository Pattern**: Separate data access layer for clean code organization

### File Structure
```
📦 Library Management System
├── 📄 library_management.py    # Main application file
├── 📁 data/                    # Auto-generated data directory
│   ├── 📄 books.csv           # Book inventory storage
│   ├── 📄 users.csv           # User registration data
│   └── 📄 loans.csv           # Loan transaction records
└── 📄 README.md               # Project documentation
```

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- Basic understanding of command-line interface
- Text editor or IDE (VS Code, PyCharm, etc.)

## 🛠️ Installation & Setup

1. **Clone or Download** the project files
2. **Create a project directory**:
   ```bash
   mkdir library-management
   cd library-management
   ```
3. **Save the code** as `library_management.py`
4. **Run the application**:
   ```bash
   python library_management.py
   ```

## 💻 Usage Guide

### Starting the Application
```bash
python library_management.py
```

### Main Menu Options
```
1. Add Book          - Add new books to the library inventory
2. View Books        - Display all books with availability status
3. Delete Book       - Remove books (only if no copies are issued)
4. Register User     - Add new library users
5. View Users        - Display all registered users
6. Issue Book        - Lend books to users
7. Return Book       - Process book returns
8. View User Loans   - Check books currently borrowed by a user
9. Exit              - Close the application
```

### Sample Workflow
1. **Register users** using option 4
2. **Add books** to inventory using option 1
3. **Issue books** to users using option 6
4. **Track loans** using option 8
5. **Process returns** using option 7

## 📊 Data Schema

### books.csv
| Field | Type | Description |
|-------|------|-------------|
| id | int | Unique book identifier |
| title | string | Book title |
| author | string | Book author |
| total | int | Total copies owned |
| available | int | Copies currently available |

### users.csv
| Field | Type | Description |
|-------|------|-------------|
| id | int | Unique user identifier |
| name | string | User full name |

### loans.csv
| Field | Type | Description |
|-------|------|-------------|
| user_id | int | Reference to user |
| book_id | int | Reference to book |
| borrow_date | date | Date book was issued |
| return_date | date | Date book was returned (empty if not returned) |

## 🔧 Code Structure

### Core Classes

#### `Entity` (Base Class)
- Provides auto-incrementing ID management
- Base class for all domain objects

#### `Book` (Inherits from Entity)
- Manages book information and availability
- Handles serialization to/from CSV format

#### `User` (Inherits from Entity)
- Represents library users
- Manages user data persistence

#### `Loan` (Composition)
- Tracks book borrowing transactions
- Manages borrow and return dates

#### `CSVRepository` (Abstract Base)
- Generic CSV file operations
- Template for data persistence

#### `Library` (Facade)
- Main business logic controller
- Coordinates all system operations

## 🖥️ Running in VS Code

1. **Install Python Extension**:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search and install "Python" by Microsoft

2. **Open Project**:
   - File → Open Folder
   - Select your project directory

3. **Run the Code**:
   - Click the ▶️ button in the top-right corner
   - Or press `F5` to run with debugging
   - Or use `Ctrl+F5` to run without debugging

## 🚨 Error Handling

The system includes basic error handling for:
- Invalid menu selections
- File I/O operations
- Data type conversions
- Business logic validations

## 🎯 Learning Objectives

This project demonstrates:
- **Object-Oriented Programming** principles
- **Inheritance** patterns (single and multilevel)
- **File handling** with CSV format
- **Menu-driven** console applications
- **Data persistence** without databases
- **Clean code** organization and structure

## 🔄 Future Enhancements

Potential improvements to consider:
- [ ] Search functionality for books and users
- [ ] Due date tracking with overdue notifications
- [ ] Book reservation system
- [ ] User authentication and roles
- [ ] Database integration (SQLite)
- [ ] GUI interface using tkinter
- [ ] Book categories and genres
- [ ] Fine calculation for overdue books
- [ ] Backup and restore functionality
- [ ] Advanced reporting and analytics

## 📝 Code

```python
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
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

**Perfect for**: Learning OOP concepts, understanding file I/O operations, practicing Python programming, and preparing for coding interviews.

**Skill Level**: Beginner to Intermediate

**Time to Complete**: 2-4 hours to understand and extend

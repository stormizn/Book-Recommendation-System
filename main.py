"""
Book Recommendation System
==========================

A menu-driven, console-based book recommendation system built with Python and
MySQL for the Class 12 CBSE Computer Science practical.

Main features
-------------
1.  User registration and login (passwords are stored as salted PBKDF2 hashes).
2.  Browse the catalogue, filter it by genre and view complete book details.
3.  Search books by title, author or genre.
4.  Rate a book from 1 to 5 and change that rating later.
5.  Keep a personal reading list (add, view and remove books).
6.  Get content-based recommendations from the genres rated highly by the user.
7.  View a profile page with the user's own rating statistics.

Before running this program, create the database with `database.sql` and fill
it with sample books using `sample_data.sql`.
"""

import getpass
import hashlib
import hmac
import os
import secrets
import sys

import mysql.connector

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
# Either edit the values below or set these four environment variables:
#   BOOK_DB_HOST, BOOK_DB_PORT, BOOK_DB_USER, BOOK_DB_PASSWORD, BOOK_DB_NAME
HOST = os.environ.get("BOOK_DB_HOST", "localhost")
PORT = int(os.environ.get("BOOK_DB_PORT", "3306"))
USER = os.environ.get("BOOK_DB_USER", "root")
PASSWORD = os.environ.get("BOOK_DB_PASSWORD", "stormizn@sql1234$<>")
DATABASE = os.environ.get("BOOK_DB_NAME", "book_recommendation_db")

# ---------------------------------------------------------------------------
# Application settings
# ---------------------------------------------------------------------------
# A genre counts as "liked" when the user's average rating in it is >= 3.0.
PREFERRED_GENRE_THRESHOLD = 3.0
# Maximum number of recommendations shown in one go.
RECOMMENDATION_LIMIT = 10
# Books shown per page while browsing or searching.
PAGE_SIZE = 15

# Column widths used by print_table() so that every table lines up exactly.
BOOK_WIDTHS = (4, 28, 20, 16)

# Password hashing settings (PBKDF2-HMAC-SHA256).
HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 100000
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 64


class Session:
    """Stores the details of the user who is currently logged in."""

    def __init__(self):
        self.user_id = None
        self.username = ""

    @property
    def is_logged_in(self):
        """Return True when a user is currently logged in."""
        return self.user_id is not None

    def login(self, user_id, username):
        """Remember the user who just logged in."""
        self.user_id = user_id
        self.username = username

    def logout(self):
        """Forget the logged-in user."""
        self.user_id = None
        self.username = ""


# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------
def connect_database():
    """Open and return a connection to the MySQL database."""
    return mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        charset="utf8mb4",
        connect_timeout=10,
    )


def report_database_error(error, connection=None):
    """Print a friendly message instead of a Python traceback."""
    if connection is not None:
        try:
            connection.rollback()
        except mysql.connector.Error:
            pass

    hints = {
        1045: "MySQL refused the login - check USER and PASSWORD in main.py.",
        1049: "The database does not exist - run database.sql first.",
        1062: "That record already exists (duplicate value).",
        1146: "A table is missing - run database.sql to create the tables.",
        1406: "A value is too long for its column.",
        2003: "Cannot reach the MySQL server - is it running?",
        2006: "The connection to MySQL was lost.",
        2013: "The connection to MySQL timed out.",
        2055: "The connection to MySQL was lost.",
    }
    errno = getattr(error, "errno", None)
    message = hints.get(errno, str(error))
    print(f"\n[Database error] {message}")
    print("The action could not be completed. Please try again.")


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------
def read_line(prompt=""):
    """Read one line of input; close cleanly on Ctrl+C or Ctrl+D."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled - closing the program.")
        raise SystemExit(0)


def get_int(prompt, low, high):
    """Take a whole number from the user between `low` and `high`."""
    while True:
        raw = read_line(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"Invalid input! Please enter a whole number "
                  f"between {low} and {high}.")
            continue
        if low <= value <= high:
            return value
        print(f"Please enter a number between {low} and {high}.")


def get_text(prompt, min_length=1, max_length=255):
    """Take a non-empty text input whose length is within the given limits."""
    while True:
        value = read_line(prompt).strip()
        if len(value) < min_length:
            print(f"Please enter at least {min_length} character(s).")
        elif len(value) > max_length:
            print(f"Please keep it within {max_length} characters.")
        else:
            return value


def get_password(prompt, min_length=MIN_PASSWORD_LENGTH,
                 max_length=MAX_PASSWORD_LENGTH):
    """Take a hidden password input (characters are not echoed)."""
    while True:
        try:
            password = getpass.getpass(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled - closing the program.")
            raise SystemExit(0)

        if password.strip() == "":
            print("The password cannot be empty.")
        elif len(password) < min_length:
            print(f"The password must be at least "
                  f"{min_length} characters long.")
        elif len(password) > max_length:
            print(f"The password must be at most "
                  f"{max_length} characters long.")
        else:
            return password


def ask_yes_no(prompt):
    """Ask a yes/no question and return True or False."""
    while True:
        answer = read_line(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer 'y' for yes or 'n' for no.")


# ---------------------------------------------------------------------------
# Password hashing helpers
# ---------------------------------------------------------------------------
def hash_password(password):
    """Return a salted hash in the form algorithm$iterations$salt$digest."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        HASH_ITERATIONS,
    ).hex()
    return f"{HASH_ALGORITHM}${HASH_ITERATIONS}${salt}${digest}"


def needs_hash_upgrade(stored_hash):
    """Return True when a row still holds an old plain-text password."""
    return not stored_hash.startswith(HASH_ALGORITHM + "$")


def verify_password(password, stored_hash):
    """Compare a typed password with the value stored in the users table."""
    if needs_hash_upgrade(stored_hash):
        # Rows created by older versions of this program stored plain text.
        return hmac.compare_digest(
            password.encode("utf-8"), stored_hash.encode("utf-8")
        )

    try:
        _, iterations, salt, digest = stored_hash.split("$")
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        ).hex()
    except (ValueError, TypeError):
        return False

    return hmac.compare_digest(
        candidate.encode("utf-8"), digest.encode("utf-8")
    )


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------
def fit_cell(value, width):
    """Cut or pad a value so that it occupies exactly `width` characters."""
    text = "" if value is None else str(value)
    if len(text) > width:
        text = text[: width - 3].rstrip() + "..."
    return text.ljust(width)


def print_table(headers, rows, widths):
    """Print an aligned table with a header row and separator lines."""
    total_width = sum(widths) + 2 * (len(widths) - 1)

    def build_line(cells):
        cells = list(cells) + [""] * (len(widths) - len(cells))
        return "  ".join(fit_cell(cell, width)
                         for cell, width in zip(cells, widths))

    print(build_line(headers))
    print("-" * total_width)
    for row in rows:
        print(build_line(row))
    print("-" * total_width)


def display_books(rows):
    """Display (book_id, title, author, genre) rows as a table."""
    if not rows:
        print("\nNo books found!")
        return
    print_table(("ID", "Title", "Author", "Genre"), rows, BOOK_WIDTHS)


def display_books_paged(rows, page_size=PAGE_SIZE):
    """Display books page by page so long lists do not flood the console."""
    if not rows:
        print("\nNo books found!")
        return

    total = len(rows)
    if total <= page_size:
        display_books(rows)
        print(f"Total: {total} book(s).")
        return

    for start in range(0, total, page_size):
        page = rows[start:start + page_size]
        print(f"\nShowing books {start + 1}-{start + len(page)} of {total}")
        display_books(page)
        if start + page_size >= total:
            break
        answer = read_line("Press Enter for the next page, or 'q' to stop: ")
        if answer.strip().lower() == "q":
            print("Stopped listing.")
            return


# ---------------------------------------------------------------------------
# Small database helpers
# ---------------------------------------------------------------------------
def max_book_id(cursor):
    """Return the highest book_id in the catalogue (0 when it is empty)."""
    cursor.execute("SELECT COALESCE(MAX(book_id), 0) FROM books")
    return cursor.fetchone()[0]


def choose_genre(cursor):
    """Let the user pick a genre from a numbered list of available genres."""
    cursor.execute(
        "SELECT DISTINCT genre FROM books "
        "WHERE genre IS NOT NULL ORDER BY genre"
    )
    genres = [row[0] for row in cursor.fetchall()]

    if not genres:
        print("The catalogue has no books yet.")
        return None

    print("\nAvailable genres:")
    for number, genre in enumerate(genres, start=1):
        print(f"  {number}. {genre}")

    position = get_int("Enter the genre number (0 to cancel): ",
                       0, len(genres))
    if position == 0:
        return None
    return genres[position - 1]


# ---------------------------------------------------------------------------
# User accounts
# ---------------------------------------------------------------------------
def register_user(connection):
    """Create a new user account."""
    print("\n--- Create a new account ---")
    username = get_text("Choose a username (3-50 characters): ", 3, 50)

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s", (username,)
        )
        if cursor.fetchone() is not None:
            print("That username is already taken - please pick another.")
            return

        password = get_password(
            f"Choose a password ({MIN_PASSWORD_LENGTH}-"
            f"{MAX_PASSWORD_LENGTH} characters): "
        )
        confirm = get_password("Re-enter the password to confirm: ")
        if password != confirm:
            print("The two passwords do not match - account not created.")
            return

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hash_password(password)),
        )
        connection.commit()
        print(f"Account '{username}' created successfully! Please log in.")
    finally:
        cursor.close()


def login_user(connection, session):
    """Log an existing user in. Returns True on success."""
    print("\n--- Log in ---")
    username = get_text("Username: ", 1, 50)
    password = get_password("Password: ", min_length=1)

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT user_id, username, password_hash "
            "FROM users WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()

        if row is None or not verify_password(password, row[2]):
            print("Invalid username or password. Please try again.")
            return False

        if needs_hash_upgrade(row[2]):
            # Upgrade a plain-text password from an older version.
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (hash_password(password), row[0]),
            )
            connection.commit()
            print("(Your stored password was upgraded to a secure hash.)")

        session.login(row[0], row[1])
        print(f"Login successful! Welcome, {session.username}.")
        return True
    finally:
        cursor.close()


def login_menu(connection, session):
    """Show the register/login menu. True once a user logs in."""
    while True:
        print()
        print("=" * 44)
        print("   BOOK RECOMMENDATION SYSTEM")
        print("=" * 44)
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = get_int("Enter your choice (1-3): ", 1, 3)

        try:
            if choice == 1:
                register_user(connection)
            elif choice == 2:
                if login_user(connection, session):
                    return True
            else:
                print("Goodbye - thank you for using the "
                      "Book Recommendation System!")
                return False
        except mysql.connector.Error as error:
            report_database_error(error, connection)
        except Exception as error:
            print(f"\n[Unexpected problem] {type(error).__name__}: {error}")
            print("The program is still running - please try again.")


# ---------------------------------------------------------------------------
# Browsing, searching and book details
# ---------------------------------------------------------------------------
def show_book_details(cursor, session):
    """Show every stored detail about one book, plus its average rating."""
    highest_id = max_book_id(cursor)
    if highest_id == 0:
        print("There are no books in the catalogue yet.")
        return

    book_id = get_int(f"Enter the book ID (1-{highest_id}): ", 1, highest_id)
    cursor.execute(
        """SELECT b.title, b.author, b.genre, b.book_description,
                  ROUND(AVG(r.rating), 1), COUNT(r.rating_id)
           FROM books b
           LEFT JOIN ratings r ON r.book_id = b.book_id
           WHERE b.book_id = %s
           GROUP BY b.book_id, b.title, b.author, b.genre,
                    b.book_description""",
        (book_id,),
    )
    row = cursor.fetchone()
    if row is None:
        print("Book not found! Please check the book ID and try again.")
        return

    title, author, genre, description, average, number_of_ratings = row
    if number_of_ratings:
        rating_text = (f"{float(average):.1f}/5 from "
                       f"{number_of_ratings} reader(s)")
    else:
        rating_text = "not rated yet"

    print()
    print("=" * 60)
    print(f"Title       : {title}")
    print(f"Author      : {author}")
    print(f"Genre       : {genre if genre else 'Unknown'}")
    print(f"Rating      : {rating_text}")
    print(f"Description : {description if description else 'Not available.'}")

    if session.is_logged_in:
        cursor.execute(
            "SELECT rating FROM ratings WHERE user_id = %s AND book_id = %s",
            (session.user_id, book_id),
        )
        own_rating = cursor.fetchone()
        if own_rating:
            print(f"Your rating : {own_rating[0]}/5")
        else:
            print("Your rating : not rated yet")
    print("=" * 60)


def browse_books(connection, session):
    """Browse all books, filter them by genre, or open one book's details."""
    print("\n1. Show all books")
    print("2. Filter by genre")
    print("3. View full details of a book")
    choice = get_int("Enter your choice (1-3): ", 1, 3)

    cursor = connection.cursor()
    try:
        if choice == 1:
            cursor.execute(
                "SELECT book_id, title, author, genre "
                "FROM books ORDER BY book_id"
            )
            display_books_paged(cursor.fetchall())
        elif choice == 2:
            genre = choose_genre(cursor)
            if genre is None:
                print("Cancelled.")
                return
            cursor.execute(
                "SELECT book_id, title, author, genre FROM books "
                "WHERE genre = %s ORDER BY title",
                (genre,),
            )
            rows = cursor.fetchall()
            print(f"\nBooks in the '{genre}' genre:")
            display_books_paged(rows)
        else:
            show_book_details(cursor, session)
    finally:
        cursor.close()


def escape_like(text):
    """Escape the wildcards % and _ so they are searched for literally."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_books(connection):
    """Search the catalogue by title, author or genre."""
    print("\n1. Search by title")
    print("2. Search by author")
    print("3. Search by genre")
    choice = get_int("Enter your choice (1-3): ", 1, 3)

    keyword = get_text("Enter the search keyword: ", 1, 100)
    pattern = "%" + escape_like(keyword) + "%"

    # Each menu choice maps to its own fixed query, so the searchable column
    # can never come from user input.
    queries = {
        1: ("SELECT book_id, title, author, genre FROM books "
            "WHERE title LIKE %s ORDER BY title"),
        2: ("SELECT book_id, title, author, genre FROM books "
            "WHERE author LIKE %s ORDER BY author, title"),
        3: ("SELECT book_id, title, author, genre FROM books "
            "WHERE genre LIKE %s ORDER BY genre, title"),
    }

    cursor = connection.cursor()
    try:
        cursor.execute(queries[choice], (pattern,))
        rows = cursor.fetchall()
        print(f"\nSearch results for '{keyword}':")
        display_books_paged(rows)
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Rating a book
# ---------------------------------------------------------------------------
def rate_book(connection, session):
    """Add a rating, or change the rating the user gave earlier."""
    cursor = connection.cursor()
    try:
        highest_id = max_book_id(cursor)
        if highest_id == 0:
            print("There are no books in the catalogue yet.")
            return

        book_id = get_int(f"Enter the book ID to rate (1-{highest_id}): ",
                          1, highest_id)
        cursor.execute(
            "SELECT title FROM books WHERE book_id = %s", (book_id,)
        )
        book = cursor.fetchone()
        if book is None:
            print("Book not found! Please check the book ID and try again.")
            return
        title = book[0]

        cursor.execute(
            "SELECT rating_id, rating FROM ratings "
            "WHERE user_id = %s AND book_id = %s",
            (session.user_id, book_id),
        )
        existing = cursor.fetchone()

        if existing is None:
            rating = get_int(f"How would you rate '{title}' (1-5)? ", 1, 5)
            cursor.execute(
                "INSERT INTO ratings (user_id, book_id, rating) "
                "VALUES (%s, %s, %s)",
                (session.user_id, book_id, rating),
            )
            connection.commit()
            print(f"Thank you! You rated '{title}' {rating}/5.")
            return

        print(f"You already rated '{title}' {existing[1]}/5.")
        if not ask_yes_no("Do you want to change that rating? (y/n): "):
            print("Your rating was left unchanged.")
            return

        rating = get_int("Enter the new rating (1-5): ", 1, 5)
        cursor.execute(
            "UPDATE ratings SET rating = %s WHERE rating_id = %s",
            (rating, existing[0]),
        )
        connection.commit()
        print(f"Rating updated! '{title}' is now rated {rating}/5.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Reading list
# ---------------------------------------------------------------------------
def reading_list_menu(connection, session):
    """View, add to, or remove from the user's reading list."""
    print("\n1. View my reading list")
    print("2. Add a book to my reading list")
    print("3. Remove a book from my reading list")
    choice = get_int("Enter your choice (1-3): ", 1, 3)

    cursor = connection.cursor()
    try:
        if choice == 1:
            cursor.execute(
                """SELECT b.book_id, b.title, b.author, b.genre
                   FROM reading_lists rl
                   JOIN books b ON rl.book_id = b.book_id
                   WHERE rl.user_id = %s
                   ORDER BY b.title""",
                (session.user_id,),
            )
            rows = cursor.fetchall()
            if not rows:
                print("\nYour reading list is empty. "
                      "Use option 2 to add a book.")
                return
            display_books_paged(rows)
        elif choice == 2:
            add_to_reading_list(cursor, connection, session)
        else:
            remove_from_reading_list(cursor, connection, session)
    finally:
        cursor.close()


def add_to_reading_list(cursor, connection, session):
    """Add one book to the user's reading list."""
    highest_id = max_book_id(cursor)
    if highest_id == 0:
        print("There are no books in the catalogue yet.")
        return

    book_id = get_int(f"Enter the book ID to add (1-{highest_id}): ",
                      1, highest_id)
    cursor.execute("SELECT title FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    if book is None:
        print("Book not found! Please check the book ID and try again.")
        return

    cursor.execute(
        "SELECT list_id FROM reading_lists "
        "WHERE user_id = %s AND book_id = %s",
        (session.user_id, book_id),
    )
    if cursor.fetchone() is not None:
        print("This book is already in your reading list!")
        return

    cursor.execute(
        "INSERT INTO reading_lists (user_id, book_id) VALUES (%s, %s)",
        (session.user_id, book_id),
    )
    connection.commit()
    print(f"'{book[0]}' has been added to your reading list!")


def remove_from_reading_list(cursor, connection, session):
    """Remove one book from the user's reading list."""
    cursor.execute(
        """SELECT b.book_id, b.title
           FROM reading_lists rl
           JOIN books b ON rl.book_id = b.book_id
           WHERE rl.user_id = %s
           ORDER BY b.title""",
        (session.user_id,),
    )
    rows = cursor.fetchall()

    if not rows:
        print("Your reading list is empty.")
        return

    print("\nYour reading list:")
    for number, (_, title) in enumerate(rows, start=1):
        print(f"  {number}. {title}")

    position = get_int("Enter the number to remove (0 to cancel): ",
                       0, len(rows))
    if position == 0:
        print("Cancelled.")
        return

    book_id, title = rows[position - 1]
    cursor.execute(
        "DELETE FROM reading_lists WHERE user_id = %s AND book_id = %s",
        (session.user_id, book_id),
    )
    connection.commit()
    print(f"'{title}' was removed from your reading list.")


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------
def get_recommendations(connection, session):
    """Recommend unread books from the genres the user rates highly."""
    cursor = connection.cursor()
    try:
        # Step 1: work out the user's favourite genres with SQL aggregates.
        cursor.execute(
            """SELECT b.genre, AVG(r.rating), COUNT(*)
               FROM ratings r
               JOIN books b ON b.book_id = r.book_id
               WHERE r.user_id = %s
               GROUP BY b.genre
               HAVING AVG(r.rating) >= %s
               ORDER BY AVG(r.rating) DESC, b.genre""",
            (session.user_id, PREFERRED_GENRE_THRESHOLD),
        )
        preferred_genres = cursor.fetchall()

        if not preferred_genres:
            cursor.execute(
                "SELECT COUNT(*) FROM ratings WHERE user_id = %s",
                (session.user_id,),
            )
            if cursor.fetchone()[0] == 0:
                print("You have not rated any book yet! Rate a few books "
                      "first so that the system can learn your taste.")
            else:
                print("None of your genres has an average rating of "
                      f"{PREFERRED_GENRE_THRESHOLD} or more yet, so there is "
                      "nothing to recommend. Try rating more books!")
            return

        genres = [row[0] for row in preferred_genres]

        # Step 2: collect unread books from those genres, skipping books that
        # are already in the reading list, and bring their average score.
        placeholders = ", ".join(["%s"] * len(genres))
        query = f"""
            SELECT b.book_id, b.title, b.author, b.genre,
                   COALESCE(AVG(r.rating), 0) AS average_rating,
                   COUNT(r.rating_id) AS number_of_ratings
            FROM books b
            LEFT JOIN ratings r ON r.book_id = b.book_id
            WHERE b.genre IN ({placeholders})
              AND b.book_id NOT IN (
                  SELECT book_id FROM ratings WHERE user_id = %s
              )
              AND b.book_id NOT IN (
                  SELECT book_id FROM reading_lists WHERE user_id = %s
              )
            GROUP BY b.book_id, b.title, b.author, b.genre
            ORDER BY number_of_ratings DESC, average_rating DESC, b.title
        """
        cursor.execute(query, genres + [session.user_id, session.user_id])
        candidates = cursor.fetchall()

        if not candidates:
            print("No new books are left in your favourite genres - you have "
                  "already rated or saved all of them!")
            return

        # Step 3: put the strongest genre first, then the most popular books.
        genre_rank = {genre: rank for rank, genre in enumerate(genres)}
        candidates.sort(
            key=lambda row: (genre_rank.get(row[3], len(genres)),
                             -row[5],
                             -float(row[4]),
                             row[1].lower())
        )
        shortlist = candidates[:RECOMMENDATION_LIMIT]

        genre_list = ", ".join(
            f"{genre} ({float(average):.1f}/5)"
            for genre, average, _ in preferred_genres
        )
        print(f"\nYour favourite genres: {genre_list}")
        print(f"Top {len(shortlist)} of {len(candidates)} matching book(s), "
              "best genre first:")
        display_books([(row[0], row[1], row[2], row[3])
                       for row in shortlist])
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
def show_profile(connection, session):
    """Show the logged-in user's rating statistics and reading history."""
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT created_at FROM users WHERE user_id = %s",
            (session.user_id,),
        )
        member_since = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*), COALESCE(AVG(rating), 0) "
            "FROM ratings WHERE user_id = %s",
            (session.user_id,),
        )
        rated_count, average_rating = cursor.fetchone()

        cursor.execute(
            "SELECT COUNT(*) FROM reading_lists WHERE user_id = %s",
            (session.user_id,),
        )
        saved_count = cursor.fetchone()[0]

        print()
        print("=" * 56)
        print(f"  PROFILE - {session.username}")
        print("=" * 56)
        print(f"  Member since     : {str(member_since).split(' ')[0]}")
        print(f"  Books rated      : {rated_count}")
        if rated_count:
            print(f"  Average rating   : {float(average_rating):.1f}/5")
        else:
            print("  Average rating   : -")
        print(f"  Reading list     : {saved_count} book(s)")

        if rated_count:
            cursor.execute(
                """SELECT b.genre, AVG(r.rating), COUNT(*)
                   FROM ratings r
                   JOIN books b ON b.book_id = r.book_id
                   WHERE r.user_id = %s
                   GROUP BY b.genre
                   ORDER BY AVG(r.rating) DESC, b.genre""",
                (session.user_id,),
            )
            print("  Genre averages   :")
            for genre, genre_average, count in cursor.fetchall():
                print(f"      {fit_cell(genre, 18)}"
                      f"{float(genre_average):.1f}/5  ({count} book(s))")

            cursor.execute(
                """SELECT b.title, r.rating
                   FROM ratings r
                   JOIN books b ON b.book_id = r.book_id
                   WHERE r.user_id = %s
                   ORDER BY b.title""",
                (session.user_id,),
            )
            print("\n  Books you have rated:")
            for title, rating in cursor.fetchall():
                print(f"      {fit_cell(title, 40)}{rating}/5")
        print("=" * 56)
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Main menu and program entry point
# ---------------------------------------------------------------------------
def main_menu(connection, session):
    """Show the main menu. Returns 'logout' or 'exit'."""
    # Keeping the labels next to their numbers means the menu and the
    # dispatch below can never drift apart.
    actions = {
        1: "Browse Books",
        2: "Search Books",
        3: "Rate a Book",
        4: "My Reading List",
        5: "Get Recommendations",
        6: "My Profile",
        7: "Log Out",
        8: "Exit",
    }

    while True:
        print()
        print("=" * 44)
        print(f"  MAIN MENU - {session.username}")
        print("=" * 44)
        for number, name in actions.items():
            print(f"{number}. {name}")
        choice = get_int("Enter your choice (1-8): ", 1, 8)

        # Echo the choice straight away: the user always gets visible
        # feedback, even when the option itself has no output.
        if choice <= 6:
            print(f"\n--- {actions[choice]} ---")

        try:
            if choice == 1:
                browse_books(connection, session)
            elif choice == 2:
                search_books(connection)
            elif choice == 3:
                rate_book(connection, session)
            elif choice == 4:
                reading_list_menu(connection, session)
            elif choice == 5:
                get_recommendations(connection, session)
            elif choice == 6:
                show_profile(connection, session)
            elif choice == 7:
                session.logout()
                print("You have been logged out.")
                return "logout"
            else:
                print("Goodbye - thank you for using the "
                      "Book Recommendation System!")
                return "exit"
        except mysql.connector.Error as error:
            report_database_error(error, connection)
        except Exception as error:
            # Last line of defence: an unexpected problem must never kill
            # the program or leave the user staring at a silent screen.
            print(f"\n[Unexpected problem] {type(error).__name__}: {error}")
            print("That option could not finish, but the program is still "
                  "running.")


def use_line_buffering():
    """Make every print appear immediately, even in IDE consoles and pipes."""
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass


def run_self_check():
    """Check the connection, the tables and the three main menu options.

    Run it with:  python main.py --check
    It needs no typing, so it also works when the normal menu misbehaves.
    """
    use_line_buffering()
    print("BOOK RECOMMENDATION SYSTEM - SELF CHECK")
    print("-" * 44)

    try:
        connection = connect_database()
    except mysql.connector.Error as error:
        report_database_error(error)
        return 1

    try:
        print("Connection      : OK")
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT VERSION()")
            print(f"MySQL version   : {cursor.fetchone()[0]}")
            # The table names come from this fixed list, never from input.
            for table in ("users", "books", "ratings", "reading_lists"):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"{table:16}: {cursor.fetchone()[0]} row(s)")
            cursor.execute(
                "SELECT user_id, username FROM users ORDER BY user_id LIMIT 1"
            )
            first_user = cursor.fetchone()
        finally:
            cursor.close()

        if first_user is None:
            print("\nNo accounts exist yet, so the menu options were skipped.")
            print("Register an account in the normal menu and run this again.")
            print("\nSELF CHECK FINISHED")
            return 0

        session = Session()
        session.login(first_user[0], first_user[1])
        print(f"\nTesting the options for user '{session.username}':")

        checks = (
            ("Get Recommendations", lambda: get_recommendations(connection,
                                                               session)),
            ("My Profile", lambda: show_profile(connection, session)),
        )
        for name, action in checks:
            print(f"\n--- {name} ---")
            try:
                action()
            except Exception as error:
                print(f"[FAILED] {type(error).__name__}: {error}")
                return 1
            print(f"--- {name}: OK ---")

        print("\nSELF CHECK FINISHED - everything worked")
        return 0
    finally:
        connection.close()


def main():
    """Start the program."""
    use_line_buffering()
    print("Connecting to the MySQL database...")
    try:
        connection = connect_database()
    except mysql.connector.Error as error:
        report_database_error(error)
        print("Check that MySQL is running and that the settings at the top "
              "of main.py match your installation.")
        return

    session = Session()
    try:
        while True:
            if not login_menu(connection, session):
                break
            if main_menu(connection, session) == "exit":
                break
    finally:
        connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        raise SystemExit(run_self_check())
    main()

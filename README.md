# Book Recommendation System

A menu-driven, console-based book recommendation system written in Python and
backed by MySQL, built as a **Class 12 CBSE Computer Science (083) practical
project**.

Users register, log in, browse and search a catalogue of books, rate what they
read, keep a reading list, and receive recommendations based on the genres they
rate highly.

---

## Features

| # | Feature | Where |
|---|---|---|
| 1 | Register a new account (password confirmation, length checks) | `main.py → register_user()` |
| 2 | Log in / log out without restarting the program | `login_user()`, `main_menu()` |
| 3 | Browse the whole catalogue, 15 books per page | `browse_books()` |
| 4 | Filter books by genre (picked from a list, no typing) | `choose_genre()` |
| 5 | View full details of one book (description + average rating) | `show_book_details()` |
| 6 | Search by title, author or genre (partial, case-insensitive) | `search_books()` |
| 7 | Rate a book from 1 to 5 | `rate_book()` |
| 8 | Change an existing rating | `rate_book()` |
| 9 | Add / view / remove books on a personal reading list | `reading_list_menu()` |
| 10 | Get recommendations from your favourite genres | `get_recommendations()` |
| 11 | Profile page: ratings count, average, genre averages | `show_profile()` |
| 12 | Friendly database error messages instead of tracebacks | `report_database_error()` |

**Not implemented (deliberately out of scope):** admin panel for adding or
deleting books, book reviews, exporting the reading list, and a web interface.
See [Limitations](#limitations) and [Future scope](#future-scope).

---

## How it works

1. The program connects to MySQL and shows the **register / login menu**.
2. After a successful login the **main menu** appears.
3. Browsing, searching and book details only *read* from the database.
4. Rating a book and editing the reading list *write* to the database and are
   committed immediately.
5. Recommendations are calculated from the ratings the user has stored.

```
START
  |
  v
Connect to MySQL --> failed? --> friendly error --> END
  |
  v
+---------------------+
| Register / Login    |<---------------------+
+---------------------+                      |
  | login ok            | exit               | log out
  v                     |                    |
+---------------------+ |                    |
| Main menu (8 items) | |                    |
+---------------------+ |                    |
  |                     |                    |
  +-- 1 Browse ---------+                    |
  +-- 2 Search ---------+                    |
  +-- 3 Rate / update --+                    |
  +-- 4 Reading list ---+                    |
  +-- 5 Recommend ------+                    |
  +-- 6 Profile --------+                    |
  +-- 7 Log out --------+--------------------+
  +-- 8 Exit -----------+--> close connection --> END
```

---

## Recommendation algorithm

The system uses **rule-based (content-based) filtering** — it does not need
other users' data to work.

1. For the logged-in user, SQL works out the **average rating per genre**:

   ```sql
   SELECT b.genre, AVG(r.rating), COUNT(*)
     FROM ratings r
     JOIN books b ON b.book_id = r.book_id
    WHERE r.user_id = %s
    GROUP BY b.genre
   HAVING AVG(r.rating) >= %s      -- 3.0, see PREFERRED_GENRE_THRESHOLD
    ORDER BY AVG(r.rating) DESC;
   ```

2. Every genre whose average is **3.0 or more** becomes a *preferred genre*.
3. Books in those genres are collected, **excluding** books the user has
   already rated and books already on the reading list.
4. Candidates are ranked by:
   * preferred genre (highest average first),
   * then number of ratings the book has received from everyone,
   * then its average rating,
   * then title.
5. The **top 10** are displayed (`RECOMMENDATION_LIMIT`).

### Worked example (real output)

The user rated *Cosmos* (Science) **5** and *The Da Vinci Code* (Mystery) **4**:

```
Your favourite genres: Science (5.0/5), Mystery (4.0/5)
Top 10 of 15 matching book(s), best genre first:
ID    Title                         Author                Genre
--------------------------------------------------------------------------
2     A Brief History of Time       Stephen Hawking       Science
109   A Briefer History of Time     Stephen Hawking       Science
7     The Selfish Gene              Richard Dawkins       Science
11    The Time Machine              H.G. Wells            Science
78    A Study in Scarlet            Arthur Conan Doyle    Mystery
52    And Then There Were None      Agatha Christie       Mystery
6     Angels & Demons               Dan Brown             Mystery
63    Inferno                       Dan Brown             Mystery
9     Murder on the Orient Express  Agatha Christie       Mystery
64    Origin                        Dan Brown             Mystery
```

Science (average 5.0) is filled first, then Mystery (average 4.0). *Cosmos* and
*The Da Vinci Code* are missing because the user has already rated them.

Two settings can be changed at the top of `main.py`:

```python
PREFERRED_GENRE_THRESHOLD = 3.0   # how high a genre average must be
RECOMMENDATION_LIMIT = 10         # how many suggestions to show
```

---

## Technologies used

| Technology | Purpose |
|---|---|
| Python 3 | Core language (functions, classes, loops, exception handling) |
| MySQL 8 | Relational database |
| `mysql-connector-python` | Python ↔ MySQL connectivity |
| `hashlib` / `hmac` / `secrets` | Salted PBKDF2 password hashing |

---

## Project structure

```text
Book-Recommendation-System/
├── main.py                 # The whole application
├── database.sql            # Creates the database + 4 tables (structure only)
├── sample_data.sql         # Adds 116 sample books (safe to re-run)
├── upgrade_database.sql    # One-time upgrade for old databases (optional)
├── requirements.txt        # Python dependency
└── README.md               # This file
```

---

## Database schema

Database: `book_recommendation_db` (utf8mb4 / utf8mb4_unicode_ci).
All tables use the InnoDB engine so that foreign keys are enforced.

```
users (1) ──< ratings >── (1) books
users (1) ──< reading_lists >── (1) books
```

### `users`

| Column | Type | Notes |
|---|---|---|
| user_id | INT, PK, AUTO_INCREMENT | |
| username | VARCHAR(50), NOT NULL, UNIQUE | 3–50 characters |
| password_hash | VARCHAR(255), NOT NULL | `pbkdf2_sha256$100000$<salt>$<digest>` |
| created_at | TIMESTAMP | auto |

### `books`

| Column | Type | Notes |
|---|---|---|
| book_id | INT, PK, AUTO_INCREMENT | |
| title | VARCHAR(255), NOT NULL | |
| author | VARCHAR(255), NOT NULL | |
| genre | VARCHAR(100), NOT NULL | one of 13 genres (see below) |
| book_description | TEXT | shown in "View full details" |
| created_at | TIMESTAMP | auto |
| | UNIQUE (title, author) | prevents duplicate books |

### `ratings`

| Column | Type | Notes |
|---|---|---|
| rating_id | INT, PK, AUTO_INCREMENT | |
| user_id | INT, NOT NULL, FK → users | `ON DELETE CASCADE` |
| book_id | INT, NOT NULL, FK → books | `ON DELETE CASCADE` |
| rating | TINYINT, NOT NULL | `CHECK (rating BETWEEN 1 AND 5)` |
| created_at | TIMESTAMP | auto |
| | UNIQUE (user_id, book_id) | **one rating per user per book** |

### `reading_lists`

| Column | Type | Notes |
|---|---|---|
| list_id | INT, PK, AUTO_INCREMENT | |
| user_id | INT, NOT NULL, FK → users | `ON DELETE CASCADE` |
| book_id | INT, NOT NULL, FK → books | `ON DELETE CASCADE` |
| created_at | TIMESTAMP | auto |
| | UNIQUE (user_id, book_id) | a book appears once per user |

### Genres in the sample data

`Fiction`, `Science`, `Science Fiction`, `Fantasy`, `Mystery`, `Thriller`,
`Classics`, `Dystopian`, `Romance`, `History`, `Biography`, `Self Help`,
`Personal Finance` — every genre has **at least three books**, so a
recommendation can always be produced. `Science` holds popular-science
non-fiction; `Science Fiction` holds novels.

---

## Setup (Windows)

### 1. Prerequisites

* **Python 3.8+** — check with `python --version`
* **MySQL Server 8.0+** — check with `mysql --version`
* MySQL Workbench (optional, for running the `.sql` files)

### 2. Create the database

In MySQL Workbench, open and run `database.sql`, then open and run
`sample_data.sql`.

From a terminal instead:

```bash
mysql -u root -p < database.sql
mysql -u root -p < sample_data.sql
```

> **PowerShell does not support `<`.** Use:
>
> ```powershell
> Get-Content database.sql | mysql -u root -p
> Get-Content sample_data.sql | mysql -u root -p
> ```

`database.sql` only creates tables that do not exist yet, and
`sample_data.sql` skips books that already exist, so **both files can be run
again safely** without creating duplicates.

### 3. Check that it worked

```sql
USE book_recommendation_db;
SHOW TABLES;
SELECT COUNT(*) FROM books;   -- should return 116
```

### 4. Configure the connection

Open `main.py` and edit the four values near the top:

```python
HOST = "localhost"
PORT = 3306
USER = "root"
PASSWORD = "your_password"     # <-- your MySQL password
DATABASE = "book_recommendation_db"
```

Or leave the file untouched and set environment variables before running:

```powershell
$env:BOOK_DB_PASSWORD = "your_password"
python main.py
```

### 5. Install the Python dependency

```bash
pip install -r requirements.txt
```

### 6. Run

```bash
python main.py
```

If you want to check the connection and the three interactive options without
typing anything, run the built-in self check:

```bash
python main.py --check
```

It prints the MySQL version and the row counts, then runs *Get
Recommendations* and *My Profile* for the first account in the database.

### Already had an older version of this project?

Run **`upgrade_database.sql`** once (it adds the new constraints, removes
duplicate ratings and fixes a few book titles), then, if you want the new
books, run `sample_data.sql` again. Your accounts and ratings are kept, and
old plain-text passwords are converted to hashes automatically the next time
each user logs in.

---

## Example session (abridged, real output)

```text
Connecting to the MySQL database...

============================================
   BOOK RECOMMENDATION SYSTEM
============================================
1. Register
2. Login
3. Exit
Enter your choice (1-3): 2

--- Log in ---
Username: carol
Password:
Login successful! Welcome, carol.

============================================
  MAIN MENU - carol
============================================
1. Browse Books
2. Search Books
3. Rate a Book
4. My Reading List
5. Get Recommendations
6. My Profile
7. Log Out
8. Exit
Enter your choice (1-8): 1

1. Show all books
2. Filter by genre
3. View full details of a book
Enter your choice (1-3): 1

Showing books 1-15 of 116
ID    Title                         Author                Genre
--------------------------------------------------------------------------
1     The Alchemist                 Paulo Coelho          Fiction
2     A Brief History of Time       Stephen Hawking       Science
3     The Da Vinci Code             Dan Brown             Mystery
4     The God of Small Things       Arundhati Roy         Fiction
5     Cosmos                        Carl Sagan            Science
6     Angels & Demons               Dan Brown             Mystery
7     The Selfish Gene              Richard Dawkins       Science
8     Pride and Prejudice           Jane Austen           Fiction
9     Murder on the Orient Express  Agatha Christie       Mystery
10    To Kill a Mockingbird         Harper Lee            Fiction
11    The Time Machine              H.G. Wells            Science
12    The Magician's Nephew         C.S. Lewis            Fiction
13    The Hobbit                    J.R.R. Tolkien        Fantasy
14    The Lord of the Rings         J.R.R. Tolkien        Fantasy
15    Harry Potter and the Phil...  J.K. Rowling          Fantasy
--------------------------------------------------------------------------
Press Enter for the next page, or 'q' to stop: q
Stopped listing.
```

Viewing one book (shows the average of *all* readers plus your own rating):

```text
============================================================
Title       : Cosmos
Author      : Carl Sagan
Genre       : Science
Rating      : 3.5/5 from 2 reader(s)
Description : A journey through space and time, exploring the wonders of the universe.
Your rating : 5/5
============================================================
```

The profile page:

```text
========================================================
  PROFILE - carol
========================================================
  Member since     : 2026-10-30
  Books rated      : 2
  Average rating   : 4.5/5
  Reading list     : 0 book(s)
  Genre averages   :
      Science           5.0/5  (1 book(s))
      Mystery           4.0/5  (1 book(s))

  Books you have rated:
      Cosmos                                  5/5
      The Da Vinci Code                       4/5
========================================================
```

---

## Password security

Passwords are **never stored in plain text**:

* Each password is hashed with **PBKDF2-HMAC-SHA256**, 100,000 iterations and
  a fresh random 16-byte salt (`secrets.token_hex(16)`).
* The stored value has the form
  `pbkdf2_sha256$100000$<salt>$<digest>`, which fits in `VARCHAR(255)`.
* Comparison uses `hmac.compare_digest()` (constant-time).
* Passwords are typed with `getpass`, so they are not echoed.
* A row created by an older version (plain text) still logs in, and is
  upgraded to a hash the first time that user logs in.

The database can therefore be inspected without exposing anyone's password.

---

## Input validation and error handling

* Menu choices: only integers inside the stated range are accepted.
* Username: 3–50 characters, must not already exist.
* Password: 6–64 characters, entered twice at registration.
* Book ID prompts use the **real** highest `book_id`, not a fixed number.
* `Ctrl+C` / `Ctrl+D` closes the program cleanly instead of printing a
  traceback.
* Every database action is wrapped; a lost connection, missing table or
  duplicate value produces a readable message and the program keeps running.
* **All SQL uses `%s` placeholders** (parameterised queries), so user input can
  never be executed as SQL. The one f-string in a query only inserts `%s`
  markers, never user text.

---

## Troubleshooting

| Message | Fix |
|---|---|
| `Cannot reach the MySQL server` | Start MySQL (`services.msc` → MySQL80) and check `HOST`/`PORT`. |
| `MySQL refused the login` | Wrong `USER`/`PASSWORD` in `main.py`. |
| `The database does not exist` | Run `database.sql`. |
| `A table is missing` | Run `database.sql`. |
| `ModuleNotFoundError: mysql.connector` | `pip install -r requirements.txt` |
| `Warning: Password input may be echoed` | You are running inside IDLE, which has no real console. Run `python main.py` from PowerShell or CMD instead. |
| A menu option seems to do nothing | Run `python main.py --check`. If it passes, start the program from PowerShell or CMD rather than an IDE run window. Every menu choice now prints a `--- Option name ---` header, so a missing header means the keystroke never reached the program. |
| Duplicate-entry error in `upgrade_database.sql` | Delete duplicate rows first (the message explains how). |
| Port 3306 already in use | Set `PORT` (or `BOOK_DB_PORT`) to another port, e.g. 3307. |

---

## CBSE syllabus coverage

Useful for the viva — every row points at real code:

| Class 12 topic | Where it is used |
|---|---|
| Functions, arguments, return values | Every feature is a function |
| Scope (local / global) | `Session` object instead of globals |
| `try` / `except` / `finally` | `report_database_error`, `main()` |
| String handling | `fit_cell`, `escape_like` |
| Lists, tuples, dictionaries | `preferred_genres`, `genre_rank`, `queries` dict |
| Class and object | `Session` class |
| `while` loops, `if`/`elif` | All menus |
| Python–MySQL connectivity | `mysql.connector.connect()`, `cursor`, `commit` |
| Parameterised queries | `execute(sql, (value,))` everywhere |
| `SELECT`, `INSERT`, `UPDATE`, `DELETE` | Browse / register / change rating / remove from list |
| `JOIN` | Reading list, genre averages |
| Sub-queries | Recommendations ("not already rated") |
| Aggregate functions (`AVG`, `COUNT`, `MAX`, `ROUND`, `COALESCE`) | Statistics, recommendations |
| `GROUP BY` … `HAVING` | Finding preferred genres |
| Primary key, foreign key, `UNIQUE`, `CHECK` | `database.sql` |
| `ON DELETE CASCADE`, referential integrity | `database.sql` |
| Normalisation | Four tables, no repeated data |

---

## Project report checklist

For the practical file itself (the code alone is not the submission):

- [ ] Cover page, certificate, acknowledgement, index
- [ ] Problem statement and objective
- [ ] Scope / limitations
- [ ] ER diagram — copy the relationships from [Database schema](#database-schema)
- [ ] Table structures — run `DESCRIBE users;` etc. and paste the screenshots
- [ ] Flowchart — redraw the diagram in [How it works](#how-it-works)
- [ ] Source code listing
- [ ] Output screenshots for **each** menu option
- [ ] Testing table (valid input, invalid input, boundary values)
- [ ] Conclusion and future scope
- [ ] Bibliography

---

## Limitations

* **Genre-based, not collaborative.** Recommendations use only the logged-in
  user's ratings; other users' ratings affect the *order* inside a genre but
  not which genres are suggested. With a single user the result is a filtered
  genre list.
* **Coarse genres.** 13 genres cannot describe a mixed or unusual taste; a
  book in `Science Fiction` is never recommended to a `Science` reader.
* **The catalogue is read-only inside the app.** Books are added only through
  `sample_data.sql`.
* **Single user at a time.** No concurrent sessions, no roles or admin account.
* **Console interface.** No colours, no mouse, no web page.
* **Averages are unweighted.** One 5-star rating is enough to make a genre
  "preferred"; there is no minimum number of ratings.

---

## Future scope

* Collaborative filtering ("readers who liked this also liked…").
* Admin login to add, edit and delete books from inside the program.
* Reviews and comments, with a word limit.
* Export the reading list to a `.csv` or `.txt` file (file handling).
* Weight recent ratings more heavily than old ones.
* Web front end with Flask, reusing this database unchanged.
* Recommendations by author and by reading-list similarity.

---

## License

Written for educational use as part of the CBSE Class 12 curriculum.
No license is applied.

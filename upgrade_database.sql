-- =====================================================================
-- Book Recommendation System - Upgrade an EXISTING database
-- =====================================================================
-- Run this file ONCE only if you already created the database with an
-- older version of this project. A fresh installation does NOT need it:
-- database.sql already contains all of these changes.
--
-- Run it BEFORE re-running sample_data.sql, and run the whole file top to
-- bottom in MySQL Workbench or with:
--     Get-Content upgrade_database.sql | mysql -u root -p
--
-- Your accounts and ratings are kept. Old plain-text passwords are
-- upgraded to secure hashes automatically the next time each user logs in.
-- =====================================================================

USE book_recommendation_db;

-- Use the same character set as a fresh installation
ALTER DATABASE book_recommendation_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 1. Make sure no book has an empty genre (the column becomes NOT NULL)
-- ---------------------------------------------------------------------
UPDATE books
   SET genre = 'Unknown'
 WHERE genre IS NULL OR genre = '';

-- ---------------------------------------------------------------------
-- 2. Remove duplicate ratings, keeping the oldest one for each pair
-- ---------------------------------------------------------------------
DELETE r1
  FROM ratings r1
  JOIN ratings r2
    ON r1.user_id = r2.user_id
   AND r1.book_id = r2.book_id
   AND r1.rating_id > r2.rating_id;

-- ---------------------------------------------------------------------
-- 3. A user may rate a book only once
-- ---------------------------------------------------------------------
ALTER TABLE ratings
    ADD CONSTRAINT unique_user_book_rating UNIQUE (user_id, book_id);

-- Use a small integer for a 1-5 rating
ALTER TABLE ratings MODIFY rating TINYINT NOT NULL;

-- ---------------------------------------------------------------------
-- 4. One row per book, so sample_data.sql can be re-run safely
-- ---------------------------------------------------------------------
-- If this statement fails with "Duplicate entry", your books table already
-- contains the same book twice. Find the duplicates with:
--     SELECT title, author, COUNT(*) FROM books
--      GROUP BY title, author HAVING COUNT(*) > 1;
-- delete the extra copies, and then run this statement again.
ALTER TABLE books
    ADD CONSTRAINT unique_book UNIQUE (title, author);

ALTER TABLE books MODIFY genre VARCHAR(100) NOT NULL;

-- ---------------------------------------------------------------------
-- 5. Data corrections in the sample catalogue
-- ---------------------------------------------------------------------
UPDATE books
   SET title = 'Great Expectations'
 WHERE title = 'The Great Expectations';

UPDATE books
   SET title = 'The Magician''s Nephew'
 WHERE title = 'Magician''s Nephew';

UPDATE books
   SET title = 'The Lion, the Witch and the Wardrobe',
       book_description = 'Four children step through a wardrobe into the magical land of Narnia.'
 WHERE title = 'The Chronicles of Narnia';

UPDATE books
   SET book_description = 'A young Coriolanus Snow mentors Lucy Gray Baird, a tribute from District 12.'
 WHERE title = 'The Ballad of Songbirds and Snakes';

-- ---------------------------------------------------------------------
-- 6. Remove the duplicate series entry
--    (The Lightning Thief already covers the same book.)
-- ---------------------------------------------------------------------
DELETE r
  FROM ratings r
  JOIN books b ON b.book_id = r.book_id
 WHERE b.title = 'Percy Jackson and the Olympians';

DELETE rl
  FROM reading_lists rl
  JOIN books b ON b.book_id = rl.book_id
 WHERE b.title = 'Percy Jackson and the Olympians';

DELETE FROM books WHERE title = 'Percy Jackson and the Olympians';

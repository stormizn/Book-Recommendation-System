-- =====================================================================
-- Book Recommendation System - Database Schema
-- =====================================================================
-- Creates the database and all four tables.
--
-- Safe to re-run: CREATE TABLE IF NOT EXISTS skips tables that already
-- exist, so re-running this file never deletes or changes your data.
--
-- Sample books are in sample_data.sql (safe to re-run as well).
-- If you created the database with an OLDER version of this project, run
-- upgrade_database.sql once instead of re-running this file.
--
-- Relationships (for the ER diagram in the project report):
--   users (1) ----< ratings (many)
--   users (1) ----< reading_lists (many)
--   books (1) ----< ratings (many)
--   books (1) ----< reading_lists (many)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS book_recommendation_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE book_recommendation_db;

-- ---------------------------------------------------------------------
-- 1. users : one row per registered account
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    -- Stores a salted PBKDF2 hash (never the plain password).
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 2. books : the catalogue
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    book_id          INT AUTO_INCREMENT PRIMARY KEY,
    title            VARCHAR(255) NOT NULL,
    author           VARCHAR(255) NOT NULL,
    genre            VARCHAR(100) NOT NULL,
    book_description TEXT,
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- One row per book, so re-running sample_data.sql cannot add duplicates.
    UNIQUE KEY unique_book (title, author)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 3. ratings : one score (1-5) per user per book
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ratings (
    rating_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT     NOT NULL,
    book_id    INT     NOT NULL,
    rating     TINYINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rating_range CHECK (rating BETWEEN 1 AND 5),
    -- A user may rate a book only once (also enforced by the program).
    CONSTRAINT unique_user_book_rating UNIQUE (user_id, book_id),
    CONSTRAINT fk_rating_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_rating_book FOREIGN KEY (book_id)
        REFERENCES books (book_id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 4. reading_lists : books a user wants to read
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reading_lists (
    list_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    book_id    INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_book_list UNIQUE (user_id, book_id),
    CONSTRAINT fk_list_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_list_book FOREIGN KEY (book_id)
        REFERENCES books (book_id) ON DELETE CASCADE
) ENGINE = InnoDB;

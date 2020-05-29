CREATE EXTENSION pgcrypto;

CREATE TABLE users_bookiview (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_bookiview,
    book_id INTEGER REFERENCES books,
    review TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating > 0 OR rating < 6)
);
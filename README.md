# Project 1

Bookiview is a website where you can search by ISBN number, by the title of the book, by the author of it and even so which any combination of them. Also here you can read reviews of your favorite books, write your own and rate your books.

- `index.html`: Main page 
- `create-account.html`: Here you can create an account on Bookiview, including your user, email and password.
- `login.html`: It contains a form to log in to Bookiview.
- `search.html`: Here you can search your books fill in any criteria in the form.
- `results.html`: This displays a list of books which match with the search criteria.
- `book.html`: Info and reviews of a book selected in the results view.

Also Bookiview includes an API where you can obtain some information about your book writing `/api/<isbn>`

```
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
```
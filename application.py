import os
import requests

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
app.secret_key = 'wOuBr38gGcU4tPLLig0-AQ'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	if 'loggeg_in' in session:
		session["logged_in"]=False
	return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		name = request.form.get("name")
		password = request.form.get("password")
		if db.execute("SELECT * FROM users_bookiview WHERE name = :name AND password = crypt(:password, password)", {"name": name, "password": password}).rowcount == 1:
			user = db.execute("SELECT id FROM users_bookiview WHERE name = :name", {"name": name}).fetchone()
			session["name"] = name
			session["id"] = user.id
			session["logged_in"] = True
			session["message"] = 1
			db.commit()
			return redirect(url_for('search'))			
		else:
			session["message"] = 3
			return render_template("login.html", message=3)
	else:
		return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
	if request.method == "POST":
		name = request.form.get("name")
		email = request.form.get("email").lower()
		password = request.form.get("password")
		if db.execute("SELECT * FROM users_bookiview WHERE name = :name OR email = :email", {"name": name, "email": email}).rowcount != 0:
	 		db.commit()
	 		message = 1
	 		return render_template("create-account.html", message=message)
		db.execute("INSERT INTO users_bookiview (name, email, password) VALUES (:name, :email, crypt(:password, gen_salt('bf')))", {"name": name, "email": email, "password": password})
		db.commit()
		session["name"] = name
		message = 0
		return redirect(url_for('index'))
	else:
		return render_template("create-account.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
	if request.method == "POST":
		isbn = request.form.get("isbnBook")
		title = request.form.get("titleBook").lower()
		author = request.form.get("authorBook").lower()
		if (isbn == "") & (title == "") & (author == ""):
			message = 2
			return redirect(url_for('search'))
		books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND LOWER(title) LIKE :title AND LOWER(author) LIKE :author", {"isbn": "%"+isbn+"%", "title": "%"+title+"%", "author": "%"+author+"%"}).fetchall()
		db.commit()
		if len(books) == 0:
			session["message"] = 3
			return render_template("search.html")
		session["message"] = 0
		return render_template("results.html", books=books)
	else:
		return render_template("search.html")

@app.route("/book/<isbn>", methods=['GET', 'POST'])
def book(isbn):
	if request.method == "POST":
		rating = request.form.get("ratingRadios")
		review = request.form.get("reviewTextarea")
		if (rating == None) | (review == ""):
			return redirect(url_for('book',isbn=isbn))		
		book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
		user = db.execute("SELECT id FROM users_bookiview WHERE name = :name", {"name": session["name"]}).fetchone()
		reviews = db.execute("SELECT * FROM reviews JOIN users_bookiview ON users_bookiview.id = reviews.user_id WHERE reviews.book_id = :book_id", {"book_id": book.id}).fetchall()
		db.execute("INSERT INTO reviews (user_id, book_id, review, rating) VALUES (:user_id, :book_id, :review, :rating)", {"user_id": user.id, "book_id": book.id, "review": review, "rating": rating})
		db.commit()
		return render_template("book.html", book=book, reviews=reviews)
	else:
		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "gCyeIcetWtMLisDbeUW4g", "isbns": "9781632168146"})
		data = res.json()
		work_ratings_count = data['books'][0]["work_ratings_count"]
		rating_count = data['books'][0]["average_rating"]	
		book = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": isbn}).fetchone()
		reviews = db.execute("SELECT * FROM reviews JOIN users_bookiview ON users_bookiview.id = reviews.user_id WHERE reviews.book_id = :book_id", {"book_id": book.id}).fetchall()
		db.commit()
		previous_message = False
		for review in reviews:
			if review.user_id == session["id"]:
				previous_message = True
		return render_template("book.html", book=book, reviews=reviews, work_ratings_count=work_ratings_count, rating_count=rating_count, previous_message=previous_message)

@app.route("/logout")
def logout():
	session.pop("logged_in", None)
	# session.clear()
	return redirect(url_for('index'))

@app.route("/api/<isbn>")
def book_api(isbn):
    """Return details about a single flight."""

    # Make sure flight exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 404
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
    rating = 0;
    for review in reviews:
    	rating += review.rating
    if len(reviews) != 0:
    	rating = round(rating / len(reviews),1)
    return jsonify({
    	"title": book.title,
		"author": book.author,
		"year": book.year,
		"isbn": isbn,
		"review_count": len(reviews),
		"average_score": rating
  	})
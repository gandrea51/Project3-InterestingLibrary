from flask import Blueprint, flash, jsonify, render_template, redirect, send_file, url_for, request
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from .models import User, Book, Loan, Message, Event
from .utils import check_email, check_password
from . import db
from datetime import date, datetime, timedelta
import math

main = Blueprint('main', __name__)

@main.context_processor
def inject():
    if current_user.is_authenticated:
        return {'current_user': current_user}
    return {'current_user': None}

# Sezione Errori
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='The page you are looking for does not exist.'), 404
@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message='Internal server error. Please try again later.'), 500
@main.app_errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message='Access denied. You do not have the necessary permissions to access this page.'), 403

@main.route('/', methods=["GET"])
def introduction():
    books = Book.query.order_by(Book.bview.desc(), Book.title).limit(3).all()
    return render_template('welcome.html', books=books)

@main.route('/about', methods=["GET"])
def about():
    return render_template('about.html')

@main.route('/contact', methods=["GET"])
def contact():
    return render_template('contact.html')

@main.route('/inscribe', methods=["POST"])
@login_required
def inscribe():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    date_write = date.today()
    msg = Message(name=name, email=email, message=message, date_write=date_write, readit="No")
    db.session.add(msg)
    db.session.commit()
    return redirect(url_for('main.introduction'))

@main.route('/message', methods=["GET"])
@login_required
def message():
    messages = Message.query.filter(Message.readit == "No").order_by(Message.date_write.desc()).all()
    return render_template('message.html', messages=messages)

@main.route('/read/<int:id>', methods=["GET"])
@login_required
def read(id):
    message = db.session.get(Message, id)    
    if not message:
        return render_template('error.html', error_message="Il message richiesto non è stato trovato.")
    
    message.readit = "Si"
    db.session.commit()        
    return redirect(url_for('main.message'))

@main.route('/explore', methods=["GET"])
def explore():
    return render_template('explore.html')

@main.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    name = request.form.get('name')
    genre = request.form.get('genre')
    email = request.form.get('email')
    is_valid, error_message = check_email(email)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('main.signup'))
    
    password = request.form.get('password')
    is_valid, error_message = check_password(password)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('main.signup'))
    password = generate_password_hash(password)    
    role = request.form.get('role')

    user = User(name=name, genre=genre, email=email, password=password, role=role)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main.introduction'))

@main.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('main.introduction'))

@main.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('main.introduction'))

@main.route('/password', methods=["GET" , "POST"])
def signpass():
    if request.method == 'GET':
        return render_template('signpass.html')
    
    old = request.form.get('old')
    new = request.form.get('new')
    is_valid, error_message = check_password(new)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('main.signpass'))
    
    if not check_password_hash(current_user.password, old):
        return redirect(url_for('main.signpass'))
    
    new = generate_password_hash(new)
    current_user.password = new
    db.session.commit()
    return redirect(url_for('main.explore'))

@main.route('/email', methods=["GET", "POST"])
def signemail():
    if request.method == 'GET':
        return render_template('signemail.html')
    
    old = request.form.get('old')
    new = request.form.get('new')
    is_valid, error_message = check_email(new)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('main.signemail'))

    if not current_user.email == old:
        return redirect(url_for('main.signemail'))
    
    current_user.email = new
    db.session.commit()
    return redirect(url_for('main.explore'))

@main.route('/book', methods=["GET"])
@login_required
def book():
    genres = Book.query.with_entities(Book.genre, func.count(Book.genre)).group_by(Book.genre).order_by(Book.genre).all()
    books = {}
    for genre in genres:
        book = Book.query.filter_by(genre = genre[0]).order_by(Book.id).limit(5).all()
        books[genre[0]] = book
    realise = Book.query.filter_by(author="Oscar Wilde").order_by(Book.title).first()
    mrealise = ""
    if realise.copy >= 3:
        mrealise = "Ci sono ancora molte copie disponibili per questo libro!"
    elif realise.copy == 2:
        mrealise = "Attenzione! Solo 2 copie restanti! Affrettati per prenderlo!"
    elif realise.copy == 1:
        mrealise = "Ultima copia disponibile. Prendila in prestito adesso!"
    else:
        mrealise = "Al momento non vi sono copie disponibili. Torna tra qualche giorno per ricontrollare."
    classic = Book.query.filter_by(author="Virginia Woolf").order_by(Book.title).first()
    mclassic = ""
    if classic.copy >= 3:
        mclassic = "Ci sono ancora molte copie disponibili per questo libro!"
    elif classic.copy == 2:
        mclassic = "Attenzione! Solo 2 copie restanti! Affrettati per prenderlo!"
    elif classic.copy == 1:
        mclassic = "Ultima copia disponibile. Prendila in prestito adesso!"
    else:
        mclassic = "Al momento non vi sono copie disponibili. Torna tra qualche giorno per ricontrollare."
    new = Book.query.filter_by(author="Thomas Eliot").order_by(Book.title).first()
    mnew = ""
    if new.copy >= 3:
        mnew = "Ci sono ancora molte copie disponibili per questo libro!"
    elif new.copy == 2:
        mnew = "Attenzione! Solo 2 copie restanti! Affrettati per prenderlo!"
    elif new.copy == 1:
        mnew = "Ultima copia disponibile. Prendila in prestito adesso!"
    else:
        mnew = "Al momento non vi sono copie disponibili. Torna tra qualche giorno per ricontrollare."    
    tbooks = Book.query.count()
    tviews = db.session.query(db.func.sum(Book.bview)).scalar() or 0
    tdowns = db.session.query(db.func.sum(Book.bdownload)).scalar() or 0
    mbooks = Book.query.order_by(Book.bview.desc()).limit(4).all()
    stats = {'tbooks': tbooks, 'tviews': tviews, 'tdowns': tdowns, 'mbooks': mbooks}
    return render_template('book.html', genres=genres, realise=realise, mrealise=mrealise, classic=classic, mclassic=mclassic, new=new, mnew=mnew, stats=stats)

@main.route('/view/<int:book_id>', methods=["POST"])
@login_required
def view(book_id):
    book = Book.query.get_or_404(book_id)
    book.bview = book.bview + 1 if book.bview else 1
    db.session.commit()
    return jsonify({'success': True, 'message': 'Visualizzazioni aggiornate!'})

@main.route('/book/search/title', methods=["POST"])
@login_required
def btitle():
    title = request.form.get('title')
    books = Book.query.filter(Book.title.like(f'%{title}%')).all()    
    messages = {}
    for book in books:
        if book.copy >= 3:
            messages[book.id] = "Ci sono ancora molte copie disponibili per questo libro!"
        elif book.copy == 2:
            messages[book.id] = "Attenzione! Solo 2 copie restanti! Affrettati per prenderlo!"
        elif book.copy == 1:
            messages[book.id] = "Ultima copia disponibile. Prendila in prestito adesso!"
        else:
            messages[book.id] = "Al momento non vi sono copie disponibili. Torna tra qualche giorno per ricontrollare."
    return render_template('bsearch.html', books=books, hidden="Titolo", messages=messages)

@main.route('/book/search/author', methods=["POST"])
@login_required
def bauthor():
    author = request.form.get('author')
    books = Book.query.filter(Book.author.like(f'%{author}%')).all()   
    messages = {}
    for book in books:
        if book.copy >= 3:
            messages[book.id] = "Ci sono ancora molte copie disponibili per questo libro!"
        elif book.copy == 2:
            messages[book.id] = "Attenzione! Solo 2 copie restanti! Affrettati per prenderlo!"
        elif book.copy == 1:
            messages[book.id] = "Ultima copia disponibile. Prendila in prestito adesso!"
        else:
            messages[book.id] = "Al momento non vi sono copie disponibili. Torna tra qualche giorno per ricontrollare."    
    return render_template('bsearch.html', books=books, hidden="Autore", messages=messages)

@main.route('/book/search/genre', methods=["POST"])
@login_required
def bgenre():
    genre = request.form.get('genre')
    books = Book.query.filter(Book.genre.like(f'%{genre}%')).all()   
    messages = {}
    for book in books:
        if book.copy >= 3:
            messages[book.id] = "Ci sono ancora molte copie disponibili per questo libro!"
        elif book.copy == 2:
            messages[book.id] = "Attenzione! Solo 2 copie restanti! Affrettati per prenderlo!"
        elif book.copy == 1:
            messages[book.id] = "Ultima copia disponibile. Prendila in prestito adesso!"
        else:
            messages[book.id] = "Al momento non vi sono copie disponibili. Torna tra qualche giorno per ricontrollare."
    return render_template('bsearch.html', books=books, hidden="Genere", messages=messages)

@main.route('/book/genre', methods=["POST"])
def bview():
    genre = request.form.get('genre')
    books = Book.query.filter(Book.genre.like(f'%{genre}%')).order_by(Book.title).all()
    messages = {}
    for book in books:
        if book.copy >= 3:
            messages[book.id] = "Ci sono ancora molte copie disponibili per questo libro!"
        elif book.copy == 2:
            messages[book.id] = "Attenzione! Solo 2 copie restanti! Affrettati per prenderlo!"
        elif book.copy == 1:
            messages[book.id] = "Ultima copia disponibile. Prendila in prestito adesso!"
        else:
            messages[book.id] = "Al momento non vi sono copie disponibili. Torna tra qualche giorno per ricontrollare."
    return render_template('bview.html', books=books, genre=genre, messages=messages)

@main.route('/book/<int:id>/related', methods=["GET"])
def brelated(id):
    book = db.session.get(Book, id)    
    if not book:
        return render_template('error.html', error_message="Il libro richiesto non è stato trovato.")
    
    book.bview += 1
    db.session.commit()
    by_genre = Book.query.filter(Book.genre == book.genre, Book.id != id).limit(5).all()
    by_author = Book.query.filter(Book.author == book.author, Book.id != id).limit(5).all()
    by_publisher = Book.query.filter(Book.publisher == book.publisher, Book.id != id).limit(5).all()
    books = {book.id: book for book in by_genre + by_author + by_publisher}.values()     
    return render_template('brelated.html', book=book, books=books)

@main.route('/book/manager', methods=["GET"])
@login_required
def bmanager():
    books = Book.query.all()
    return render_template('bmanager.html', books=books)

@main.route('/book/create', methods=["GET", "POST"])
@login_required
def bpost():
    if request.method == 'GET':
        return render_template('bpost.html')
    
    book = Book(
        title = request.form['title'],
        year = request.form['year'],
        classification = request.form['classification'],
        position = request.form['position'],
        author = request.form['author'],
        genre = request.form['genre'],
        necklace = request.form['necklace'],
        publisher = request.form['publisher'],
        note = request.form['note'],
        copy = request.form['copy'],
        bview = 0,
        bdownload = 0,
        bmonth = "No",
        magazine = "No",
        available = "Si"
    )

    db.session.add(book)
    db.session.commit()        
    return redirect(url_for('main.bmanager'))   

@main.route('/book/<int:id>/edit', methods=["GET", "POST"])
@login_required
def bput(id):
    book = Book.query.get(id)
    if not book:
        return render_template('error.html', error_message="Il libro richiesto non è stato trovato.")    
    
    if request.method == 'GET':
        return render_template('bput.html', book=book)
    
    book.title = request.form['title']
    book.year = request.form['year']
    book.classification = request.form['classification']
    book.position = request.form['position']
    book.author = request.form['author']
    book.genre = request.form['genre']
    book.necklace = request.form['necklace']
    book.publisher = request.form['publisher']
    book.note = request.form['note']
    book.copy = request.form['copy']

    db.session.commit()
    return redirect(url_for('main.bmanager'))
    
@main.route('/book/<int:id>/drop', methods=["POST"])
@login_required
def bdelete(id):
    book = Book.query.get(id)    
    if not book:
        return render_template('error.html', error_message="Il libro richiesto non è stato trovato.")
    
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('main.bmanager'))

@main.route('/user/<int:id>', methods=["GET"])
@login_required
def profile(id):
    user = db.session.get(User, id)
    if not user:
        return render_template('error.html', error_message="L'utente richiesto non è stato trovato.")
    user.lcount = Loan.query.filter_by(user_id=user.id).count()
        
    mloan = ""
    if not Loan.query.filter_by(user_id=user.id, ended="No").all():
        mloan = "Non hai ancora effettuato prestiti.<br><br>Scopri la nostra selezione di titoli e approfitta delle offerte esclusive per il tuo prossimo progetto!"
    
    loans = Loan.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, mloan=mloan, loans=loans)

@main.route('/user', methods=["GET"])
@login_required
def user():
    users = User.query.all()
    for user in users:
        user.lcount = Loan.query.filter_by(user_id=user.id).count()
    return render_template('user.html', users=users)

@main.route('/user/manager', methods=["GET"])
@login_required
def umanager():
    users = User.query.all()
    return render_template('umanager.html', users=users)
    
@main.route('/user/<int:id>/drop', methods=["POST"])
@login_required
def udelete(id):
    user = User.query.get(id)    
    if not user:
        return render_template('error.html', error_message="L'utente richiesto non è stato trovato.")
    
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.umanager'))

@main.route('/loan', methods=["GET"])
@login_required
def loan():
    return render_template('loan.html')

@main.route('/suggest', methods=["GET"])
def suggest():
    query = request.args.get('query', '')
    suggestions = []
    
    if query:
        # Eseguiamo la ricerca di titoli che contengono la query
        books = Book.query.filter(Book.title.like(f'%{query}%')).all()
        suggestions = [book.title for book in books]
    
    return jsonify(suggestions)

@main.route('/loan/create', methods=["GET", "POST"])
@login_required
def lpost():
    if request.method == 'GET':
        return render_template('lpost.html')
    
    title = request.form.get('title')
    date_start = datetime.strptime(request.form.get('date_start'), '%Y-%m-%d')
    
    book = Book.query.filter(Book.title.like('%' + title + '%')).first()
    if not book:
        return render_template('error.html', error_message="Il libro richiesto non è stato trovato.")
    
    date_end = date_start + timedelta(days = 30 if book.magazine == 'No' else 15)
    
    loan = Loan(date_start=date_start, date_end=date_end, ended='No', returned="No", extended='No', book_id=book.id, user_id=current_user.id)
    db.session.add(loan)
    
    book.copy -= 1
    if book.copy == 0:
        book.available = 'No'
    db.session.commit()        
    
    return redirect(url_for('main.explore'))
 
@main.route('/loan/all', methods=["GET"])
@login_required
def lall():
    loans = Loan.query.all()
    return render_template('lall.html', loans=loans)

@main.route('/loan/due', methods=["GET"])
@login_required
def ldue():
    today = datetime.today()
    limit = today + timedelta(days=7)
    loans = Loan.query.filter(Loan.date_end <= limit, Loan.date_end >= today).all()    
    return render_template('ldue.html', loans=loans)

@main.route('/loan/not-repaid', methods=["GET"])
def lnr():
    loans = Loan.query.filter(Loan.ended == "Si", Loan.returned == "No").all()    
    return render_template('lnr.html', loans=loans)

@main.route('/loan/statistics', methods=["GET"])
def lstat():
    total = Loan.query.count()
    loans = Loan.query.all()
    max = sum([(loan.date_end - loan.date_start).days for loan in loans])
    avg = max / len(loans) if loans else 0    
    overdue = Loan.query.filter(Loan.date_end < datetime.today().date(), Loan.returned == "No").count()
    actual = Loan.query.filter(Loan.date_end >= datetime.today().date()).count()
    return render_template('lstat.html', total=total, avg=avg, overdue=overdue, actual=actual)

@main.route('/loan/<int:id>/extend', methods=["GET"])
@login_required
def extension(id):
    loan = db.session.get(Loan, id)    
    if not loan:
        return render_template('error.html', error_message="Il prestito richiesto non è stato trovato.")
    
    loan.date_end = loan.date_end + timedelta(days=15)
    loan.ended = "No"
    loan.extended = "Si"
    db.session.commit()
    return redirect(url_for('main.profile', id=current_user.id))

@main.route('/loan/<int:id>/term', methods=["GET"])
@login_required
def termination(id):
    loan = db.session.get(Loan, id)    
    if not loan:
        return render_template('error.html', error_message="Il prestito richiesto non è stato trovato.")
    
    loan.ended = "Si"
    loan.date_end = date.today()
    db.session.commit()    
    return redirect(url_for('main.lall'))

@main.route('/loan/<int:id>/back', methods=["GET"])
@login_required
def backup(id):
    loan = db.session.get(Loan, id)    
    if not loan:
        return render_template('error.html', error_message="Il prestito richiesto non è stato trovato.")
    
    loan.date_end = date.today()
    loan.returned = "Si"
    
    book = db.session.get(Book, loan.book_id)
    if not book:
        return render_template('error.html', error_message="Il libro richiesto non è stato trovato.")
    book.copy += 1
    if book.copy > 0:
        book.available = "Si"
    db.session.commit()    
    
    return redirect(url_for('main.lall'))

@main.route('/event', methods=["GET"])
@login_required
def event():
    events = Event.query.all()
    return render_template('event.html', events=events)

@main.route('/event/manager', methods=["GET"])
@login_required
def emanager():
    events = Event.query.all()
    return render_template('emanager.html', events=events)

@main.route('/event/create', methods=["GET", "POST"])
@login_required
def epost():
    if request.method == 'GET':
        return render_template('epost.html')
    
    event = Event(
        title = request.form['title'],
        description = request.form['description'],
        place = request.form['place'],
        date_start = request.form['date_start'],
        date_end = request.form['date_end'],
    )

    db.session.add(event)
    db.session.commit()        
    return redirect(url_for('main.emanager'))   

@main.route('/event/<int:id>/edit', methods=["GET", "POST"])
@login_required
def eput(id):
    event = Event.query.get(id)
    if not event:
        return render_template('error.html', error_message="L'evento richiesto non è stato trovato.")    
    
    if request.method == 'GET':
        return render_template('eput.html', event=event)
    
    event.title = request.form['title']
    event.description = request.form['description']
    event.place = request.form['place']
    event.date_start = request.form['date_start']
    event.date_end = request.form['date_end']
    db.session.commit()
    return redirect(url_for('main.emanager'))
    
@main.route('/event/<int:id>/drop', methods=["POST"])
@login_required
def edelete(id):
    event = Event.query.get(id)
    if not event:
        return render_template('error.html', error_message="L'evento richiesto non è stato trovato.") 
    
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('main.emanager'))

from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3

DB_PATH = 'database/library.db'

app = Flask(__name__)
import os
app.secret_key = os.urandom(24)


# -------------------- TẠO BẢNG -------------------- #
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT,
            publisher TEXT,
            year INTEGER,
            quantity INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_readers_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            register_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
#Bảng mượn
def init_borrows_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            due_date TEXT,
            return_date TEXT,
            status TEXT DEFAULT 'Đang mượn',
            fine INTEGER DEFAULT 0,
            FOREIGN KEY (reader_id) REFERENCES readers(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')
    conn.commit()
    conn.close()
from flask import session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# -------------------- SÁCH -------------------- #
@app.route('/')
@login_required
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    category = request.form['category']
    publisher = request.form['publisher']
    year = request.form['year']
    quantity = request.form['quantity']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, author, category, publisher, year, quantity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, author, category, publisher, year, quantity))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit_book(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = cursor.fetchone()
    conn.close()
    return render_template('edit.html', book=book)

@app.route('/update/<int:id>', methods=['POST'])
def update_book(id):
    title = request.form['title']
    author = request.form['author']
    category = request.form['category']
    publisher = request.form['publisher']
    year = request.form['year']
    quantity = request.form['quantity']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE books SET title = ?, author = ?, category = ?, publisher = ?, year = ?, quantity = ?
        WHERE id = ?
    ''', (title, author, category, publisher, year, quantity, id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_book(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/search')
def search():
    keyword = request.args.get('q')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
    ''', ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
    books = cursor.fetchall()
    conn.close()
    return render_template('index.html', books=books)

# -------------------- ĐỘC GIẢ -------------------- #
@app.route('/readers')
@login_required
def list_readers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM readers')
    readers = cursor.fetchall()
    conn.close()
    return render_template('readers.html', readers=readers)

@app.route('/add_reader', methods=['POST'])
def add_reader():
    name = request.form['name']
    dob = request.form['dob']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    register_date = datetime.today().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO readers (name, dob, email, phone, address, register_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, dob, email, phone, address, register_date))
    conn.commit()
    conn.close()
    return redirect('/readers')

@app.route('/delete_reader/<int:id>')
def delete_reader(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM readers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/readers')

@app.route('/edit_reader/<int:id>')
def edit_reader(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM readers WHERE id = ?', (id,))
    reader = cursor.fetchone()
    conn.close()
    return render_template('edit_reader.html', reader=reader)

@app.route('/update_reader/<int:id>', methods=['POST'])
def update_reader(id):
    name = request.form['name']
    dob = request.form['dob']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE readers SET name = ?, dob = ?, email = ?, phone = ?, address = ?
        WHERE id = ?
    ''', (name, dob, email, phone, address, id))
    conn.commit()
    conn.close()
    return redirect('/readers')
#tìm độc giả
@app.route('/search_readers')
def search_readers():
    keyword = request.args.get('q')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Nếu là số, tìm theo ID hoặc tên; nếu không, chỉ tìm theo tên
    if keyword.isdigit():
        cursor.execute('''
            SELECT * FROM readers
            WHERE id = ? OR name LIKE ?
        ''', (int(keyword), '%' + keyword + '%'))
    else:
        cursor.execute('''
            SELECT * FROM readers
            WHERE name LIKE ?
        ''', ('%' + keyword + '%',))

    readers = cursor.fetchall()
    conn.close()
    return render_template('readers.html', readers=readers)
#route mượn
@app.route('/borrows')
@login_required
def borrow_list():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT b.id, r.name, bk.title, b.borrow_date, b.due_date, b.return_date, b.status, b.fine
    FROM borrows b
    JOIN readers r ON b.reader_id = r.id
    JOIN books bk ON b.book_id = bk.id
    ORDER BY b.id DESC
''')

    borrows = cursor.fetchall()
    conn.close()
    return render_template('borrows.html', borrows=borrows)
#form tạo phiếu mượn
@app.route('/borrow_form')
@login_required
def borrow_form():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM readers')
    readers = cursor.fetchall()
    cursor.execute('SELECT id, title FROM books')
    books = cursor.fetchall()
    conn.close()
    return render_template('borrow_form.html', readers=readers, books=books)
#route xử lý phiếu  mượn
@app.route('/add_borrow', methods=['POST'])
def add_borrow():
    reader_name = request.form['reader_name']
    book_title = request.form['book_title']
    borrow_date = request.form['borrow_date']
    due_date = request.form['due_date']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lấy ID độc giả theo tên
    cursor.execute('SELECT id FROM readers WHERE name = ?', (reader_name,))
    reader = cursor.fetchone()

    # Lấy ID sách và số lượng theo tên
    cursor.execute('SELECT id, quantity FROM books WHERE title = ?', (book_title,))
    book = cursor.fetchone()

    # Nếu không tìm thấy độc giả hoặc sách
    if not reader or not book:
        cursor.execute('SELECT id, name FROM readers')
        readers = cursor.fetchall()
        cursor.execute('SELECT id, title FROM books')
        books = cursor.fetchall()
        conn.close()
        return render_template('borrow_form.html', readers=readers, books=books,
                               error="❌ Không tìm thấy độc giả hoặc sách!")

    # Nếu sách đã hết
    if book[1] <= 0:
        cursor.execute('SELECT id, name FROM readers')
        readers = cursor.fetchall()
        cursor.execute('SELECT id, title FROM books')
        books = cursor.fetchall()
        conn.close()
        return render_template('borrow_form.html', readers=readers, books=books,
                               error="❌ Sách đã hết – không thể mượn!")

    # Kiểm tra hạn trả sau ngày mượn
    if due_date:
        try:
            from datetime import datetime
            borrow_dt = datetime.strptime(borrow_date, "%Y-%m-%d")
            due_dt = datetime.strptime(due_date, "%Y-%m-%d")
            if due_dt <= borrow_dt:
                cursor.execute('SELECT id, name FROM readers')
                readers = cursor.fetchall()
                cursor.execute('SELECT id, title FROM books')
                books = cursor.fetchall()
                conn.close()
                return render_template('borrow_form.html', readers=readers, books=books,
                                       error="❌ Ngày trả phải sau ngày mượn!")
        except ValueError:
            conn.close()
            return "❌ Ngày không hợp lệ!"

    # Tạo phiếu mượn
    cursor.execute('''
        INSERT INTO borrows (reader_id, book_id, borrow_date, due_date)
        VALUES (?, ?, ?, ?)
    ''', (reader[0], book[0], borrow_date, due_date))

    # Trừ số lượng sách
    cursor.execute('''
        UPDATE books SET quantity = quantity - 1 WHERE id = ?
    ''', (book[0],))

    conn.commit()
    conn.close()
    return redirect('/borrows')
#route trả sách
@app.route('/return_book/<int:borrow_id>')
def return_book(borrow_id):
    from datetime import datetime

    return_date = datetime.today().strftime('%Y-%m-%d')
    today = datetime.today()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lấy book_id + due_date từ phiếu mượn
    cursor.execute('SELECT book_id, due_date FROM borrows WHERE id = ?', (borrow_id,))
    result = cursor.fetchone()

    if result:
        book_id = result[0]
        due_date_str = result[1]
        fine = 0

        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            if today > due_date:
                delta_days = (today - due_date).days
                fine = delta_days * 2000  # 2.000đ mỗi ngày trễ

        # Cập nhật ngày trả, trạng thái, tiền phạt
        cursor.execute('''
            UPDATE borrows
            SET return_date = ?, status = 'Đã trả', fine = ?
            WHERE id = ?
        ''', (return_date, fine, borrow_id))

        # Tăng lại số lượng sách
        cursor.execute('UPDATE books SET quantity = quantity + 1 WHERE id = ?', (book_id,))
        conn.commit()

    conn.close()
    return redirect('/borrows')

@app.route('/fix_old_fines')
def fix_old_fines():
    from datetime import datetime

    today = datetime.today()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lấy tất cả các phiếu đã trả
    cursor.execute('SELECT id, due_date, return_date FROM borrows WHERE status = "Đã trả"')
    rows = cursor.fetchall()

    updated = 0
    for borrow_id, due_date_str, return_date_str in rows:
        if due_date_str and return_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
            if return_date > due_date:
                days_late = (return_date - due_date).days
                fine = days_late * 10000  # 10.000đ mỗi ngày
                cursor.execute('UPDATE borrows SET fine = ? WHERE id = ?', (fine, borrow_id))
                updated += 1

    conn.commit()
    conn.close()

    return f'✅ Đã cập nhật tiền phạt cho {updated} phiếu mượn bị trả trễ.'
#Xoá phiếu mượn khi đã "Đã trả"
@app.route('/delete_borrow/<int:borrow_id>')
def delete_borrow(borrow_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM borrows WHERE id = ?', (borrow_id,))
    conn.commit()
    conn.close()
    return redirect('/borrows')
#route thống kêkê
@app.route('/stats')
@login_required
def statistics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Sách được mượn nhiều nhất
    cursor.execute('''
        SELECT books.title, COUNT(*) AS total
        FROM borrows
        JOIN books ON borrows.book_id = books.id
        GROUP BY borrows.book_id
        ORDER BY total DESC
        LIMIT 5
    ''')
    top_books = cursor.fetchall()

    # 2. Độc giả mượn nhiều nhất
    cursor.execute('''
        SELECT readers.name, COUNT(*) AS total
        FROM borrows
        JOIN readers ON borrows.reader_id = readers.id
        GROUP BY borrows.reader_id
        ORDER BY total DESC
        LIMIT 5
    ''')
    top_readers = cursor.fetchall()

    # 3. Số lượt mượn theo tháng/năm
    cursor.execute('''
        SELECT strftime('%Y-%m', borrow_date) AS month, COUNT(*) AS total
        FROM borrows
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    ''')
    monthly_stats = cursor.fetchall()

    conn.close()
    return render_template('stats.html', top_books=top_books,
                           top_readers=top_readers, monthly_stats=monthly_stats)

def init_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                           (username, password_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            return '❌ Tên đăng nhập đã tồn tại!'
        finally:
            conn.close()
        return redirect('/login?success=1')

    
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/')
        else:
            return redirect('/login?error=1')  # 👉 Tránh render_template, dùng redirect để reset trạng thái

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# -------------------- CHẠY APP -------------------- #
if __name__ == '__main__':
    init_db()
    init_readers_table()
    init_borrows_table()
    init_users_table()  # 
    app.run(debug=True)  # ✅ thụt vào trong


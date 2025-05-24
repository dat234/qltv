from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

DB_PATH = 'database/library.db'

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Khóa bí mật cho session

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

# -------------------- DECORATOR KIỂM TRA ĐĂNG NHẬP -------------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
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
    return render_template('index.html', books=books, active_section='books', active_subsection='list_books')

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form.get('category', '')
        publisher = request.form.get('publisher', '')
        year = request.form.get('year')
        year = int(year) if year and year.isdigit() else None
        quantity = request.form['quantity']
        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 1

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (title, author, category, publisher, year, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, author, category, publisher, year, quantity))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('add_book.html', active_section='books', active_subsection='add_book')

@app.route('/edit/<int:id>')
@login_required
def edit_book(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = cursor.fetchone()
    conn.close()
    return render_template('edit.html', book=book, active_section='books', active_subsection='edit_book')

@app.route('/update/<int:id>', methods=['POST'])
@login_required
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
@login_required
def delete_book(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/search')
@login_required
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
    return render_template('index.html', books=books, active_section='books', active_subsection='list_books')

# -------------------- ĐỘC GIẢ -------------------- #
@app.route('/readers')
@login_required
def list_readers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM readers')
    readers = cursor.fetchall()
    conn.close()
    return render_template('readers.html', readers=readers, active_section='readers', active_subsection='list_readers')

@app.route('/add_reader', methods=['GET', 'POST'])
@login_required
def add_reader():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form.get('address', '')
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

    return render_template('add_reader.html', active_section='readers', active_subsection='add_reader')

@app.route('/delete_reader/<int:id>')
@login_required
def delete_reader(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM readers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/readers')

@app.route('/edit_reader/<int:id>')
@login_required
def edit_reader(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM readers WHERE id = ?', (id,))
    reader = cursor.fetchone()
    conn.close()
    return render_template('edit_reader.html', reader=reader, active_section='readers', active_subsection='edit_reader')

@app.route('/update_reader/<int:id>', methods=['POST'])
@login_required
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

@app.route('/search_readers')
@login_required
def search_readers():
    keyword = request.args.get('q')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
    return render_template('readers.html', readers=readers, active_section='readers', active_subsection='list_readers')

# -------------------- MƯỢN TRẢ -------------------- #
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
    WHERE b.status = 'Đang mượn'
    ORDER BY b.id DESC
''')

    borrows = cursor.fetchall()
    conn.close()
    return render_template('borrows.html', borrows=borrows, active_section='borrows', active_subsection='borrow_list')

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
    return render_template('borrow_form.html', readers=readers, books=books, active_section='borrows', active_subsection='borrow_form')

@app.route('/add_borrow', methods=['POST'])
@login_required
def add_borrow():
    reader_name = request.form['reader_name']
    book_title = request.form['book_title']
    borrow_date = request.form['borrow_date']
    due_date = request.form['due_date']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM readers WHERE name = ?', (reader_name,))
    reader = cursor.fetchone()

    cursor.execute('SELECT id, quantity FROM books WHERE title = ?', (book_title,))
    book = cursor.fetchone()

    if not reader or not book:
        cursor.execute('SELECT id, name FROM readers')
        readers = cursor.fetchall()
        cursor.execute('SELECT id, title FROM books')
        books = cursor.fetchall()
        conn.close()
        return render_template('borrow_form.html', readers=readers, books=books, active_section='borrows', active_subsection='borrow_form',
                               error="❌ Không tìm thấy độc giả hoặc sách!")

    if book[1] <= 0:
        cursor.execute('SELECT id, name FROM readers')
        readers = cursor.fetchall()
        cursor.execute('SELECT id, title FROM books')
        books = cursor.fetchall()
        conn.close()
        return render_template('borrow_form.html', readers=readers, books=books, active_section='borrows', active_subsection='borrow_form',
                               error="❌ Sách đã hết – không thể mượn!")

    if due_date:
        try:
            borrow_dt = datetime.strptime(borrow_date, "%Y-%m-%d")
            due_dt = datetime.strptime(due_date, "%Y-%m-%d")
            if due_dt <= borrow_dt:
                cursor.execute('SELECT id, name FROM readers')
                readers = cursor.fetchall()
                cursor.execute('SELECT id, title FROM books')
                books = cursor.fetchall()
                conn.close()
                return render_template('borrow_form.html', readers=readers, books=books, active_section='borrows', active_subsection='borrow_form',
                                       error="❌ Ngày trả phải sau ngày mượn!")
        except ValueError:
            conn.close()
            return "❌ Ngày không hợp lệ!"

    cursor.execute('''
        INSERT INTO borrows (reader_id, book_id, borrow_date, due_date)
        VALUES (?, ?, ?, ?)
    ''', (reader[0], book[0], borrow_date, due_date))

    cursor.execute('''
        UPDATE books SET quantity = quantity - 1 WHERE id = ?
    ''', (book[0],))

    conn.commit()
    conn.close()
    return redirect('/borrows')

@app.route('/return_book/<int:borrow_id>')
@login_required
def return_book(borrow_id):
    return_date = datetime.today().strftime('%Y-%m-%d')
    today = datetime.today()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

        cursor.execute('''
            UPDATE borrows
            SET return_date = ?, status = 'Đã trả', fine = ?
            WHERE id = ?
        ''', (return_date, fine, borrow_id))

        cursor.execute('UPDATE books SET quantity = quantity + 1 WHERE id = ?', (book_id,))
        conn.commit()

    conn.close()
    return redirect('/borrows')

@app.route('/borrows/returned')
@login_required
def returned_borrow_list():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, r.name, bk.title, b.borrow_date, b.due_date, b.return_date, b.status, b.fine
        FROM borrows b
        JOIN readers r ON b.reader_id = r.id
        JOIN books bk ON b.book_id = bk.id
        WHERE b.status = 'Đã trả'
        ORDER BY b.return_date DESC
    ''')
    returned_borrows = cursor.fetchall()
    conn.close()
    return render_template('returned_borrows.html', borrows=returned_borrows, active_section='borrows', active_subsection='borrow_returned')

@app.route('/fix_old_fines')
@login_required
def fix_old_fines():
    today = datetime.today()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

@app.route('/delete_borrow/<int:borrow_id>')
@login_required
def delete_borrow(borrow_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM borrows WHERE id = ?', (borrow_id,))
    conn.commit()
    conn.close()
    return redirect('/borrows')

# -------------------- THỐNG KÊ -------------------- #
@app.route('/stats')
@login_required
def statistics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- Tổng quan ---
    cursor.execute('SELECT COUNT(*) FROM books')
    total_books = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM readers')
    total_readers = cursor.fetchone()[0]

    # --- Tình trạng sách ---
    cursor.execute('SELECT COUNT(*) FROM borrows WHERE return_date IS NULL')
    borrowed_books = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM borrows WHERE return_date IS NOT NULL')
    returned_books = cursor.fetchone()[0]

    # --- Doanh thu phạt ---
    cursor.execute('''
        SELECT SUM(fine) AS total_fine
        FROM borrows
        WHERE fine > 0
    ''')
    fine_revenue = cursor.fetchone()[0] or 0

    # --- Sách được mượn nhiều nhất ---
    cursor.execute('''
        SELECT b.title, COUNT(*) AS total
        FROM borrows bo
        JOIN books b ON bo.book_id = b.id
        GROUP BY bo.book_id
        ORDER BY total DESC
        LIMIT 5
    ''')
    top_books = cursor.fetchall()

    # --- Độc giả mượn nhiều nhất ---
    cursor.execute('''
        SELECT r.name, COUNT(*) AS total
        FROM borrows bo
        JOIN readers r ON bo.reader_id = r.id
        GROUP BY bo.reader_id
        ORDER BY total DESC
        LIMIT 5
    ''')
    top_readers = cursor.fetchall()

    # --- Thống kê theo tháng ---
    cursor.execute('''
        SELECT strftime('%Y-%m', borrow_date) AS month, COUNT(*) AS total
        FROM borrows
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    ''')
    monthly_stats = cursor.fetchall()

    conn.close()
    return render_template('stats.html',
                           total_books=total_books,
                           total_readers=total_readers,
                           borrowed_books=borrowed_books,
                           returned_books=returned_books,
                           fine_revenue=fine_revenue,
                           top_books=top_books,
                           top_readers=top_readers,
                           monthly_stats=monthly_stats,
                           active_section='stats',
                           active_subsection='overview_report')

# -------------------- TÀI KHOẢN -------------------- #
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
            conn.close() # Đảm bảo đóng kết nối trước khi trả về
            return '❌ Tên đăng nhập đã tồn tại!'
        finally:
            conn.close()
        return redirect(url_for('login', success=1))

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
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login', error=1))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route('/account/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    success_message = None
    error_message = None

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']
        user_id = session['user_id']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            error_message = 'Lỗi: Không tìm thấy thông tin người dùng.'
        elif not check_password_hash(user_data[0], current_password):
            error_message = 'Mật khẩu hiện tại không đúng.'
        elif new_password != confirm_new_password:
            error_message = 'Mật khẩu mới và xác nhận mật khẩu không khớp.'
        elif len(new_password) < 6: # Thêm kiểm tra độ dài mật khẩu
            error_message = 'Mật khẩu mới phải có ít nhất 6 ký tự.'
        else:
            new_password_hash = generate_password_hash(new_password)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id))
            conn.commit()
            conn.close()
            success_message = 'Mật khẩu đã được thay đổi thành công!'

    return render_template('change_password.html', success_message=success_message, error_message=error_message, active_section='account', active_subsection='change_password')

# -------------------- CHẠY APP -------------------- #
if __name__ == '__main__':
    if not os.path.exists('database'):
        os.makedirs('database')
    init_db()
    init_readers_table()
    init_borrows_table()
    init_users_table()
    app.run(port=5001, debug=True)

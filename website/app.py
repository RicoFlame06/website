import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session


# Creates databases
def database():
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                )       
            ''')
    
    cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
                )       
            ''')
    
    con.commit()
    con.close()
    

    
    
@app.route('/')
def home():
    return render_template('register.html')
    
@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']

        hashed_password = generate_password_hash(password) # Hashes passwords
        
        # Inserts user input into the database
        try:
            con = sqlite3.connect('users.db')
            cur = con.cursor()
            cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            con.commit()
            con.close()
            return redirect(url_for('login'))  # ✅ Redirect to login

        except sqlite3.IntegrityError:
            flash("Email already registered")
            return redirect(url_for('register'))
        
        
    return render_template('register.html')


    
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        con = sqlite3.connect('users.db')
        con.row_factory = sqlite3.Row

        user = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        con.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to a dashboard page
        else:
            flash("Invalid Credentials", 'error')
            return redirect(url_for('login'))
        
    return render_template('login.html')

    
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', email=session['email'])  # You’ll make this file next

@app.route('/todo_list')
def todo_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))


    user_id = session.get('user_id')
    
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cur.fetchall()
    con.close()

    return render_template('to-do-list.html', email=session['email'], tasks=tasks)  # You’ll make this file next



@app.route('/add', methods=["GET", "POST"])
def add_task():

    if request.method == 'POST':
        task = request.form['task']
        user_id = session.get('user_id')
        

        if not task:
            return redirect(url_for('todo_list'))
        
        # Inserts user input into the database
        try:
            con = sqlite3.connect('users.db')
            cur = con.cursor()
            cur.execute("INSERT INTO tasks (task, user_id) VALUES (?, ?)", (task, user_id))
            con.commit()
            con.close()
            return redirect(url_for('todo_list'))
  # ✅ Redirect to to do list

        except sqlite3.IntegrityError:
            flash("Invalid task")
            return redirect(url_for('todo_list'))
        
        
    return redirect(url_for('todo_list'))






@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    database()
    app.run(debug=True)  # Default is host='127.0.0.1' and port=5000

import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session


# Creates user database
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

@app.route('/to-do-list')
def todolist():
    if 'user_id' not in session:
        return redirect(url_for('to-do-list'))

    return render_template('to-do-list.html', email=session['email'])  # You’ll make this file next


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    database()
    app.run(debug=True)  # Default is host='127.0.0.1' and port=5000

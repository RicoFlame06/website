from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)

# Dummy user for demonstration
EMAIL = "ricardo@gmail.com"
PASSWORD = "password123"




@app.route('/')
def home():
    return redirect(url_for('login'))


def is_valid_password(password):
    if len(password) < 8:
        return "Password must be 8 characters"
    if not any(char.isdigit() for char in password):
        return "Password must contain a number"
    if not any(char in "!@#$%^&*()" for char in password):
        return "Password must contain a symbol" 
    if not any(char.isupper() for char in password):
        return "Password must contain an upper case character"
    if not any(char.islower() for char in password):
        return "Password must contain a lowercase case character"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == EMAIL and password == PASSWORD:
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']

    
        if password != cpassword:
                return render_template('register.html', error="Passwords don't match")
        
        error = is_valid_password(password)
        if error:
            return render_template('register.html', error=error)
        
        return render_template('register.html', error="Email taken")


    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

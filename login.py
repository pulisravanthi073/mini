from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Initialize SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
''')
conn.commit()
conn.close()

# Route: Login
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE email=?", (email,))
        row = c.fetchone()
        conn.close()

        if row and bcrypt.check_password_hash(row[0], password):
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid email or password"

    return render_template('login.html', error=error)

# Route: Dashboard
@app.route('/dashboard')
def dashboard():
    return "<h1>Welcome to your Dashboard!</h1>"

# Route: Register (for testing)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Email already exists"
        finally:
            conn.close()
        return redirect(url_for('login'))

    return '''
    <form method="POST">
        <input name="email" placeholder="Email" required>
        <input name="password" placeholder="Password" type="password" required>
        <button type="submit">Register</button>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)

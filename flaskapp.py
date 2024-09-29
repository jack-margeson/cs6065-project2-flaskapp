from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = sqlite3.connect('/home/ubuntu/flaskapp/mydatabase.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT, password TEXT, firstname TEXT, lastname TEXT, email TEXT)''')
conn.commit()
conn.close()

def count_words_in_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
        words = text.split()
    return len(words)


@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']

    conn = sqlite3.connect('/home/ubuntu/flaskapp/mydatabase.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)",
              (username, password, firstname, lastname, email))
    conn.commit()
    conn.close()

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('/home/ubuntu/flaskapp/mydatabase.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[1] == password:
            session['username'] = username
            return redirect(url_for('profile', username=username))
        else:
            error = 'Invalid username or password. Please try again.'

    return render_template('login.html', error=error)

@app.route('/profile/<username>')
def profile(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))

    conn = sqlite3.connect('/home/ubuntu/flaskapp/mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    word_count = count_words_in_file('/home/ubuntu/flaskapp/Limerick-1.txt')

    return render_template('profile.html', user=user, word_count=word_count)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/download-limerick')
def download():
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(directory='/home/ubuntu/flaskapp', path='Limerick-1.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

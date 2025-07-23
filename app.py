from flask import Flask, render_template
app = Flask(__name__)
app.debug = True

app.secret_key = 'This is your secret key to utilize session in Flask'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=("GET", "POST"))
def input():
    return render_template('input.html')


if __name__ == '__main__':
    app.run(port=4455)
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/<username>')
def hello(username):
    if username == 'admin':
        role = 'admin'
        age = 30
    else:
        role = 'user'
        age = 16
        
    user_data = {
        'name': username,
        'role': role,
        'age' : age
    }
    return render_template("welcome.html", user=user_data)

if __name__ == '__main__':
    app.run(debug=True)
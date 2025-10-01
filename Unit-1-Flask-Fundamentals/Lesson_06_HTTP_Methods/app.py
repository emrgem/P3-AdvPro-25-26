from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    # return 'Hello, World!'
    return render_template("home.html")

@app.route('/profile/<username>')
def profile(username):
    user_data = {
        'name': username,
        'school': 'BT',
        'age': 16,
        'is_present':True
    }
    return render_template("profile.html", user=user_data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact_form.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        user_data = {
            'name': name,
            'email': email,
            'message': message,     
        }
        
        # return f"Thanks {name}! We'll contact you at {email}"
        return render_template('success.html', user=user_data)
    
if __name__ == '__main__':
    app.run(debug=True)
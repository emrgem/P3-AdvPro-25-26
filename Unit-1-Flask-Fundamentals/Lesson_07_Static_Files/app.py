from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
            <a href="/feedback"> Feedback Form </a>
        '''
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        rating = request.form.get('rating')
        return render_template('form.html', name=name, rating=rating)
    # if request.method == 'GET':
    return render_template('form.html')
if __name__ == '__main__':
    app.run(debug=True)
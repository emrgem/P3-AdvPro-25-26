from flask import Flask, render_template
import csv
app = Flask(__name__)

# Function to read/import csv to list of dicts
def read_roster():
    students = []
    with open('roster.csv', 'r') as file:
        reader = csv.DictReader(file)
        # for row in reader:
        #     students.append(row)
        # return students
        return [row for row in reader]

@app.route('/')
def home():
    """Home page with link to roster"""
    return '''
    <html>
        <head>
            <title>Class Roster App</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    text-align: center;
                }
                h1 { color: #4fc3f7; }
                a {
                    display: inline-block;
                    padding: 15px 30px;
                    background: #4fc3f7;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 18px;
                }
                a:hover { background: #3ba8d6; }
            </style>
        </head>
        <body>
            <h1>Class Roster Application</h1>
            <p>View the student roster for Advanced Programming</p>
            <a href="/roster">👥View Roster</a>
            <a href="/stats">📊View Stats</a>
        </body>
    </html>
    '''

@app.route('/roster')
def roster():
    students = read_roster()
    # print(students)
    return render_template('roster.html', students=students)   

@app.route('/stats', methods=['GET'])
def statistics():
    students = read_roster()
    # Calculate statistics
    total = len(students)
    seniors = [s for s in students if s['Grade'] == 12]
    juniors = [s for s in students if s['Grade'] == 11]
    sophomores = [s for s in students if s['Grade'] == 10]
    freshmen = [s for s in students if s['Grade'] == 9]
    males = [s for s in students if s['Gender'] == 'M']
    females = [s for s in students if s['Gender'] == 'F']
    
    data = {
    "students": students,
    "total": total,
    "seniors": seniors,
    "juniors": juniors,
    "sophomores": sophomores,
    "freshmen": freshmen,
    "males": males,
    "females": females
    }
    return render_template('stats.html', **data)

if __name__ == '__main__':
    app.run(debug=True)

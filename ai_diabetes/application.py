from flask import Flask, request, redirect
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
import pandas as pd
from sklearn import linear_model


application = Flask(__name__)
application.debug = True

high_bp, high_chol, stroke, heart_disease, diff_walk = ('', '', '', '', '')
bmi, age = ('', '')
fname, mname, lname = ('', '', '')
gender = ''
city, suburb = ('', '')


application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Diabetes.db'

db = SQLAlchemy(application)

migrate = Migrate(application, db)


class Doctor(db.Model):
    ID = db.Column(db.Integer, primary_key=True)

    Full_Name = db.Column(db.String(20), unique=False, nullable=False)
    Center = db.Column(db.String(200), unique=False, nullable=False)
    City = db.Column(db.String(100), unique=False, nullable=False)
    Suburb = db.Column(db.String(100), unique=False, nullable=False)
    Phone = db.Column(db.String(100), unique=False, nullable=False)
    Rating = db.Column(db.String(5), unique=False, nullable=False)


with application.app_context():
    db.create_all()

def home():
    return render_template('home.html')

def index():
    return render_template('index.html')

def predict_step1():
    return render_template('step1.html')

def step1():
    global high_bp, high_chol, stroke, heart_disease, diff_walk

    high_bp = request.form.get('HighBP')
    high_chol = request.form.get('HighChol')
    stroke = request.form.get('Stroke')
    heart_disease = request.form.get('HeartDisease')
    diff_walk = request.form.get('DiffWalk')

    return redirect('/predict/step2')

def predict_step2():
    bmi = [int(i) for i in range(7, 252)]
    age = [int(i) for i in range(0, 101)]
           
    return render_template('step2.html', bmi = bmi, age = age)
    
def step2():
    global bmi, age

    bmi = request.form.get('BMI')
    age = request.form.get('Age')

    return redirect('/predict/step3')

def predict_step3():
    return render_template('step3.html')

def step3():
    global fname, mname, lname
    global gender
    global city, suburb

    fname = request.form.get('FirstName')
    mname = request.form.get('MiddleName')
    lname = request.form.get('LastName')

    gender = request.form.get('Gender')

    city = request.form.get('City')
    suburb = request.form.get('Suburb')

    return redirect('/predict/result')

def result():
    global high_bp, high_chol, stroke, heart_disease, diff_walk, bmi, age
    global fname, mname, lnmae, gender

    high_bp = 1 if high_bp == 'Yes' else 0
    high_chol = 1 if high_chol == 'Yes' else 0
    stroke = 1 if stroke == 'Yes' else 0
    heart_disease = 1 if heart_disease == 'Yes' else 0
    diff_walk = 1 if diff_walk == 'Yes' else 0

    bmi = int(bmi)
    age = int(age)

    data = pd.read_csv('Diabetes_Health_Indicators.csv')

    X = data[['HighBP', 'HighChol', 'Stroke', 'HeartDisease', 'DiffWalk', 'BMI', 'Age']]
    y = data['Diabetes_012']

    regr = linear_model.LinearRegression()
    regr.fit(X,y)

    prediction = regr.predict([[high_bp, high_chol, stroke, heart_disease, diff_walk, bmi, age]])

    print(prediction)
    
    prediction = round(prediction[0], 0)

    if prediction == 0:
        prediction = 'No Diabetes'

    elif prediction == 1:
        prediction = 'Pre Diabetes'

    else:
        prediction = 'Diabetes'
    
    return render_template('result.html', name = fname + ' ' + mname + ' ' + lname, \
                           high_bp = high_bp, high_chol = high_chol, stroke = stroke, \
                           heart_disease = heart_disease, diff_walk = diff_walk, bmi = bmi, age = age, \
                           prediction = prediction)

def find_doctor():
    global city, suburb

    data = Doctor.query.all()

    return render_template('nearby.html', data = data)
    
application.add_url_rule('/', 'home', home)

application.add_url_rule('/predict/step1', 'predict_step1', predict_step1)
application.add_url_rule('/step1', 'step1', step1, methods=['POST'])

application.add_url_rule('/predict/step2', 'predict_step2', predict_step2)
application.add_url_rule('/step2', 'step2', step2, methods=['POST'])

application.add_url_rule('/predict/step3', 'predict_step3', predict_step3)
application.add_url_rule('/step3', 'step3', step3, methods=['POST'])

application.add_url_rule('/predict/result', 'result', result)

application.add_url_rule('/nearby', 'nearby', find_doctor, methods=['POST'])


if __name__ == '__main__':
    application.run()

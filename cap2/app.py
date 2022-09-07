from email.message import EmailMessage
from plistlib import UID
from flask import Flask, render_template, url_for, request, redirect, session, flash
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
# Importing essential libraries
from flask import Flask, render_template, request
import pickle
import numpy as np

# Load the Random Forest CLassifier model
filename = 'covid.pkl'
classifier = pickle.load(open(filename, 'rb'))

app = Flask(__name__)

app.secret_key = '1' # for flask session


# Use a service account
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# pyrebase init
# Your web app's Firebase configuration
firebaseConfig = {
   'apiKey': "AIzaSyCvNo0fzI_RX4k9R0ZgkSDt8LWOpsP2FaM",
   'authDomain': "dokonsulta-d5145.firebaseapp.com",
   'databaseURL': "https://dokonsulta-d5145-default-rtdb.firebaseio.com",
  'projectId': "dokonsulta-d5145",
  'storageBucket': "dokonsulta-d5145.appspot.com",
  'messagingSenderId': "427575389379",
  'appId': "1:427575389379:web:505a3f3ca8eec6945ac676",
  'measurementId': "G-LBH6E12KWG"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()



@app.route('/', methods = ['GET'])
def home_page():
    if 'user' not in session:
        return render_template('home_page.html')
    else:
        return redirect('/logout')


#Patient Login
@app.route('/patient_login', methods = ['GET', 'POST'])
def patient_login():
    if request.method == 'GET':
        if 'user' not in session:
            return render_template('patient_login.html')
        else:
            return redirect('/logout')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        

        # check e-mail,pass
        flag_4 = False
        # check pass
        try:
            patient_user = auth.sign_in_with_email_and_password(email, password)
           
            
            # e-mail verification check
            acc_info = auth.get_account_info(patient_user['idToken'])
            if acc_info['users'][0]['emailVerified'] == False:
                flag_4 = True
        except:
            flag_3 = False
        if  flag_4 == False:
            flash('Incorrect, unverified or non-existent e-mail, division or password...', 'error')
            return redirect('/patient_login')
    
        
        session['user'] = email
        session['person_type'] = 'patient'
        return redirect('/patient_dashboard')



@app.route('/patient_signup', methods = ['GET', 'POST'])
def patient_signup():
    if request.method == 'GET':
        if 'user' not in session:
            return render_template('patient_signup.html')
        else:
            return redirect('/logout')

    elif request.method == 'POST':
        
        fname = request.form['fname']
        lname = request.form['lname']
        mname = request.form['mname']
        gender = request.form['gender']
        dob = request.values['dob']
        
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']

        # check if passwords match
        if password != password2:
            flash('The passwords do not match...', 'error')
            return redirect('/teacher_signup')
        # check length of pass
        if len(password) < 6:
            flash('The password has to be more than 5 characters long...', 'error')
            return redirect('/patient_signup')
        
        # auth user
        try:
            patient_user = auth.create_user_with_email_and_password(email, password)
        except:
            flash('This e-mail has already been registered. Please use another e-mail...', 'error')
            return redirect('/patient_signup')
        # e-mail verification
        auth.send_email_verification(patient_user['idToken'])

        # add patient to db
        #db.collection('patient').document(patient['localId']).set({
        db.collection('patient').document(email).set({
            'fname': fname,
            'lname': lname,
            'mname': mname,
            'gender': gender,
            'dob': dob,
            'password': password # firebase auth
        })
       
       
       
       
    
       
    
       

        flash('Registration successful! Please check your e-mail for verification and then log in...', 'info')
        return redirect('/patient_login')



@app.route('/patient_dashboard', methods = ['GET'])
def patient_dashboard():
    if 'user' in session and session['person_type'] == 'patient':
        
        patient_details = db.collection('patient').document(session['user']).get()
        
        
        lec_conducted_count = 0
    
        
        attendance = {}
        
         
        return render_template('patient_dashboard.html', patient_details = patient_details.to_dict()  )
    else:
        return redirect('/logout')



@app.route('/logout', methods = ['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)
        session.pop('person_type', None)
        session.pop('division', None)

        flash('You have been logged out...', 'warning')
        return redirect('/')
    else:
        return redirect('/')



@app.route('/forgot_password', methods = ['GET', 'POST'])
def forgotPassword():
    if request.method == 'GET':
        if 'user' not in session:
            return render_template('forgot_password_page.html')
        else:
            return redirect('/logout')
    elif request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
        except:
            flash('That e-mail ID is not registered...', 'error')
            return redirect('/')
        flash('Check your e-mail to set new password...', 'info')
        return redirect('/')


@app.route('/predict', methods=['GET','POST'])
def predict():
    if request.method == 'GET':
        if 'user' in session and session['person_type'] == 'patient':
            return render_template('predict.html')
        else:
            return redirect('/logout')
    elif request.method =='POST':
        if 'user' in session and session['person_type'] == 'patient':
        
            patient_details = db.collection('patient').document(session['user']).get()
             

            age = request.form['age']
            cough = request.form['cough']
            fever = request.form['fever']
            sr = request.form['sorethroat']
            sb = request.form['shortbreath']
            ha = request.form['headache']
            cic = request.form['cic']
            gender = request.form['gender']

            data = np.array([[age,cough,fever,sr,sb,ha,cic,gender]])
            my_prediction = classifier.predict(data)
            
            
            
            
            
            
            return render_template('result.html', prediction=my_prediction)
            


    else:
        return redirect('/logout')

if __name__ == '__main__':
    app.run(debug = True)
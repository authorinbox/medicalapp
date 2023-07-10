from flask import Flask, render_template, redirect, request, session, jsonify, url_for, Response
from turbo_flask import Turbo
from apscheduler.schedulers.background import BackgroundScheduler
from api import *
import threading
import os
import csv
import time
import stripe
import io
import xlwt
import random

def send_email(from_email, from_pass, to_email, subject, body, hosting, port):
        
    import smtplib
    from email.mime.text import MIMEText
    
    sender_email = from_email
    sender_password = from_pass
    recipient_email = to_email
    subject = subject
    body = f"""
    <html>
    <body>
        {body}
    </body>
    </html>
    """
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = recipient_email

    server = smtplib.SMTP_SSL(hosting, port)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, html_message.as_string())
    server.quit()

def shift_amount(i):
    return i%26

alphabet = 'abcdefghijklmnopqrstuvwqyz'

def encrypt(text, required_shift):
    out_string = ''
    text = text.lower() 
    for char in text:
        if char not in alphabet: 
            out_string = out_string + char
        else:
            alpha_index = alphabet.find(char) 
            out_string = out_string + alphabet[shift_amount(alpha_index +required_shift)]
    return out_string 

stripe.api_key = "sk_test_51N2SQHSGFNkJqmhn6bvGMgnmPBuvJGoHmWzG6ugloAG7HoQmbiHE9SGOeCoRAly0hPeNpJNgJDRNix7hzwNzO4Q500Extn3i6b"

journals = ''

YOUR_DOMAIN = "http://localhost:1250"
UPLOAD_FOLDER = "./static/journals"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_credits_and_journals():
    filename = "premium_db.csv"
    credits = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        credits.append(rows.pop(0))
        for row in rows:
            date_struct = time.strptime(row[2], '%d/%m/%Y')
            timestamp = time.mktime(date_struct)
            new_timestamp = timestamp + 30 * 24 * 60 * 60
            new_date_struct = time.localtime(new_timestamp)
            new_date_str = time.strftime('%d/%m/%Y', new_date_struct)
            credits.append([row[0], row[1], row[2], row[3], new_date_str])
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(credits.pop(0))
        for credit in credits:
            if time.strftime('%d/%m/%Y') != credit[4]:
                writer.writerow(credit[:-1])
            else:                
                continue
            '''
    graces = {}
    with open("journals_name.csv", 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        emails = [row[0] for row in data[1:]]
        if session['user_id'] in emails:
            for row in data[1:]:
                if row[0] == session['user_id']:
                    date_struct = time.strptime(row[8], '%d/%m/%Y')
                    timestamp = time.mktime(date_struct)
                    new_timestamp = timestamp + 30 * 24 * 60 * 60
                    new_date_struct = time.localtime(new_timestamp)
                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)                                
                    exp_time = time.strptime(new_date_str, '%d/%m/%Y')
                    new_timestamp = timestamp + 45 * 24 * 60 * 60
                    new_date_struct = time.localtime(new_timestamp)
                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)
                    grc_time = time.strptime(new_date_str, '%d/%m/%Y')
                    if exp_time < time.gmtime() and time.gmtime() < grc_time:
                        graces[row[1]] = [row[2], row[8], new_date_str]    
    with open("journals_name.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(credits.pop(0))
        for credit in credits:
            if time.strftime('%d/%m/%Y') != credit[4]:
                writer.writerow(credit[:-1])
            else:                
                continue
    body = f"""
    <html>
    <body>
        <h1>Verify Your Email Address</h1>
        <p>Your verification code is: <b>{code}</b> </p>
    </body>
    </html>
    """
    send_email("pandeyrainy2020@gmail.com", "ohgltbipjxwmvqck", email, "Verification Email", body, "smtp.gmail.com", 465)
                        
            '''
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(delete_credits_and_journals,'interval',hours=23)
scheduler.start()

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)
turbo = Turbo(app)

@app.route('/') 
def main(message=False):
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('home.html', alert=message)
    
@app.route('/home', methods=['GET', 'POST'])
def home(message=False, searches=False, journals=False):
    if 'func' in session:
        if session['func'] == "Normal":
            if 'user_id' in session:
                if session['sub'] == "Trial":
                    filename = "trial_db.csv"
                    with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        data = list(reader)
                        emails = [row[0] for row in data[1:]]
                    if session['user_id'] in emails:
                        for row in data[1:]:
                            print(row)
                            if row[0] == session['user_id']:
                                searches = row[1]
                    return render_template('overview.html', alert=message, trial="trial",  searches=searches)
                elif session['sub'] == "Premium":       
                    filename = "journals_db.csv"
                    with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        data = list(reader)
                        emails = [row[0] for row in data[1:]]
                    no_of_jour = 0
                    if session['user_id'] in emails:
                        for row in data[1:]:
                            if row[0] == session['user_id']:
                                filename = "journals_name.csv"
                                with open(filename, 'r') as file:
                                    reader = csv.reader(file)
                                    data = list(reader)
                                    emails = [row[0] for row in data[1:]]
                                    no_of_jour = int(emails.count(session['user_id']))
                    filename = "premium_db.csv"
                    credits = {}
                    with open(filename, 'r') as file:
                                    reader = csv.reader(file)
                                    rows = list(reader)
                                    for row in rows:
                                        if row[0] == session['user_id']:
                                            date_struct = time.strptime(row[2], '%d/%m/%Y')
                                            timestamp = time.mktime(date_struct)
                                            new_timestamp = timestamp + 30 * 24 * 60 * 60
                                            new_date_struct = time.localtime(new_timestamp)
                                            new_date_str = time.strftime('%d/%m/%Y', new_date_struct)
                                            credits[row[3]] = [row[1], row[2], new_date_str]
                    for key, value in credits.items():
                        credits[key] = [value[0], value[1], time.strptime(value[2], '%d/%m/%Y')]                      
                    sorted_credits = dict(sorted(credits.items(), key=lambda item: item[1][2]))
                    for key, value in sorted_credits.items():
                        sorted_credits[key] = [value[0], value[1], time.strftime('%d/%m/%Y', value[2])]
                    sorted_credits = [[key, [int(value[0]), value[1], value[2]]] for key, value in sorted_credits.items()]
                    print(sorted_credits)
                    credits = {}
                    for credit in sorted_credits:
                        if no_of_jour > credit[1][0]:
                            no_of_jour -= credit[1][0]
                        elif no_of_jour == credit[1][0]:
                            for left_credit in sorted_credits[sorted_credits.index(credit)+1:]:
                                credits[left_credit[0]] = left_credit[1]
                            break
                        else:
                            credit[1][0] -= no_of_jour
                            credits[credit[0]] = [credit[1][0], credit[1][1]]
                            for item in sorted_credits[sorted_credits.index(credit):]:
                                credits[item[0]] = item[1]
                            break
                    graces = {}
                    with open("journals_name.csv", 'r') as file:
                        reader = csv.reader(file)
                        data = list(reader)
                        emails = [row[0] for row in data[1:]]
                        if session['user_id'] in emails:
                            for row in data[1:]:
                                if row[0] == session['user_id']:
                                    date_struct = time.strptime(row[8], '%d/%m/%Y')
                                    timestamp = time.mktime(date_struct)
                                    new_timestamp = timestamp + 30 * 24 * 60 * 60
                                    new_date_struct = time.localtime(new_timestamp)
                                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)                                
                                    exp_time = time.strptime(new_date_str, '%d/%m/%Y')
                                    new_timestamp = timestamp + 45 * 24 * 60 * 60
                                    new_date_struct = time.localtime(new_timestamp)
                                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)
                                    grc_time = time.strptime(new_date_str, '%d/%m/%Y')
                                    if exp_time < time.gmtime() and time.gmtime() < grc_time:
                                        graces[row[1]] = [row[2], row[8], new_date_str]
                    journals = {}
                    with open("journals_name.csv", 'r') as file:
                        reader = csv.reader(file)
                        data = list(reader)
                        emails = [row[0] for row in data[1:]]
                        if session['user_id'] in emails:
                            for row in data[1:]:
                                if row[0] == session['user_id']:
                                    date_struct = time.strptime(row[8], '%d/%m/%Y')
                                    timestamp = time.mktime(date_struct)
                                    new_timestamp = timestamp + 30 * 24 * 60 * 60
                                    new_date_struct = time.localtime(new_timestamp)
                                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)                                
                                    exp_time = time.strptime(new_date_str, '%d/%m/%Y')
                                    if time.gmtime() < exp_time and row[1] not in graces:
                                        journals[row[1]] = [row[2], row[8], new_date_str]
                    filename = "journals_name.csv"
                    with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        data = list(reader)
                        emails = [row[0] for row in data[1:]]
                        total_journals = int(emails.count(session['user_id']))
                    journals = dict(reversed(list(journals.items())))
                    graces = dict(reversed(list(graces.items())))
                    credits = dict(reversed(list(credits.items())))
                    print(journals, graces, credits)
                    return render_template('overview.html', alert=message, premium="premium", total_journals=total_journals, journals=journals, graces=graces, credits=credits)
            else:
                return redirect("/")
        elif session['func'] == "Payment":
            return redirect("/payment")
    else:
        return redirect("/")
    
@app.route('/testing/')
def testing(message=False):
    return render_template('addlisting.html', db_id=session['listing_id'])
    
@app.route('/contact')
def contact(message=False):
    return render_template('contact.html', alert=message)

@app.route('/adv-form', methods=['GET', 'POST'])
def adv_form(message=False):
    name = request.form.get('name')
    email = request.form.get('email')
    org = request.form.get('org')
    message = request.form.get('message')
    filename = 'adv_form.csv'
    with open(filename, 'a', newline="") as file:
        writer = csv.writer(file)
        new_row = [name, email, org, message]
        writer.writerow(new_row)        
    return contact("Thank You !! We have registered your request")

@app.route('/trial', methods=['GET', 'POST'])
def trial(message=False):
    session['func'] = "Free Trial"
    return register("Please register before starting the free trial")

@app.route('/basic-plan', methods=['GET', 'POST'])
def basic_plan(message=False):
    session['func'] = "Payment"
    return register("Please register before subscribing")

@app.route('/payment', methods=['GET', 'POST'])
def payment(message=False):
    return render_template('payment.html', alert=message)

@app.route('/payment-form', methods=['GET', 'POST'])
def payment_form(message=False):
    journals = request.form.get('journals')
    session['journals'] = journals
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1NSLuLSGFNkJqmhnHogN3s4N',
                    'quantity': int(journals),
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/pay_suc',
            cancel_url=YOUR_DOMAIN + '/pay_fail',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/pay_suc', methods=['GET', 'POST'])
def pay_suc():
    session['func'] = "Normal"
    session['sub'] = "Premium"
    with open("premium_db.csv", 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
    with open("premium_db.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] != session['user_id']:
                writer.writerow(row)
            else:
                row[1] = session['journals']
                row[2] = time.strftime('%d/%m/%Y')
                writer.writerow(row)
    with open('journals_db.csv', 'a', newline='') as journal_file:
        journal_writer = csv.writer(journal_file)
        journal_writer.writerow([session['user_id'], session['journals']])
    return home("Payment Successful\n!\nTo start creating, go to Journals tab", journals=session['journals'])

@app.route('/pay_fail', methods=['GET', 'POST'])
def pay_fail():
    return payment("Payment Failed !!! Please try again")

@app.route('/login', methods=['GET', 'POST'])
def login(message=False):
    if 'user_id' in session:
        return redirect('/home')
    else:
        session['func'] = "Normal"
        return render_template('login.html', alert=message)

@app.route('/login_valid', methods=['GET', 'POST'])
def login_validation():
    input_email = request.form.get('email').lower()
    input_password = request.form.get('pass')
    filename = 'login_db.csv'
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        for row in data[1:]:
            if row[0] == input_email and row[1] == input_password:
                trial = 'trial_db.csv'
                premium = 'premium_db.csv'
                with open(trial, 'r') as trial, open(premium, 'r') as premium:
                    trial_reader = csv.reader(trial)
                    premium_reader = csv.reader(premium)
                    trial_data = list(trial_reader)
                    premium_data = list(premium_reader)
                    trial_emails = [row[0] for row in trial_data[1:]]
                    premium_emails = [row[0] for row in premium_data[1:]]
                    if int(row[2]) == 1:
                        if input_email in trial_emails or input_email in premium_emails:
                            session['user_id'] = row[0]
                            if input_email in trial_emails:
                                session['sub'] = "Trial"
                            elif input_email in premium_emails:
                                session['sub'] = "Premium"
                            return redirect('/home')
                    else:
                        return login("Your account has been deactivated !!! Please try again later")
        else:
            return login("Wrong credentials !!! Please try again")


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password(message=False):
    return render_template('forgot.html', alert=message)

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email(message=False):
    email = request.form.get('email').lower()
    session['reset_email'] = email
    code = random.randint(1000, 9999)
    session['code'] = code
    body = f"""
    <html>
    <body>
        <h1>Verify Your Email Address</h1>
        <p>Your verification code is: <b>{code}</b> </p>
    </body>
    </html>
    """
    send_email("authorinbox033@gmail.com", "wdctpohewedxteol", email, "Verification Email", body, "smtp.gmail.com", 465)
                    
    return render_template('forgotcode.html', alert=message)

@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    code = request.form.get('code')
    print(code, session['code'])
    if str(code) == str(session['code']):
        return render_template("reset.html")
    else:
        return forgot_password("Wrong Passcode")
    
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    password = request.form.get('newpass')
    filename = 'login_db.csv'
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] != session['reset_email']:
                writer.writerow(row)
            else:
                row[1] = password
                writer.writerow(row)
    session['user_id'] = session['reset_email']
    session.pop('reset_email')
    return main("Password successfully Changed! Please login again using new password")

@app.route('/register', methods=['GET', 'POST'])
def register(message=False):
    if 'user_id' in session:
        return redirect('/')
    else:
        return render_template('sign up.html', alert=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup(message=False):
    if 'user_id' in session:
        return redirect('/')
    else:
        return redirect('/register')
    
@app.route('/register_valid', methods=['GET', 'POST'])
def signup_validation():
    print(1)
    email = request.form.get('email').lower()
    password = request.form.get('pass')
    conpas = request.form.get('conpas')
    filename = 'login_db.csv'
    print(2)
    with open(filename, 'r') as file:
        reader = csv.reader(file) 
        data = list(reader)
        for row in data[1:]:
            print(row)
            if row[0] == email:
                return register("This email is already registered")
        else:
            if password == conpas:
                with open('login_db.csv', 'a', newline='') as file:
                    print(3)
                    writer = csv.writer(file)                    
                    new_row = [email, password, 1]
                    writer.writerow(new_row)
                    session['user_id'] = email
                    print(4)
                    print(session['func'])
                    if session['func'] == "Free Trial":
                        with open('trial_db.csv', 'a', newline='') as trial_file:
                            trial_writer = csv.writer(trial_file)
                            trial_writer.writerow([email, "5"])
                            print(5)
                        with open('journals_db.csv', 'a', newline='') as journal_file:
                            journal_writer = csv.writer(journal_file)
                            journal_writer.writerow([email, "1"])
                            print(6)
                        session['func'] = "Normal"
                        session['sub'] = "Trial"
                    elif session['func'] == "Payment":                        
                        with open('premium_db.csv', 'r') as file:
                            reader = csv.reader(file)
                            data = list(reader)
                            credit_id = int(data[-1][3]) +  1
                        with open('premium_db.csv', 'a', newline='') as premium_file:
                            premium_writer = csv.writer(premium_file)
                            premium_writer.writerow([email, 0, time.strftime('%d/%m/%Y'), credit_id])
                    code = random.randint(1000, 9999)
                    session['code'] = code
                    body = f"""
                    <html>
                    <body>
                        <h1>Verify Your Email Address</h1>
                        <p>Your verification code is: <b>{code}</b> </p>
                    </body>
                    </html>
                    """
                    session['user_id'] = email
                    send_email("authorinbox033@gmail.com", "wdctpohewedxteol", email, "Verification Email", body, "smtp.gmail.com", 465)
                    return render_template('code.html')
            elif password != conpas:
                return register("Passwords do not match")

@app.route('/code_valid', methods=['GET', 'POST'])
def code_valid():
    code = request.form.get('code')
    if str(code) == str(session['code']):
        return home("Congratulations !!! You are successfully registered")

@app.route('/credits', methods=['GET', 'POST'])
def credits(message=False):
    return render_template('credits.html', alert=message)

@app.route('/credit_form', methods=['GET', 'POST'])
def credit_form(message=False):
    credits = request.form.get('credits')
    session['credits'] = credits
    print(credits)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1NSLuLSGFNkJqmhnHogN3s4N',
                    'quantity': int(credits),
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/cred_suc',
            cancel_url=YOUR_DOMAIN + '/cred_fail',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/cred_suc', methods=['GET', 'POST'])
def cred_suc():
    filename = "premium_db.csv"
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        db_id = int(data[-1][3]) +  1
    with open(filename, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)        
        new_row = [session['user_id'], session['credits'], time.strftime('%d/%m/%Y'), db_id]
        writer.writerow(new_row)
    filename = "journals_db.csv"
    with open(filename, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)        
        for row in rows:
            if row[0] != session['user_id']:
                writer.writerow(row)
            else:
                row[1] = int(row[1]) + int(session['credits'])
                writer.writerow(row)
                
    return home("New credits have been purchased")

@app.route('/cred_fail', methods=['GET', 'POST'])
def cred_fail():
    return credits("Payment Failed !!! Please try again")

@app.route('/retrieve/<ret_id>', methods=['GET', 'POST'])
def retrieve(ret_id=None, message=None):
    session['ret_id'] = ret_id
    return render_template('retrieve.html', alert=message)

@app.route('/retrieve_form', methods=['GET', 'POST'])
def retrieve_form():
    method = request.form.get('method')
    if method == 'buy':
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': "price_1NSLuLSGFNkJqmhnHogN3s4N",
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + '/ret_suc',
                cancel_url=YOUR_DOMAIN + '/ret_fail',
            )
        except Exception as e:
            return str(e)
        
        filename = "journals_name.csv"
        with open(filename, 'r') as file:
                    reader = csv.reader(file)
                    rows = list(reader)
        for row in rows:
            if row[1] == session['ret_id']:
                journal_name = row[2]
        body = f"""
        <html>
        <body>
            <h1>Journal Retrieved</h1>
            <p>Your journal {journal_name} has been retrieved by purchasing a new credit</p>
        </body>
        </html>
        """
        send_email("authorinbox033@gmail.com", "wdctpohewedxteol", session['user_id'], "Alert: Journal Retrieved", body, "smtp.gmail.com", 465)
        return redirect(checkout_session.url, code=303)    
    elif method == "use":
        journal_name = ""
        filename = 'premium_db.csv'
        total = 0
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]
        if session['user_id'] in emails:
            for row in data[1:]:
                if row[0] == session['user_id']:
                    total += int(row[1])
        with open('journals_name.csv', 'r') as file:
            for row in data[1:]:
                if row[0] == session['user_id']:
                    total -= 1
        if total > 0:
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(rows.pop(0))
                for row in rows:
                    if row[0] != session['user_id']:
                        writer.writerow(row)
                    else:
                        if int(row[1]) == 0:
                            continue
                        else:
                            row[1] = int(row[1]) - 1
                            writer.writerow(row)
                            for new_row in rows:
                                if new_row[0] != session['user_id'] or new_row[3] != row[3]:
                                    writer.writerow(new_row)
                            break
            filename = "journals_db.csv"
            with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        rows = list(reader)
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)        
                for row in rows:
                    if row[0] != session['user_id']:
                        writer.writerow(row)
                    else:
                        row[1] = int(row[1]) - 1
                        writer.writerow(row)
            filename = "journals_name.csv"
            with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        rows = list(reader)
            for row in rows:
                if row[1] == session['ret_id']:
                    journal_name = row[2]
            body = f"""
            <html>
            <body>
                <h1>Journal Retrieved</h1>
                <p>Your journal {journal_name} has been retrieved by using existing credits</p>
                <p>You have {total} credits left</p>
            </body>
            </html>
            """
            send_email("authorinbox033@gmail.com", "wdctpohewedxteol", session['user_id'], "Alert: Journal Retrieved", body, "smtp.gmail.com", 465)
            return redirect('/ret_suc')
        else:
            return retrieve(message='You do not have enough credits !')


@app.route('/ret_suc', methods=['GET', 'POST'])
def ret_suc():
    filename = "journals_name.csv"
    with open(filename, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] != session['user_id'] or row[1] != session['ret_id']:
                writer.writerow(row)
            else:
                row[8] = time.strftime("%d/%m/%Y")
                writer.writerow(row)
                for temp_row in [new_row for new_row in rows[rows.index(row)+1:]]:
                    writer.writerow(temp_row)
                break

    return home("Journal Retrieved Successfully")

@app.route('/ret_fail', methods=['GET', 'POST'])
def ret_fail():
    return retrieve("Retrieving Failed !!! Please try again")

@app.route('/search', methods=['GET', 'POST'])
def search(message=False, data=False, count=False, filename_prompt=False, total=False, found=False):
    if 'user_id' in session:
        return render_template('search.html', alert=message, data=data, count=count, filename_prompt=filename_prompt, total=total, found=found)
    else:
        return redirect("/")
    
@app.route('/get_count', methods=['GET', 'POST'])
def return_count():
    filename = "trial_db.csv"
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        emails = [row[0] for row in data[1:]]
    if session['user_id'] in emails:
        for row in data[1:]:
            if row[0] == session['user_id']:
                searches = row[1]
        if int(searches) >= 1:
            db = request.form.get('db')
            keyword = request.form.get('keyword')
            from_date = request.form.get('from-date').replace("-", "/")
            to_date = request.form.get('to-date').replace("-", "/")
            session['db'] = db
            session['keyword'] = keyword
            session['from_date'] = from_date
            session['to_date'] = to_date

            with open(filename, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                for row in rows:
                    if row[0] != session['user_id']:
                        writer.writerow(row)
                    else:
                        row[1] = int(row[1]) - 1
                        writer.writerow(row)
            search_count = str(get_count(db,keyword,from_date,to_date))
            return search(message=("Total Records Found - " + search_count), count=search_count) 
        else:
            return search("You do not have any more searches left in your trial")       
    else:
        db = request.form.get('db')
        keyword = request.form.get('keyword')
        from_date = request.form.get('from-date').replace("-", "/")
        to_date = request.form.get('to-date').replace("-", "/")
        session['db'] = db
        session['keyword'] = keyword
        session['from_date'] = from_date
        session['to_date'] = to_date

        search_count = str(get_count(db,keyword,from_date,to_date))
        return search(message=("Total Records Found - " + search_count), count=search_count) 


@app.route('/get_records', methods=['GET', 'POST'])
def return_records():
    try:
        db = session['db']
        keyword = session['keyword'].capitalize()
        from_date = session['from_date']
        to_date = session['to_date']
    except:
        return search("Please Perform A Search First")
    start = int(request.form.get('from-num'))
    count = int(request.form.get('to-num')) - start

    no_of_records = get_count(db, keyword, from_date=from_date, to_date=to_date)

    if str(count).lower() == "all":
        responses = get_records(db, keyword, count=int(no_of_records)+10, start=start, from_date=from_date, to_date=to_date)
    else:
        responses = get_records(db, keyword, count=count, start=start, from_date=from_date, to_date=to_date)
    
    ids = responses[1]
    output = {}
    i = 0
    for record in ids:
        i += 1
        print(i)
        response = get_email(db, record)
        if response != {} and response != None:
            for email, name in response.items():
                output[name] = email
    
    emails = [output, i]

    if emails[0] == {}:
        return search("No emails found in the selcted range")
    else:
        session['data'] = emails
        return search(data=emails[0], filename_prompt=f"{db}-{keyword}-{time.strftime('%d/%m/%Y')}", total=count, found=emails[-1])
    
@app.route('/save_data', methods=['GET', 'POST'])
def save_data():
    db = session['db']
    keyword = session['keyword'].capitalize()
    from_date = session['from_date']
    to_date = session['to_date']
    data_to_save = session['data']
    filename = request.form.get("filename")
    with open('email_names.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        db_id = int(data[-1][1]) +  1
    with open('email_names.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    new_row = [filename, db_id, session['user_id'], time.strftime('%m/%y'), data_to_save[1]]
                    writer.writerow(new_row)
    with open('email_db.csv', 'a', newline ='') as file:
                    writer = csv.writer(file) 
                    for key, value in data_to_save[0].items():     
                        if from_date == "":
                            from_date = "No Input"  
                        if to_date == "":
                            to_date = "No Input"                       
                        new_row = [key, value, db_id, session['user_id'], db, keyword, from_date, to_date]
                        writer.writerow(new_row)
    session.pop('db')
    session.pop('keyword')
    session.pop('from_date')
    session.pop('to_date')
    return search("Data Saved Successfully")

@app.route('/use_data', methods=['GET', 'POST'])
def use_data():
    data_to_use = session['data']
    session['usage_data'] = data_to_use
    return redirect('/recipients')

@app.route('/data', methods=['GET', 'POST'])
def data():
    if 'user_id' in session:
        return render_template('month.html')
    else:
        return redirect("/")
    
@app.route('/data/<month>', methods=['GET', 'POST'])
def month_data(month):
    month_ref = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
    search_key = month_ref[month] + "/23"
    filename = "email_names.csv"
    with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            table = {}
            for row in data[1:]:
                if row[3] == search_key and row[2] == session['user_id']:
                    table[row[1]] = str(row[0]) + " | " + str(row[4])
    return render_template('data.html', data=table)
    
@app.route('/delete/<db_id>', methods=['GET', 'POST'])
def delete(db_id):
    filename = "email_names.csv"
    month = ""

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[1] != db_id:
                writer.writerow(row)
            else:
                month = row[3]
    
    filename = "email_db.csv"
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[2] != db_id:
                writer.writerow(row)

    month_ref = {'01': 'jan', '02': 'feb', '03': 'mar', '04': 'apr', '05': 'may', '06': 'jun', '07': 'jul', '08': 'aug', '09': 'sep', '10': 'oct', '11': 'nov', '12': 'dec'}
    month_name = month_ref[month.split("/")[0]]
    return redirect(f"/data/{month_name}")

@app.route('/listing/<db_id>', methods=['GET', 'POST'])
def listing(db_id):
    session['listing_id'] = db_id
    filename = "email_db.csv"
    with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            table = {}
            for row in data[1:]:
                if row[2] == db_id and row[3] == session['user_id']:
                    print(row[0], row[1])
                    table[row[0]] = row[1]
    print(table)
    return render_template('listing.html', data=table, db_id=db_id)

@app.route('/add_listing_template', methods=['GET', 'POST'])
def add_listing_template():
    return render_template('addlisting.html', db_id=session['listing_id'])

@app.route('/add_listing/<db_id>', methods=['GET', 'POST'])
def add_listing(db_id):
    name = request.form.get('name')
    email = request.form.get('email')
    filename = "email_db.csv"
    details = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        for row in data:
            if row[2] == db_id:
                details = [row[4], row[5], row[6], row[7]]
    with open(filename, 'a', newline="") as file:
        writer = csv.writer(file)
        new_row = [name, email, db_id, session["user_id"]] + details
        writer.writerow(new_row)
    filename = "email_names.csv"
    with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
    with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in data:
                if row[1] == db_id and row[2] == session['user_id']:
                    row[4] = int(row[4]) + 1
                    writer.writerow(row)
                else:
                    writer.writerow(row)
    return redirect(f"/listing/{db_id}")

@app.route('/export_listing/<db_id>', methods=['GET', 'POST'])
def export_listing(db_id):
    export_data = {}
    filename = "email_db.csv"
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        for row in rows:
            if row[2] == db_id and row[3] == session['user_id']:
                export_data[row[0]] = [row[1], row[4], row[5], row[6], row[7]]

    style = xlwt.easyxf('font: bold 1')
    output = io.BytesIO()
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Email Records")
    sheet.write(0, 0, 'Source', style)
    sheet.write(0, 1, 'Keyword', style)    
    sheet.write(0, 2, 'From Date', style)
    sheet.write(0, 3, 'To Date', style)
    sheet.write(0, 4, 'Name', style)
    sheet.write(0, 5, 'Email', style)

    idx = 0
    for key, value in export_data.items():
        sheet.write(idx+1, 0, value[1])
        sheet.write(idx+1, 1, value[2])        
        sheet.write(idx+1, 2, value[3])
        sheet.write(idx+1, 3, value[4])
        sheet.write(idx+1, 4, key)
        sheet.write(idx+1, 5, value[0])
        idx += 1

    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=Email Records.xls"})

@app.route('/delete_listing/<value>', methods=['GET', 'POST'])
def delete_listing(value):
    db_id = session['listing_id']
    filename = "email_db.csv"
    with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
    with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in data:
                if value == f"{row[0]} - {row[1]}" and row[2] == db_id and row[3] == session['user_id']:
                    continue
                else:
                    writer.writerow(row)
    filename = "email_names.csv"
    with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
    with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in data:
                if row[1] == db_id and row[2] == session['user_id']:
                    row[4] = int(row[4]) - 1
                    writer.writerow(row)
                else:
                    writer.writerow(row)
    return redirect(f"/listing/{db_id}")

@app.route('/journals', methods=['GET', 'POST'])
def journals(message=False, journals=False, no_of_jour=False):
    if 'user_id' in session:    
        filename = "journals_db.csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]
        if session['user_id'] in emails:
            for row in data[1:]:
                if row[0] == session['user_id']:
                    filename = "journals_name.csv"
                    with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        data = list(reader)
                        emails = [row[0] for row in data[1:]]
                        no_of_jour = str(emails.count(session['user_id'])) + " / " + row[1]
        filename = "journals_name.csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]
        if session['user_id'] in emails:
            journals = []
            for row in data[1:]:
                if row[0] == session['user_id']:
                    journals.append([row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[1]])
        return render_template('journals.html', alert=message, no_of_jour=no_of_jour, journals=journals)
        '''
        return render_template('journals.html', alert=message, no_of_jour=no_of_jour)
        '''
    else:
        return redirect("/")

@app.route('/add_journal', methods=['GET', 'POST'])
def add_journal():
    filename = "journals_db.csv"
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        emails = [row[0] for row in data[1:]]
    if session['user_id'] in emails:
        for row in data[1:]:
            if row[0] == session['user_id']:
                allowed = int(row[1])
    filename = "journals_name.csv"
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        emails = [row[0] for row in data[1:]]
        done = int(emails.count(session['user_id']))
    if allowed > done:
        filename = "journals_name.csv"
        with open(filename, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
                db_id = int(data[-1][1]) +  1
                print(db_id)
        image = request.files['image']
        if image and allowed_file(image.filename):
            imagename = f"{db_id}.{image.filename.split('.')[-1]}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], imagename))
        journal_name = request.form.get('journal-name')
        issn = request.form.get('issn')
        doi = request.form.get('doi')
        countries = request.form.get('countries')
        start_year = request.form.get('start-year')
        category = request.form.get('category')
        with open("journals_db.csv", 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            ids = [row[0] for row in data[1:]]
        if session['user_id'] in ids:
            with open(filename, 'a', newline="") as file:
                writer = csv.writer(file)
                new_row = [session["user_id"], db_id, journal_name, issn, doi, countries, start_year, category, time.strftime('%d/%m/%Y')]
                writer.writerow(new_row)  
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                print(list(reader))
        return journals(f"Created New \n Journal - {journal_name}")
    else:
        return journals(f"You have already exhausted your credits")

@app.route('/templates', methods=['GET', 'POST'])
def templates(message=False):
    if 'user_id' in session:
        templates = {}
        filename = "journals_name.csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]  
            if session['user_id'] in emails:
                for jour_row in data[1:]:
                    template = []
                    if jour_row[0] == session['user_id']:
                        image_files = os.listdir("./static/journals")
                        for filename in image_files:
                            if filename.startswith(jour_row[1]) and filename.endswith(('.png', '.jpg', '.jpeg')):
                                image = filename.split("/")[-1]
                                templates[jour_row[1]] = [image, jour_row[2]]
                print(templates)
        return render_template('templates.html', alert=message, journals=templates)
    else:
        return redirect("/")
    
@app.route('/view_templates/<journal_id>', methods=['GET', 'POST'])
def view_templates(journal_id):
    filename = "templates_name.csv"
    templates = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        emails = [row[0] for row in rows[1:]]
        if session['user_id'] in emails:
            for row in rows:
                if row[0] == session['user_id'] and row[2] == journal_id:
                    templates[row[3]] = f"{row[1]} | Created on - {row[4]}"
    return render_template("designs.html", templates=templates)

@app.route('/add_template', methods=['GET', 'POST'])
def add_template(prereq=False, editing_option=False):
    filename = "journals_name.csv"
    journals = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        emails = [row[0] for row in rows[1:]]
        if session['user_id'] in emails:
            if prereq:
                for row in rows:
                    if row[0] == session['user_id']:
                        if row[1] != prereq[1]:
                            journals.append([row[2], row[1]])
                        else:
                            prereq.append(row[2])
            else:
                for row in rows:
                    if row[0] == session['user_id']:
                        journals.append([row[2], row[1]])
    if 'template_purpose' not in session or session['template_purpose'] != 'edit':
        session['template_purpose'] = 'add'
    return render_template('create.html', journals=journals, prereq=prereq, editing_option=editing_option)

@app.route('/edit_template/<template_id>', methods=['GET', 'POST'])
def edit_template(template_id):
    prereq = []
    with open("templates_name.csv", 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        emails = [row[0] for row in rows[1:]]
        if session['user_id'] in emails:
            for row in rows:
                if row[0] == session['user_id'] and row[3] == template_id:
                    prereq.append(row[1])
                    prereq.append(row[2])
    with open("templates_db.csv", 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        emails = [row[0] for row in rows[1:]]
        if session['user_id'] in emails:
            for row in rows:
                if row[0] == session['user_id'] and row[1] == template_id:
                    prereq.append(row[-1])
    session['template_purpose'] = 'edit'
    session['template_edit'] = template_id
    return add_template(prereq, editing_option=template_id)

@app.route('/save_template', methods=['GET', 'POST'])
def save_template():
    print(session['template_purpose'])
    journal = request.form.get('journal')
    content = request.form.get('content')
    name = request.form.get('name')
    filename = "templates_name.csv"
    is_existing = False
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        for row in data:
                if row[0] == session['user_id'] and row[1] == name and row[2] == journal:
                    is_existing = True
    if session['template_purpose'] == 'add':
        if not is_existing:
            template_id = int(data[-1][3]) +  1
            with open(filename, 'a', newline="") as file:
                writer = csv.writer(file)
                new_row = [session['user_id'], name, journal, template_id, time.strftime('%d/%m/%Y')]
                writer.writerow(new_row)  
            with open("templates_db.csv", 'a', newline="") as file:
                writer = csv.writer(file)
                new_row = [session['user_id'], template_id, content]
                writer.writerow(new_row) 
            return templates(f"Created New \n Template - {name}")
        else:
            return templates("Template Already Exists With This Name")
    else:
        with open(filename, 'w', newline="") as file:
                writer = csv.writer(file)
                for row in data:
                    print(row)
                    if row[0] != session['user_id'] or row[3] != session['template_edit']:
                        print(1, row)
                        writer.writerow(row)
                    else:
                        row[1] = name
                        row[2] = journal
                        print(2, row)
                        writer.writerow(row)
        with open("templates_db.csv", 'r', newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)
        with open("templates_db.csv", 'w', newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[0] != session['user_id'] or row[1] != session['template_edit']:
                    writer.writerow(row)
                else:
                    row[2] = content
                    writer.writerow(row)
            return templates(f"Changes saved to template - {name}")

@app.route('/edit_template/<template_id>', methods=['GET', 'POST'])
def view_template(template_id):
    if 'user_id' in session:
        filename = "templates_db.csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            emails = [row[0] for row in rows[1:]]
            if session['user_id'] in emails:
                for row in rows:
                    if row[0] == session['user_id'] and row[1] == template_id:
                        template=row[2]
            return render_template('preview.html', content=template)
    else:
        return redirect("/")
    
@app.route('/delete_template/<template_id>', methods=['GET', 'POST'])
def delete_template(template_id):
    if 'user_id' in session:
        jour_id = ""
        with open("templates_name.csv", 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        with open("templates_name.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            for row in rows:
                if row[-1] != template_id:
                    writer.writerow(row)    
                else:
                    jour_id = row[2]                
        with open("templates_db.csv", 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        with open("templates_db.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            for row in rows:
                if row[1] != template_id:
                    writer.writerow(row)            
        return redirect(f"/view_templates/{jour_id}")
    else:
        return redirect("/")

@app.route('/recipients', methods=['GET', 'POST'])
def recipients(message=False):
    if 'user_id' in session:
        journals = []
        with open("journals_name.csv", 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            emails = [row[0] for row in rows[1:]]
            if session['user_id'] in emails:
                for row in rows:
                    if row[0] == session['user_id']:
                        journals.append([row[2], row[1]])
        templates = []
        with open("templates_name.csv", 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            emails = [row[0] for row in rows[1:]]
            if session['user_id'] in emails:
                for row in rows:
                    if row[0] == session['user_id']:
                        templates.append([row[1], row[3]])
        return render_template('recipients.html', alert=message, journals=journals, templates=templates)
    else:
        return redirect("/")
    
@app.route('/preview/', methods=['GET', 'POST'])
def preview():
    if 'user_id' in session:
        template = request.form.get('content')
        session['template'] = template
        return render_template('preview.html', content=template)
    else:
        return redirect("/")

@app.route('/receiver', methods=['GET', 'POST'])
def receiver():
    if 'user_id' in session:
        journal = request.form.get('journal')
        template = request.form.get('template')
        from_email = request.form.get('fromemail')
        from_pass = request.form.get('frompass')
        hosting = request.form.get('hosting')
        port = request.form.get('port')
        subject = request.form.get('subject')
        
        '''
        session['from_email'] = from_email        
        session['from_pass'] = from_pass
        session['hosting'] = hosting
        session['port'] = port
        session['subject'] = subject
        filename = "email_names.csv"
        with open(filename, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
                table = {}
                for row in data[1:]:
                    if row[-2] == session['user_id']:
                        table[row[1]] = row[0]
                return render_template('receiver.html', data=table)
        sender_email = "pandeyrainy2020@gmail.com"
        sender_password = "ohgltbipjxwmvqck"
        recipient_email = "pandeyrainy2020@gmail.com,lhl260521@gmail.com"
        subject = "Hello from Python Email"
        body = """
        <html>
        <body>
            <p>This is an <b>HTML</b> email sent for Krishanu Karmakar.</p>
        </body>
        </html>
        """
        html_message = MIMEText(body, 'html')
        html_message['Subject'] = subject
        html_message['From'] = sender_email
        html_message['To'] = recipient_email

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        '''
        try:
            send_email(from_email, from_pass, "authorinbox033@gmail.com", subject, "Testing", hosting, port)
        except Exception as e:
            return recipients("Invalid Credentials !!!")
        else:
            session['journal'] = journal
            session['template'] = template
            session['from_email'] = from_email        
            session['from_pass'] = from_pass
            session['hosting'] = hosting
            session['port'] = port
            session['subject'] = subject
            filename = "email_names.csv"
            with open(filename, 'r') as file:
                    reader = csv.reader(file)
                    data = list(reader)
                    table = {}
                    for row in data[1:]:
                        if row[2] == session['user_id']:
                            table[row[1]] = str(row[0]) + " | " + str(row[4])
                    if 'usage_data' in session:
                        return render_template('publish.html')
                    else:
                        return render_template('receiver.html', data=table)
    else:
        return redirect("/")
    
@app.route('/receiver/<db_id>', methods=['GET', 'POST'])
def receiver_data(db_id):
    if 'user_id' in session:
        session['db_id'] = db_id
        return render_template('publish.html')
    else:
        return redirect("/")
     
def send_email(from_email, from_pass, to_email, subject, body, hosting, port):
        
    import smtplib
    from email.mime.text import MIMEText

    sender_email = from_email
    sender_password = from_pass
    recipient_email = to_email
    subject = subject
    body = f"""
    <html>
    <body>
        {body}
    </body>
    </html>
    """
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = recipient_email

    server = smtplib.SMTP_SSL(hosting, port)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, html_message.as_string())
    server.quit()

@app.route('/test', methods=['GET', 'POST'])
def test():
    if 'user_id' in session:      
        test_name = request.form.get('testname')
        test_email = request.form.get('testemail')
        content = session['template'].replace(r"{name}", test_name)
        send_email(session['from_email'], session['from_pass'], test_email, session['subject'], content, session['hosting'], session['port'])
        return render_template('publish.html', alert=f"Sent Test Message To {test_name} on {test_email}")
    else:
        return redirect("/")

def publish_send(total, uid, dbid, temp, frome, fromp, sub, hos, port):
    if isinstance(dbid, dict):
        print(dbid)
        for name, email in dbid:
            content = temp.replace(r"{name}", name)
            send_email(frome, fromp, email, sub, content, hos, port)
            with open("count.txt", "r") as file:
                progress = file.read()
                if progress == "" or str(progress)[0] == "0":
                    progress = f"0 / {total}"
            with open("count.txt", "w") as file:
                if str(progress).split(" / ")[0] == str(progress).split(" / ")[-1]:
                    file.write("All Done!")
                else:
                    file.write(str(int(progress.split(" / ")[0]) + 1) + " / " + str(total))
    else:
        filename = 'email_db.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            for row in data:
                if row[3] == uid and row[2] == dbid:
                    content = temp.replace(r"{name}", row[0])
                    send_email(frome, fromp, row[1], sub, content, hos, port)
                    with open("count.txt", "r") as file:
                        progress = file.read()
                        if progress == "" or str(progress)[0] == "0":
                            progress = f"0 / {total}"
                    with open("count.txt", "w") as file:
                        if str(progress).split(" / ")[0] == str(progress).split(" / ")[-1]:
                            file.write("All Done!")
                        else:
                            file.write(str(int(progress.split(" / ")[0]) + 1) + " / " + str(total))
    with open("count.txt", "r") as file:
        progress = file.read()
    if str(progress).split(" / ")[0] == str(progress).split(" / ")[-1]:
        with open("count.txt", "w") as file:
            pass

@app.route('/publish', methods=['GET', 'POST'])
def publish():
    if 'user_id' in session:
        if 'usage_data' in session:
            data = session['usage_data']
            threading.Thread(target=publish_send, args=[len(data), session['user_id'], data, session['template'], session['from_email'], session['from_pass'], session['subject'], session['hosting'], session['port']]).start()
        else:
            filename = 'email_db.csv'
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
                total_rows = 0
                for row in data:
                    if row[2] == session['db_id']:
                        total_rows += 1
                threading.Thread(target=publish_send, args=[total_rows, session['user_id'], session['db_id'], session['template'], session['from_email'], session['from_pass'], session['subject'], session['hosting'], session['port']]).start()
        return render_template('publishprog.html')
    else:
        return redirect("/")

@app.context_processor
def publish_inject_load():
    with open("count.txt", "r") as file:
        return {'prog1': file.read()}    

@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()

def update_load():
    with app.app_context():
        while True:
            time.sleep(1)
            turbo.push(turbo.replace(render_template('publishsnip.html'), 'prog'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect("/")

# --------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin(message=False):
    if 'admin_id' in session:
        return render_template('admin.html')
    else:
        return render_template('adminlogin.html', alert=message)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    input_email = request.form.get('email').lower()
    input_password = request.form.get('pass')
    filename = 'admin_login.csv'
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        for row in data[1:]:
            if row[0] == input_email and row[1] == input_password:
                session['admin_id'] = row[0]
                return redirect('/admin')
        else:
            return admin("Wrong credentials !!! Please try again")

@app.route('/admin_users', methods=['GET', 'POST'])
def admin_users(message=False):
    if 'admin_id' in session:
        premium_users = {}
        filename = 'premium_db.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            for row in rows[1:]:
                if row[0] in premium_users:
                    premium_users[row[0]]['Credits'] += int(row[1])
                else:
                    premium_users[row[0]] = {'Credits': int(row[1])}

        for key in premium_users.keys():
            value = premium_users[key]
            value['Payment Done'] = int(value['Credits']) * 1000

        filename = 'journals_name.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            journals = {}
            for row in rows[1:]:
                if row[0] in journals:
                    journals[row[0]] += 1
                else:
                    journals[row[0]] = 1

        for key in premium_users.keys():
            value = premium_users[key]
            if key in journals:
                value['Journals'] = int(journals[key])
                value['Credits'] -= int(journals[key])
            else:
                value['Journals'] = 0

        trial_users = {}
        filename = 'trial_db.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            for row in rows[1:]:
                trial_users[row[0]] = row[1]
                
        return render_template('adminusers.html', premium_users=premium_users, trial_users=trial_users)
    else:
        return redirect('/admin')

@app.route('/admin_premium', methods=['GET', 'POST'])
def admin_premium(message=False):
    if 'admin_id' in session:
        premium = {}
        filename = 'premium_db.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            for row in rows[1:]:
                premium[row[0]] = row[0]
        return render_template('adminpremium.html', premium=premium)
    else:
        return redirect('/admin')
    

@app.route('/admin_premium_user/<user_id>', methods=['GET', 'POST'])
def admin_premium_user(user_id, message=False):
    if 'admin_id' in session:
        filename = "journals_db.csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]
        no_of_jour = 0
        if user_id in emails:
            for row in data[1:]:
                if row[0] == user_id:
                    filename = "journals_name.csv"
                    with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        data = list(reader)
                        emails = [row[0] for row in data[1:]]
                        no_of_jour = int(emails.count(user_id))
        filename = "premium_db.csv"
        credits = {}
        with open(filename, 'r') as file:
                        reader = csv.reader(file)
                        rows = list(reader)
                        for row in rows:
                            if row[0] == user_id:
                                date_struct = time.strptime(row[2], '%d/%m/%Y')
                                timestamp = time.mktime(date_struct)
                                new_timestamp = timestamp + 30 * 24 * 60 * 60
                                new_date_struct = time.localtime(new_timestamp)
                                new_date_str = time.strftime('%d/%m/%Y', new_date_struct)
                                credits[row[3]] = [row[1], new_date_str]
        for key, value in credits.items():
            credits[key] = [value[0], time.strptime(value[1], '%d/%m/%Y')]                      
        sorted_credits = dict(sorted(credits.items(), key=lambda item: item[1][1]))
        for key, value in sorted_credits.items():
            sorted_credits[key] = [value[0], time.strftime('%d/%m/%Y', value[1])]
        sorted_credits = [[key, [int(value[0]), value[1]]] for key, value in sorted_credits.items()]
        print(sorted_credits)
        credits = {}
        for credit in sorted_credits:
            if no_of_jour > credit[1][0]:
                no_of_jour -= credit[1][0]
            elif no_of_jour == credit[1][0]:
                for left_credit in sorted_credits[sorted_credits.index(credit)+1:]:
                    credits[left_credit[0]] = left_credit[1]
                break
            else:
                credit[1][0] -= no_of_jour
                credits[credit[0]] = [credit[1][0], credit[1][1]]
                for item in sorted_credits[sorted_credits.index(credit):]:
                    credits[item[0]] = item[1]
                break
        graces = {}
        with open("journals_name.csv", 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]
            if user_id in emails:
                for row in data[1:]:
                    date_struct = time.strptime(row[8], '%d/%m/%Y')
                    timestamp = time.mktime(date_struct)
                    new_timestamp = timestamp + 30 * 24 * 60 * 60
                    new_date_struct = time.localtime(new_timestamp)
                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)                                
                    exp_time = time.strptime(new_date_str, '%d/%m/%Y')
                    new_timestamp = timestamp + 45 * 24 * 60 * 60
                    new_date_struct = time.localtime(new_timestamp)
                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)
                    grc_time = time.strptime(new_date_str, '%d/%m/%Y')
                    if exp_time < time.gmtime() and time.gmtime() < grc_time:
                        graces[row[1]] = [row[2], new_date_str]
        journals = {}
        with open("journals_name.csv", 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]
            if user_id in emails:
                for row in data[1:]:
                    date_struct = time.strptime(row[8], '%d/%m/%Y')
                    timestamp = time.mktime(date_struct)
                    new_timestamp = timestamp + 30 * 24 * 60 * 60
                    new_date_struct = time.localtime(new_timestamp)
                    new_date_str = time.strftime('%d/%m/%Y', new_date_struct)                                
                    exp_time = time.strptime(new_date_str, '%d/%m/%Y')
                    if time.gmtime() < exp_time and row[1] not in graces:
                        journals[row[1]] = [row[2], new_date_str]
        filename = "journals_name.csv"
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            emails = [row[0] for row in data[1:]]
            total_journals = int(emails.count(user_id))
        return render_template('adminpremiumuser.html', alert=message, premium_user=True, total_journals=total_journals, journals=journals, graces=graces, credits=credits)
    else:
        return redirect('/admin')

@app.route('/admin_activate', methods=['GET', 'POST'])
def admin_activate(message=False):
    if 'admin_id' in session:
        return render_template('adminactivate.html', alert=message)
    else:
        return redirect('/admin')
        
@app.route('/admin_enable', methods=['GET', 'POST'])
def admin_enable():
    if 'admin_id' in session:
        email = request.form.get('email')
        filename = 'login_db.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file) 
            data = list(reader)
            for row in data[1:]:
                if row[0] == email and int(row[2]) == 1:
                    return admin_activate("This email is already enabled")
            else:
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)        
                    for row in data:
                        if row[0] != email:
                            writer.writerow(row)
                        else:
                            row[2] = 1
                            writer.writerow(row)
                return admin_activate(f"Enabled {email}")
    else:
        return redirect('/admin')
    
@app.route('/admin_disable', methods=['GET', 'POST'])
def admin_disable():
    if 'admin_id' in session:
        email = request.form.get('email')
        filename = 'login_db.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file) 
            data = list(reader)
            for row in data[1:]:
                if row[0] == email and int(row[2]) == 0:
                    return admin_activate("This email is already disabled")
            else:
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)        
                    for row in data:
                        if row[0] != email:
                            writer.writerow(row)
                        else:
                            row[2] = 0
                            writer.writerow(row)
                return admin_activate(f"Disabled {email}")
    else:
        return redirect('/admin')
    
@app.route('/admin_responses', methods=['GET', 'POST'])
def admin_responses(message=False):
    if 'admin_id' in session:
        responses = {}
        filename = 'adv_form.csv'
        with open(filename, 'r') as file:
                    reader = csv.reader(file)
                    rows = list(reader)
        for row in rows[1:]:
            responses[row[3] + row[2] + row[1] + row[0]] = [row[0], row[1], row[2], row[3]]
        return render_template('adminresponses.html', responses=responses)
    else:
        return redirect('/admin')    

@app.route('/admin_access', methods=['GET', 'POST'])
def admin_access(message=False):
    if 'admin_id' in session:
        return render_template('adminaccess.html', alert=message)
    else:
        return redirect('/admin')

@app.route('/admin_add_access', methods=['GET', 'POST'])
def admin_add_access():
    if 'admin_id' in session:
        email = request.form.get('email').lower()
        password = request.form.get('pass')
        filename = 'admin_login.csv'
        with open(filename, 'r') as file:
            reader = csv.reader(file) 
            data = list(reader)
            for row in data[1:]:
                if row[0] == email:
                    return admin_access("This email is already registered")
                else:
                    with open(filename, 'a', newline='') as file:
                        writer = csv.writer(file)                  
                        new_row = [email, password]
                        writer.writerow(new_row)
                    return admin_access(f"Successfully gave access of admin panel to {email}")
    else:
        return redirect('/admin')

@app.route('/admin_logout', methods=['GET', 'POST'])
def admin_logout():
    if 'admin_id' in session:
        session.pop('admin_id')
    return redirect("/admin")

if __name__ == '__main__':
    app.run(debug=True, port=1250)

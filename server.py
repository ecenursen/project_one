from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from forms import AddressForm
import pyrebase
from dbinit import db, auth
from firebase import firebase
from bitcoin_func import *


app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY'] = '9ioJbIGGH6ndzWOi3vEW'

# Home page route
@app.route("/" ,methods=["GET","POST"])
def home_page():
    return render_template("home.html")


# Route to Register(Sign up) page
@app.route('/register/')
def register():
    return render_template("register_page.html")

# Route to Login Page
@app.route('/login')
def login():
    return render_template("login_page.html")

# Route to Wallet Information Page
@app.route('/mywallet',methods=['GET'])
def wallet_info():
    # Getting the balance info
    balance_answer = RPC_GetBalance()
    if balance_answer['RESPONSE'] == 'SUCCESS':
        curr_balance = float(balance_answer['RESULT'])
        curr_balance = '{:20f}'.format(curr_balance)
    else:
        print("Balance Error: ", balance_answer['ERROR'])

    return render_template("wallet_info.html",balance=curr_balance,username=session["username"],addr=session["address"])

# Route to My Transactions Page
@app.route('/mytrans',methods=['GET'])
def trans_history():
    # Obtaining the User's transaction data by the "address" parameter
    trans_answer = GetUserTransactions(session['address'])
    if trans_answer['RESPONSE'] == 'SUCCESS':
        transes = trans_answer['RESULT']
    else:
        print("Recent Block Error: ", trans_answer['ERROR'])
    
    return render_template("mytransaction_page.html",username=session["username"],transactions=transes[::-1])

# Route to Recent Blocks Page
@app.route('/recentblocks',methods=['GET'])
def recent_blocks():
    # Getting the latest 100 Blocks Data
    block_answer = Get_Recent_Blocks(100)
    if block_answer['RESPONSE'] == 'SUCCESS':
        blocks = block_answer['RESULT']
    else:
        print("Recent Block Error: ", block_answer['ERROR'])
    return render_template("recent_blocks.html",blocks=blocks)

# Route to Make New Transaction Page 
@app.route('/maketrans',methods=['GET','POST'])
def make_trans():
    # Getting the neccessary parameters from HTML form
    result = request.form
    if request.method == "POST":
        # Receiver Address
        receiverAddress= result["address"]
        # Logged in User Address
        address = session["address"]
        # Transaction Amount
        sendValue = float(result["sendvalue"])
        # Transaction Fee
        fee = float(result["fee"])
        # Minimum fee value can be 0.00001
        if fee < 0.00001:
            fee = 0.00001
        # if the User does not enter the transaction fee
        if(fee != 0.0):
            # Calling the Make Transaction function
            newTransAnswer = MakeTrans(address,receiverAddress,sendValue,fee)
        else:
            # Calling the Make Transaction function
            newTransAnswer = MakeTrans(address,receiverAddress,sendValue)
        if newTransAnswer['RESPONSE'] == 'SUCCESS':
            print("Transaction is Successfull")
            print("txid:",newTransAnswer['RESULT'])
            return redirect(url_for('home_page'))
        else:
            print(newTransAnswer['ERROR'])
            return redirect(url_for('make_trans'))
    # To show the balance info in Make transaction page
    balance_answer = RPC_GetBalance()
    if balance_answer['RESPONSE'] == 'SUCCESS':
        curr_balance = balance_answer['RESULT']
        curr_balance = '{:20f}'.format(curr_balance)
    else:
        print("Balance Error: ", balance_answer['ERROR'])

    return render_template("create_transaction.html",balance=curr_balance,username=session["username"])

# Submit the register form
@app.route('/registersubmit', methods=['GET', 'POST'])
def register_submit():
    # Getting the user credentials from HTML page form
    result = request.form
    if request.method == "POST":
        username = result["username"]
        password = result["psw"]
        name = result["name"]

        # Creating the new wallet for new user
        wallet_answer = CreateWallet("Wallet"+username)
        if wallet_answer['RESPONSE'] == 'SUCCESS':
            # Getting the address for the new wallet
            address_answer = GetAddressofWallet()
            if address_answer['RESPONSE'] == 'SUCCESS':
                # Getting the Private Key of the Address
                privkey_answer = GetPrivKey(address_answer['RESULT'])
                if privkey_answer['RESPONSE'] == 'SUCCESS':
                    try:
                        # Storing the new user in database
                        if(db.child("users").child(username).get().val() == None):
                            db.child("users").child(username).set({"Name": name, "Username": username, "Password": password, "Address":address_answer['RESULT'], "Wallet Name":("Wallet"+username), "Private Key":privkey_answer['RESULT']})
                            # Changing the session parameters
                            session["logged_in"] = True
                            session["username"] = username
                            session["name"] = name
                            session["address"] = address_answer['RESULT']
                            session["walletname"] = "Wallet" + username
                            session['logged_in'] = True
                            # Finally Redirect to Home Page
                            return redirect(url_for('home_page'))
                        else:
                            flash('The username exists, please try another one', 'danger')
                    except:
                        return redirect(url_for('register'))
                else:
                    print(privkey_answer['ERROR'])
            else:
                print(address_answer['ERROR'])
        else:
            print(wallet_answer['ERROR'])
    else:
        if session["logged_in"] == True:
            return redirect(url_for('home_page'))
        else:
            return redirect(url_for('register'))

# Submit the login form
@app.route('/loginsubmit', methods=['GET', 'POST'])
def login_submit():
    # Getting the user credentials from HTML page form
    result = request.form
    if request.method == "POST":
        username = result["username"]
        password = result["psw"]
        try:
            # Checking the user exist in database or not
            if(db.child("users").child(username).get().val() == None):
                flash('Login Unsuccessful. Please check username and password', 'danger')
                return redirect(url_for('login'))
            # Checking Password    
            else:
                if(db.child("users").child(username).get().val()["Password"] != password):
                    flash('Login Unsuccessful. Please check username and password', 'danger')
                    return redirect(url_for('login'))
                else:
                    # Changing the session parameters
                    session["logged_in"] = True
                    session["username"] = db.child("users").child(username).get().val()["Username"]
                    session["name"] = db.child("users").child(username).get().val()["Name"]
                    session["address"] = db.child("users").child(username).get().val()["Address"]
                    session["pvkey"] = db.child("users").child(username).get().val()["Private Key"]
                    session["walletname"] = db.child("users").child(username).get().val()["Wallet Name"] 
                    # Loading the wallet to system
                    wallet_answer = LoadWallet(session['walletname'])
                    if wallet_answer['RESPONSE'] != 'SUCCESS':
                        print("Login Error: ",wallet_answer['ERROR'])
                    # Redirect to Home Page after logged in
                    return redirect(url_for('home_page'))
        except:
            return redirect(url_for('login'))
    else:
        if session["logged_in"] == True:
            return redirect(url_for('home_page'))
        else:
            return redirect(url_for('login'))


# Logout Function
@app.route('/logout')
def logout():
    # Unloading the wallet from system
    wallet_answer = UnloadWallet(session['walletname'])
    if wallet_answer['RESPONSE'] != 'SUCCESS':
        print("Logout Error: ",wallet_answer['ERROR'])
    session['logged_in'] = None
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(debug=True)

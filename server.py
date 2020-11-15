from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from forms import AddressForm
import requests
import pyrebase
from dbinit import db, auth
from firebase import firebase
from bitcoin_func import LoadWallet,UnloadWallet,CreateWallet,GetAddressofWallet,GetPrivKey,RPC_GetBalance

person = {"logged_in": False, "name": "", "username": "", "password": "", "address":"", "private key":"" }

"""
db.child("User").child("Name").set("Joshgun")
db.child("User").child("Surname").set("Rzabayli")
db.child("User").child("ID").set("1")
db.child("User").child("Name").set("Joshgun")
db.child("User").child("Surname").set("Rzabayli")
db.child("User").child("ID").set("2")
db.child("User").push(data)
"""




app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY'] = '9ioJbIGGH6ndzWOi3vEW'
url_regtest = "http://127.0.0.1:18332/"
auth_regtest = ('admin','admin')

# Home page route
@app.route("/" ,methods=["GET","POST"])
def home_page():
    return render_template("home.html")


# Get address route
@app.route("/getaddr/" ,methods=["GET","POST"])
def getaddr_page():
    if request.method =='POST':
        print("POST")
        req = request.form
        print(req)
        dictToSend = {"jsonrpc": "1.0", "id":"curltest", "method": "getnewaddress", "params": [] }
        res = requests.post(url_regtest, json=dictToSend,auth=auth_regtest)
        print("res:",res.json()['result'])
        newaddress = res.json()['result']
        print("addr:",newaddress)
        return redirect(url_for("getaddr_page",newaddr=newaddress))
    elif request.method == 'GET':
        newaddress = request.args['newaddr']
        print("get")
    return render_template("getaddress.html",newaddr=newaddress)

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
    balance_answer = RPC_GetBalance()
    if balance_answer['RESPONSE'] == 'SUCCESS':
        curr_balance = balance_answer['RESULT']
    else:
        print("Balance Error: ", balance_answer['ERROR'])

    return render_template("wallet_info.html",balance=curr_balance,username=session["username"],addr=session["address"])

@app.route('/mytrans',methods=['GET'])
def trans_history():
    return render_template("mytransaction_page.html",username=session["username"])

@app.route('/maketrans',methods=['GET','POST'])
def make_trans():
    balance_answer = RPC_GetBalance()
    if balance_answer['RESPONSE'] == 'SUCCESS':
        curr_balance = balance_answer['RESULT']
    else:
        print("Balance Error: ", balance_answer['ERROR'])

    return render_template("create_transaction.html",balance=curr_balance,username=session["username"])

# Submit the register form
@app.route('/registersubmit', methods=['GET', 'POST'])
def register_submit():
    result = request.form
    if request.method == "POST":
        username = result["username"]
        password = result["psw"]
        name = result["name"]

        wallet_answer = CreateWallet("Wallet"+username)
        if wallet_answer['RESPONSE'] == 'SUCCESS':
            address_answer = GetAddressofWallet()
            if address_answer['RESPONSE'] == 'SUCCESS':
                privkey_answer = GetPrivKey(address_answer['RESULT'])
                if privkey_answer['RESPONSE'] == 'SUCCESS':
                    try:
                        if(db.child("users").child(username).get().val() == None):
                            db.child("users").child(username).set({"Name": name, "Username": username, "Password": password, "Address":address_answer['RESULT'], "Wallet Name":("Wallet"+username), "Private Key":privkey_answer['RESULT']})
                            session["logged_in"] = True
                            session["username"] = username
                            session["name"] = name
                            session["address"] = address_answer['RESULT']
                            session["walletname"] = "Wallet" + username
                            print(session)
            # address
            # wallet name
            # private key
                            session['logged_in'] = True
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

@app.route('/loginsubmit', methods=['GET', 'POST'])
def login_submit():
    result = request.form
    if request.method == "POST":
        username = result["username"]
        password = result["psw"]
        try:
            if(db.child("users").child(username).get().val() == None):
                flash('Login Unsuccessful. Please check username and password', 'danger')
                return redirect(url_for('login'))
            else:
                if(db.child("users").child(username).get().val()["Password"] != password):
                    flash('Login Unsuccessful. Please check username and password', 'danger')
                    return redirect(url_for('login'))
                else:
                    
                    session["logged_in"] = True
                    print("PASSED1")
                    session["username"] = db.child("users").child(username).get().val()["Username"]
                    print("PASSED2")
                    session["name"] = db.child("users").child(username).get().val()["Name"]
                    print("PASSED3")
                    session["address"] = db.child("users").child(username).get().val()["Address"]
                    print("PASSED4")
                    session["pvkey"] = db.child("users").child(username).get().val()["Private Key"]
                    print("PASSED5")
                    session["walletname"] = db.child("users").child(username).get().val()["Wallet Name"]
                    print("PASSED6")
                    print(session)   
                    wallet_answer = LoadWallet(session['walletname'])
                    if wallet_answer['RESPONSE'] != 'SUCCESS':
                        print("Login Error: ",wallet_answer['ERROR'])
                    return redirect(url_for('home_page'))
        except:
            return redirect(url_for('login'))
    else:
        if session["logged_in"] == True:
            return redirect(url_for('home_page'))
        else:
            return redirect(url_for('login'))


# Route to Login Page
@app.route('/logout')
def logout():
    wallet_answer = UnloadWallet(session['walletname'])
    if wallet_answer['RESPONSE'] != 'SUCCESS':
        print("Logout Error: ",wallet_answer['ERROR'])
    session['logged_in'] = None
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(debug=False)

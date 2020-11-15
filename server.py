from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from forms import AddressForm
import requests
import pyrebase
from dbinit import db, auth
from firebase import firebase


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

# Submit the register form
@app.route('/registersubmit', methods=['GET', 'POST'])
def register_submit():
    result = request.form
    if request.method == "POST":
        username = result["username"]
        password = result["psw"]
        name = result["name"]

        # Creating the address for new user
        getAddress = {"jsonrpc": "1.0", "id": "curltest",
                      "method": "getnewaddress", "params": []}
        resAddress = requests.post(url_regtest, json=getAddress, auth=auth_regtest)
        address = resAddress.json()["result"]
        
        # Getting the private key value from the address
        getPVKey = {"jsonrpc": "1.0", "id": "curltest",
                    "method": "dumpprivkey", "params": [address]}
        resPVKey = requests.post(url_regtest, json=getPVKey, auth=auth_regtest)
        PVKey = resPVKey.json()["result"]
        try:
            if(db.child("users").child(username).get().val() == None):
                db.child("users").child(username).set({"Name": name, "Username": username, "Password": password, "Address":address, "Wallet Name":("Wallet"+username), "Private Key":PVKey})
                session["logged_in"] = True
                session["username"] = username
                session["name"] = name
                session["address"] = address
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
    session['logged_in'] = None
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(debug=False)

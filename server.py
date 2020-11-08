from flask import Flask,render_template,request,redirect,url_for
from forms import AddressForm
import requests

app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY'] = '9ioJbIGGH6ndzWOi3vEW'
url_regtest = "http://127.0.0.1:18443/"
auth_regtest = ('admin','admin')

@app.route("/" ,methods=["GET","POST"])
def home_page():
    return render_template("home.html")

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

if __name__ == "__main__":
    app.run()

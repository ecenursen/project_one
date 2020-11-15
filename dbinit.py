import os
import sys
import pyrebase

import psycopg2 as dbapi2

config = {
    "apiKey": "AIzaSyAbQjYAiLubHRMON09IPX1VSvTxfaWQSss",
    "authDomain": "walletapp-b5157.firebaseapp.com",
    "databaseURL": "https://walletapp-b5157.firebaseio.com",
    "projectId": "walletapp-b5157",
    "storageBucket": "walletapp-b5157.appspot.com",
    "messagingSenderId": "1054776162478",
    "appId": "1:1054776162478:web:a4e86381f4cd38c9f9153f",
    "measurementId": "G-F2MX2V2KYH"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

db = firebase.database()


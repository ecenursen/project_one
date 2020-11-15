import requests
from datetime import datetime

# some configurations
url_regtest = "http://127.0.0.1:18443/"
url_testnet = "http://127.0.0.1:18332/"
curr_auth= ('admin','admin')

curr_url = url_testnet

# FOR EVERY FUNCTION STRUCTURE GOES LIKE THIS
#
# IF FUNCTION COMPLETED WITH SUCCESS
# { "RESPONSE": "SUCCESS" , "RESULT": "result of the function"}
#
# IF FUNCTION COULDN'T COMPLETED DO TO ERROR
# { "RESPONSE": "ERROR" , "ERROR": "error message"}

#function for creating RPC request structure
def Create_RPC_dict(RPC_method, RPC_params=[]):
    return {"jsonrpc": "1.0", "id":"curltest", "method": RPC_method, "params": RPC_params }

#function for loading wallet
def LoadWallet(walletname):
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("loadwallet",[walletname]),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return{"RESPONSE": "SUCCESS", "RESULT": "Wallet successfully loaded"}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]["message"]}

#function for unloading wallet
def UnloadWallet(walletname):
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("unloadwallet",[walletname]),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return {"RESPONSE": "SUCCESS", "RESULT": "Wallet successfully unloaded"}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]["message"]}

#function fro creating wallet
def CreateWallet(walletname):
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("createwallet",[walletname]),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return {"RESPONSE": "SUCCESS", "RESULT": "Wallet successfully created"}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]["message"]}

#function for creating a new address for wallet
def GetAddressofWallet():
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("getnewaddress"),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return {"RESPONSE": "SUCCESS", "RESULT":RPC_response["result"]}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}

#function for getting private key of address
def GetPrivKey(user_addr):
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("dumpprivkey",[user_addr]),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return {"RESPONSE": "SUCCESS", "RESULT":RPC_response["result"]}
    else:
        return {"RESPONSE": "ERROR","ERROR":RPC_response["error"]}

#function for getting the balance of the wallet
def RPC_GetBalance():
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("getbalance"),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return {"RESPONSE": "SUCCESS", "RESULT":RPC_response["result"]}
    else:
        return {"RESPONSE": "ERROR","ERROR": "Can't reach balance"}

#function for getting unspent transactions
def ListUnspent():
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("listunspent"),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return {"RESPONSE": "SUCCESS", "RESULT":RPC_response["result"]}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}

#function for sending signed raw transaction
def SendRawTransaction(signedhex):
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("sendrawtransaction",[signedhex]),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return {"RESPONSE": "SUCCESS", "RESULT":RPC_response["result"]}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}

#function for sending signed raw transaction
def SignRawTransaction(transhex):
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("signrawtransactionwithwallet",[transhex]),auth=curr_auth).json()
    if RPC_response["error"]==None:
        return SendRawTransaction(RPC_response["result"]["hex"])
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}

#function for creating raw transaction
def RPC_CreateRawTransaction(sendaddr,sendvalue,myaddr=0,returnvalue=0):
    list_unspent = ListUnspent() #get unspent amounts
    if list_unspent["RESPONSE"] != "ERROR": # if any problems reaching unspent values
        input_trans = list_unspent["RESULT"]
        output_trans = {}
        output_trans[sendaddr] = sendvalue
        if myaddr != 0 :
            output_trans[myaddr] = returnvalue
        params = []
        params.append(input_trans)
        params.append(output_trans)
        RPC_response = requests.post(curr_url, json=Create_RPC_dict("createrawtransaction",params),auth=curr_auth).json()
        if RPC_response["error"]==None: 
            return SignRawTransaction(RPC_response["result"])
        else:
            return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}
    else :
        return list_unspent["ERROR"]  

#function to Make Transaction
#returns the transaction id of newly created transaction if successfull
def MakeTrans(myaddr,sendaddr,sendvalue,fee=0):
    curr_balance = RPC_GetBalance()
    returnval = 0
    if curr_balance['RESPONSE'] != "ERROR": # for checking whether getbalance function has any problems
        curr_balance = curr_balance['RESULT']
        if curr_balance >= (sendvalue+fee) or curr_balance >= sendvalue: # to check whether balance is sufficient or not
            if curr_balance >= (sendvalue+fee): # to check whether send value + fee is sufficient, if not change fee accordingly
                returnval = curr_balance - (sendvalue+fee)
            else:
                returnval = curr_balance - sendvalue
            returnval = float("{:.10f}".format(returnval)) # to have float which has 10 number after point
            return RPC_CreateRawTransaction(sendaddr,sendvalue,myaddr,returnval)
        else:
            return {"RESPONSE": "ERROR","ERROR": "Balance is insufficient"}
    else: 
        return curr_balance

#function that returns n Recent Blocks, n is spesify by "count"
#Successful return gives this the structure below
# [
#   { 'hash' : "Hash of block",
#     'confirmations' : "total number of confirmation it gets",
#     'validity' : "Validity of block",
#     'time' : "Time of block constructed",
#     'trans_no' : "Total number of transaction it contains"
#   }, .... ,{}
# ]
def Get_Recent_Blocks(count):
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("getbestblockhash"),auth=curr_auth).json()
    blocks = []
    if RPC_response["error"]==None:
        block_hash = RPC_response['result']
        for i in range(count):
            RPC_response = requests.post(curr_url, json=Create_RPC_dict("getblock",[block_hash]),auth=curr_auth).json()
            if RPC_response["error"]==None:
                current_block = RPC_response['result']
                block_info = {}
                block_info['hash'] = current_block['hash']
                block_info['confirmations'] = current_block['confirmations']
                #to check validity of the block
                if block_info['confirmations']>=6 : #if block is confirmed more than 5 times, block is valid
                    block_info['validity'] = "Valid Block"
                else: 
                    block_info['validity'] = "Validity Waiting"
                block_info['time'] = datetime.utcfromtimestamp(current_block['time']).strftime('%Y-%m-%d %H:%M:%S')
                block_info['trans_no'] = current_block['nTx']
                block_hash = current_block['previousblockhash']
                blocks.append(block_info)
            else:
                return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}
        return {"RESPONSE": "SUCCESS", "RESULT": blocks}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}


#function for listing all transactions made from wallet
#Successful return gives this the structure below
# [
#   { 
#     'trans_id' : "transaction id"
#     'status': "either receive or sent"
#     'amount' : "amount that sent",
#     'confirmations' : "total number of confirmation it gets",
#     'validity' : "Validity of block that transaction is in",
#     'time' : "Time of block that transaction is in constructed",
#     'block' : "Hash of block that transaction is in"
#   }, .... ,{}
# ]
def GetUserTransactions(user_addr):
    usr_transactions = []
    RPC_response = requests.post(curr_url, json=Create_RPC_dict("listtransactions"),auth=curr_auth).json()
    if RPC_response["error"]==None:
        for trans in RPC_response["result"]:
            temp_trans = {}
            temp_trans['trans_id'] = trans['txid']
            temp_trans['status'] = trans['category'] 
            temp_trans['amount'] = '{:20f}'.format(trans['amount'])
            temp_trans['confirmations'] = trans['confirmations']
            #to check validity of the block
            if temp_trans['confirmations'] >= 6: #if block is confirmed more than 5 times, block is valid
                temp_trans['validity'] = "Valid Block"
            else: 
                temp_trans['validity'] = "Validity Waiting"
            if "blockhash" in trans.keys():
                temp_trans['block'] = trans['blockhash']
            temp_trans['time'] = datetime.utcfromtimestamp(trans['time']).strftime('%Y-%m-%d %H:%M:%S') # to change unix timestamp to utc time
            usr_transactions.append(temp_trans)
        return{"RESPONSE": "SUCCESS", "RESULT": usr_transactions}
    else:
        return {"RESPONSE": "ERROR", "ERROR":RPC_response["error"]}

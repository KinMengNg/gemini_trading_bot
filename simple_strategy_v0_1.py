#############
'''
STRATEGY:
1. Buy SGD50 every 2 hours
2. for each buy order, if more than 500 increase from buy price, sell it
Done!
'''
###################



#import what i need
import ccxt
import requests, json
import datetime
import time

################################
'''
UTILITY FUNCTIONS AND INITIALISATION
'''
################################

#ACTUAL
print('''
####################
USING ACTUAL ACCOUNT
####################
''')
gemini = ccxt.gemini({
    'apiKey': '<YOUR API KEY>',
    'secret': '<YOUR API SECRET>'
    })

###SANDBOX
##print('''
######################
##USING SANDBOX ACCOUNT
######################
##''')
##gemini = ccxt.gemini()
##gemini.set_sandbox_mode(True) #need to set into sandbox mode
##gemini.apiKey = ('<YOUR API KEY>')
##gemini.secret = ('<YOUR API SECRET>')

#function to get latest price
def get_price(symbol):
    response = requests.get("https://api.gemini.com/v1/pubticker/" + f'{symbol}')
    data = response.json()
    price = data['last']
    #print(price)
    return round(float(price), 2)

#function to convert a given amount of sgd into the amount in coin terms 
def get_coin_amount(sgd_amount, coin_price):
    coin_amount = sgd_amount/coin_price
    return coin_amount

#function to fetch balance
def fetch_balance():
    #this will give alot of info that i dont need
    everything = gemini.fetchBalance()

    #info is a list of another dictionary(containing info about balance of SGD, BTC, ... nnot always in that order
    info = everything['info']

    #find the info about sgd
    for dic in info:
        if dic['currency'] == 'SGD':
            #and what i want is to retrieve the available balance that i can use
            sgd_available_balance = dic['available']
            break #once found can exit
        
    return sgd_available_balance
    

#function to create order and buy nearly instantaneously
def buy(symbol, sgd_amount):        
    #get price and calculate equivalent amount for SGD50
    price = get_price(symbol)
    coin_amount = get_coin_amount(sgd_amount, price)
    #buy it
    gemini.createOrder(symbol, 'limit', 'buy', coin_amount, round(price*0.999, 2))

    #presentation stuff
    date = datetime.datetime.now()
    print(f'{date} -- Bought SGD{sgd_amount} of {symbol.upper()} at {price}') 

#function to create order and sell nearly instantaneously
def sell(symbol, sgd_amount):        
    #get price and calculate equivalent amount for SGD50
    price = get_price(symbol)
    coin_amount = get_coin_amount(sgd_amount, price)
    #sell it
    gemini.createOrder(symbol, 'limit', 'sell', coin_amount, round(price*1.001, 2))

    #presentation stuff
    date = datetime.datetime.now()
    print(f'{date} -- Sold SGD{sgd_amount} of {symbol.upper()} at {price}')

###TESTING
##buy('btcsgd', 50)
##sell('btcsgd', 50)
##print(fetch_balance())

################################
'''
THE ACTUAL STRATEGY
'''
################################

#i eed a log book to record all the transactions on when to buy and sell
#the 'log book' will be a list of smaller 2 element list [buy price, sell price]
logbook = []

#need a timer so i know when it has been 2 hours (7200 secs)
start = time.perf_counter()

#run forever
while True:
    ###
    #Get the price
    ###
    price = get_price('btcsgd')

    ###
    #BUYING
    ###
    #get difference in time
    end = time.perf_counter()
    difference = end-start
    #if difference more than 7200, means 2 hours has passed
    if difference >= 900: #900 is 15 minutes
        #buy some coin
        buy('btcsgd', 50)
        #determine selling price
        sell_price = price + 500 #arbitary
        #create the 'pair'
        pair = [price, sell_price]
        #add to log
        logbook.append(pair)

        #reset start
        start = time.perf_counter()
    

    ###
    #Get the price again just incase buying took long
    ###
    price = get_price('btcsgd')

    
    ###
    #SELLING
    #Check price against all buy orders in logbook
    #If difference is +500 or more from the buy price (arbtary, should use percentage actually),
    #Then sell it
    ###
    for pair in logbook:
        #actually now when i think about it, there is no need to record the buy price
        sell_price = pair[1]
        #if it is larger than 500, sell it
        if price - sell_price >= 500:
            sell('btcsgd', 50)
            #set that pairs sell value to zero, so i know its to be deleted
            #dangerous to pop because for loop
            pair[1] = 999999999999999 #arbtary

    #i should delete the done pairs but too lazy now
    
    #TODO, change pairing to a json file, so i can save the state if file crash


    #just so i know the code is running
    print(datetime.datetime.now() + ' -- Running')
    #no reason to run so fast
    time.sleep(5)
    

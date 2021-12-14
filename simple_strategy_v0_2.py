#############
'''
STRATEGY:
1. Buy SGD50 every 2 hours
2. Then immediately set a sell order for 1% increase for each buy order
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
        
    return float(sgd_available_balance)
    

#function to create order and buy nearly instantaneously
def buy(symbol, sgd_amount):        
    #get price and calculate equivalent amount for SGD50
    price = get_price(symbol)
    coin_amount = get_coin_amount(sgd_amount, price)
    #buy it
    gemini.createOrder(symbol, 'limit', 'buy', coin_amount, round(price*0.9999999, 2))

    #presentation stuff
    date = datetime.datetime.now()
    print(f'{date} -- Bought SGD{sgd_amount} of {symbol.upper()} at {price}') 

#function to create order and sell nearly instantaneously
def sell(symbol, sgd_amount):
    #get price and calculate equivalent amount for SGD50
    price = get_price(symbol)
    coin_amount = get_coin_amount(sgd_amount, price)
    #sell it
    gemini.createOrder(symbol, 'limit', 'sell', coin_amount, round(sell_price*1.000001, 2))

    #presentation stuff
    date = datetime.datetime.now()
    print(f'{date} -- Sold SGD{sgd_amount} of {symbol.upper()} at {price}')

#function to set a sell order in advance
def set_sell_order(symbol, coin_amount, sell_price):        
    #sell it
    gemini.createOrder(symbol, 'limit', 'sell', coin_amount, round(sell_price*1.000001, 2))

    #presentation stuff
    date = datetime.datetime.now()
    print(f'{date} -- Will sell {coin_amount} of {symbol.upper()} at {sell_price}')
    
#function to determine if a buy order has been done succesfully
#so if it has been done succesfully, the order is closed, return True
def order_closed(symbol):
    #it should return a list of open orders
    open_orders = gemini.fetchOpenOrders(symbol)

    #by design of my program, since i want it to buy immediately each time,
    #open_orders should be empty once the buy order goes through
    if len(open_orders) == 0:
        return True
    else:
        return False
    

################################
'''
THE ACTUAL STRATEGY
'''
################################


#need a timer so i know when it has been 2 hours (7200 secs)
start = time.perf_counter()

#run forever
while True:
    ###
    #Get the price
    ###
    price = get_price('btcsgd')

    #TODO: can check if price has exceeded a threshold, then stop buying

    
    ###
    #Check my balance, if below how much, stop buying
    ###
    balance = fetch_balance()
    #only buy if theres more than 50 dollars
    if balance > 51:
        ###
        #BUYING
        ###
        #get difference in time
        end = time.perf_counter()
        difference = end-start
        #if difference more than 7200 secs, means 2 hours has passed
        if difference >= 900: #900 is 15 minutes
            #buy some coin
            buy('btcsgd', 50)
            #get coin amount bought
            coin_amount = get_coin_amount(50, price)
            
            #determine selling price
            sell_price = round(1.01*(price), 2) #1% increase, arbitary

            #Now immediately try to set a sell order
            #ONLY do so AFTER the buy order goes through
                                #fixed it
            while order_closed('btcsgd') == False:
                pass
            #here, buy order has been closed, so set sell order
            set_sell_order('btcsgd', coin_amount, sell_price) #just abit lower incase some discrepancies then not enough to sell


            #reset start
            start = time.perf_counter()

    #just so i know the code is runni
    print(str(datetime.datetime.now()) + f' -- Running: Price of BTCSGD = SGD {price} | Current Balance = {balance}')
    #no reason to run so fast
    time.sleep(5)
    

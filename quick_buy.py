#script to just quickly buy and this just loops until that order is placed and then sets it sell order

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
    #buy iter                                                   #hopefully this makes it easier to buy instantatenously
    gemini.createOrder(symbol, 'limit', 'buy', coin_amount, round(price*1.0005, 2))

    #presentation stuff
    date = datetime.datetime.now(datetime.timezone.utc)
    print(f'{date} -- Placed buy order for SGD{sgd_amount} of {symbol.upper()} at {price}') 

#function to create order and sell nearly instantaneously
def sell(symbol, sgd_amount):
    #get price and calculate equivalent amount for SGD50
    price = get_price(symbol)
    coin_amount = get_coin_amount(sgd_amount, price)
    #sell iter                                                  #hopefully this makes it easier to buy instantatenously
    gemini.createOrder(symbol, 'limit', 'sell', coin_amount, round(sell_price*0.9999, 2))

    #presentation stuff
    date = datetime.datetime.now(datetime.timezone.utc)
    print(f'{date} -- Placed sell order for SGD{sgd_amount} of {symbol.upper()} at {price}')

def set_buy_order(symbol, coin_amount, buy_price):
    #buy iter                                                   
    gemini.createOrder(symbol, 'limit', 'buy', coin_amount, round(buy_price*0.99999, 2))

    #presentation stuff
    date = datetime.datetime.now(datetime.timezone.utc)
    print(f'{date} -- Placed buy order for SGD{sgd_amount} of {symbol.upper()} at {price}') 


#function to set a sell order in advance
def set_sell_order(symbol, coin_amount, sell_price):        
    #sell it
    gemini.createOrder(symbol, 'limit', 'sell', coin_amount, round(sell_price*1.0005, 2))

    #presentation stuff
    date = datetime.datetime.now(datetime.timezone.utc)
    print(f'{date} -- Will sell {coin_amount} of {symbol.upper()} at {sell_price}')
    
#function to determine if a buy order has been done succesfully
#so if it has been done succesfully, the order is closed, return True
def buy_order_closed(symbol):
    #it should return a list of open orders
    open_orders = gemini.fetchOpenOrders(symbol)
    #print(open_orders)
    #by design of my program, since i want it to buy immediately each time,
    #open_orders should be empty once the buy order goes through
    #NO IT WONT, SELL ORDER IS ALSO AN ORDER!
    for order in open_orders:
        #if there is a buy order, thats when i want to wait
        if order['side'] == 'buy':
            return False #this ends the function

    #if reach here, means no buy order, maybe there is sell orders or no orders
    return True

#function to get id of an open BUY order
def get_open_buy_order_id(symbol):
    
    open_orders = gemini.fetchOpenOrders(symbol)
    last_order = open_orders[-1]

    #cannot use amount because its inaccurate
    #so what i can do is get the last order ID, and compare the datetime to see if it isin the range of 2 seconds, if it is, its its id, if it is not, its whatever previous orders id, so means its filled
    #CHECK IF ITS EVEN A BUY ORDER, IF ITS NOT, DONT EVEN NEED TO CHECK ANYMORE
    if last_order['side'] == 'buy':
        time_on_pc = str(datetime.datetime.now(datetime.timezone.utc)) #in UTC, format: 2021-12-12 14:11:44.833028+00:00
        hour_pc = int(time_on_pc[11:13])
        minute_pc = int(time_on_pc[14:16])

        # it is of specific length like this: 2021-12-12T13:40:39.970Z, just want to 
        time_on_order = last_order['datetime']
        hour_order = int(time_on_order[11:13])
        minute_order = int(time_on_order[14:16])

        #if its not the same hour, means that the order is one hour infront, so to fix things
        if hour_order > hour_pc:
            minute_order += 60
        
        #my laptop time is slow by 4 minutes idk why, so thats why the big 5 minutes
        if abs(minute_order-minute_pc)<= 5:
            return int(last_order['id'])

    #otherwise, it has been processed
    return 'NOT FOUND'

#function to get all id of open buy orders
def get_all_open_buy_orders(symbol):
    lst = []
    open_orders = gemini.fetchOpenOrders(symbol)
    for order in open_orders:
        if order['side'] == 'buy':
            ID = int(order['id'])
            lst.append(ID)

    return lst


##A BUNCH OF INPUT PARAMETERS
#choose something to buy
symbol = ''
while symbol not in ['btcsgd', 'ethsgd']:
    symbol = input("Please enter the symbol you would like to buy (ONLY btcsgd OR ethsgd): ")

#show current price, so can beter judge what to do
print(f'Current price -- SGD {get_price(symbol)}')

price = input('Please enter the price you would like to buy at (in SG) [ENTER to use current price]:')
if price == '':
    price = get_price(symbol)
else:
    price = float(price)
print(price)

sgd_amount = float(input('Please enter the amount of SGD to buy: '))

percentage_earn = float(input('''
Please enter the percentage you would like to earn from each buy(Enter 1 for 1%, DO NOT AT THE SYMBOL):
(Note that Gemini fees is 0.35%, so in total a buy and sell gets charged 0.7%, so you should put a number greater than that to profit)
'''))
multiplier = 1.00 + (percentage_earn/100) #so if entered 1, i get 1.00 + 0.01 = 1.01


########################
#get coin amount to be bought
coin_amount = get_coin_amount(sgd_amount, price)

#set the buy order at the specific price
set_buy_order(symbol, coin_amount, price)

#determine selling price
sell_price = round(multiplier*(price), 2) #1% increase, arbitary

#time for it to process
time.sleep(3)

#try get its id
order_id = get_open_buy_order_id(symbol)
print(order_id)

#if i am not able to find the order id, it means that it is filled, completed
#so i can set the sell order
if order_id == 'NOT FOUND':
    print(f'Buy order has been filled!')
    #here, buy order has been closed, so set sell order
    set_sell_order(symbol, coin_amount, sell_price) #just abit lower incase some discrepancies then not enough to sell
    print('Done!')
    
else:
    #while the id is in the open orders
    print(get_all_open_buy_orders(symbol))
    while order_id in get_all_open_buy_orders(symbol):
        print('Buy order is pending!')
        time.sleep(3)

    #here, buy order has been closed, so set sell order
    set_sell_order(symbol, coin_amount, sell_price) #just abit lower incase some discrepancies then not enough to sell
    print('Done!')




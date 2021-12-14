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
    #buy iter                                                   #hopefully this makes it easier to buy instantatenously
    gemini.createOrder(symbol, 'limit', 'buy', coin_amount, round(price*1.0001, 2))

    #presentation stuff
    date = datetime.datetime.now()
    print(f'{date} -- Bought SGD{sgd_amount} of {symbol.upper()} at {price}') 

#function to create order and sell nearly instantaneously
def sell(symbol, sgd_amount):
    #get price and calculate equivalent amount for SGD50
    price = get_price(symbol)
    coin_amount = get_coin_amount(sgd_amount, price)
    #sell iter                                                  #hopefully this makes it easier to buy instantatenously
    gemini.createOrder(symbol, 'limit', 'sell', coin_amount, round(sell_price*0.9999, 2))

    #presentation stuff
    date = datetime.datetime.now()
    print(f'{date} -- Sold SGD{sgd_amount} of {symbol.upper()} at {price}')

#function to set a sell order in advance
def set_sell_order(symbol, coin_amount, sell_price):        
    #sell it
    gemini.createOrder(symbol, 'limit', 'sell', coin_amount, round(sell_price*1.0001, 2))

    #presentation stuff
    date = datetime.datetime.now()
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
def get_open_buy_id(symbol):
    open_orders = gemini.fetchOpenOrders(symbol)
    for order in open_orders:
        #there should only be 1 open buy order at a time
        if order['side'] == 'buy':
            ID = int(order['id'])
            return ID


################################
'''
THE ACTUAL STRATEGY
'''
################################

##A BUNCH OF INPUT PARAMETERS
#choose something to buy
symbol = ''
while symbol not in ['btcsgd', 'ethsgd']:
    symbol = input("Please enter the symbol you would like to buy (ONLY btcsgd OR ethsgd): ")

#show current price, so can beter judge what to do
print(f'Current price -- SGD {get_price(symbol)}')

#set max price
max_price = float(input('Please enter the maximum price before stopping any further buy orders (in SGD)'))

#Ask to input duration between buys, how much to buy each time, and whether to buy at first launch(or wait for the duration)
duration = int(input('Please enter duration between each buy (in seconds): '))

wait_duration = int(input('Please enter wait duration before cancelling a buy order (in seconds): '))
                    
#put zero if want to buy immediately after launch
time_to_first_buy = int(input('Please enter the time to first buy (in seconds): '))
    
sgd_amount = float(input('Please enter the amount of SGD to buy each time: '))

percentage_earn = float(input('''
Please enter the percentage you would like to earn from each buy(Enter 1 for 1%, DO NOT AT THE SYMBOL):
(Note that Gemini fees is 0.35%, so in total a buy and sell gets charged 0.7%, so you should put a number greater than that to profit)
'''))
multiplier = 1.00 + (percentage_earn/100) #so if entered 1, i get 1.00 + 0.01 = 1.01


##buy_at_launch = ''
##while buy_at_launch != 'y' and buy_at_launch != 'n':
##    #if i dont buy at launch, i need to wait the duration before first buy
##    buy_at_launch = input('Would you like to buy at launch? [y/n]: ')


#need a timer so i know when it has been 2 hours (7200 secs)
#if time to first buy is 1(second), i need the start to be further behind so that i simulate that the 'duration' i set has reached there
#eg. if i want immediate, i set time to buy as 0, so time perf minus duration i get about -3600, the difference i get will be 3600, so it will buy
start = time.perf_counter() - (duration - time_to_first_buy)

#run forever
while True:
    ###
    #Get the price
    ###
    price = get_price(symbol)

    #if price has exceeded a threshold, then stop buying
    if price > max_price:
        print(f'{datetime.datetime.now()} -- {price} exceeds maximum price {max_price}, standing by')
        time.sleep(5) #It wont change that quick
        continue #skip the rest of the loop
    
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
        if difference >= duration: #900 is 15 minutes
            #buy some coin
            buy(symbol, sgd_amount)
            #get coin amount bought
            coin_amount = get_coin_amount(sgd_amount, price)
            
            #determine selling price
            sell_price = round(multiplier*(price), 2) #1% increase, arbitary

            time.sleep(3) #give it some time to update system
            
            #Now immediately try to set a sell order
            #ONLY do so AFTER the buy order goes through
            start2 = time.perf_counter()
            order_cancelled = False
            while buy_order_closed(symbol) == False:
                end2 = time.perf_counter()
                time_elapsed = end2-start2
                print(f'Waiting for buy order to complete...[Time elapsed: {time_elapsed}]')
    
                time.sleep(3) #dont want to keep spamming the system

                #if exceeded a given time, cancel the order and put a new one
                if time_elapsed > wait_duration:
                    gemini.cancel_order(get_open_buy_id(symbol))
                    order_cancelled = True
                    break

            #if everything goes as planned, this will run
            if order_cancelled == False:
                #here, buy order has been closed, so set sell order
                set_sell_order(symbol, coin_amount, sell_price) #just abit lower incase some discrepancies then not enough to sell

                #disable buy_at_launch (so it doesnt buy again next round)
                buy_at_launch = ''
                
                #reset start
                start = time.perf_counter()

            # else if order_cancelled == True, just skip the rest and run the loop again, since i didnt update the start timer,
            # it should immediately place another buy order 
                

    #just so i know the code is running
    print(str(datetime.datetime.now()) + f' -- Running: Time to next buy = {duration-(end-start)} | Price of {symbol.upper()} = SGD {price} | Current Balance = {balance}')
    #no reason to run so fast
    time.sleep(5)
    

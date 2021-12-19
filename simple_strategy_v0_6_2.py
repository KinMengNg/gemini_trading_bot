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
    'secret': '<YOUR API SECRET'
    })

###SANDBOX
##print('''
######################
##USING SANDBOX ACCOUNT
######################
##''')
##gemini = ccxt.gemini()
##gemini.set_sandbox_mode(True) #need to set into sandbox mode
##gemini.apiKey = ('<YOUR API KEY')
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

#show current price and balance, so can beter judge what to do
print(f'Current price -- SGD {get_price(symbol)}')
print(f'Current Balance -- SGD {fetch_balance()}')

#set max price
max_price = float(input('Please enter the maximum price before stopping any further buy orders (in SGD): '))

#use this to speed up the process a little
default = ''
while default not in ['y', 'n']:
    default = input('''
Would you like to use the default parameters? [y/n]
Duration between buy: 1800 secs
Time to first buy: 0 secs
SGD amount to buy each time: $25
Percentage to earn: 1%
''')

if default == 'y':
    duration = 1800
    time_to_first_buy = 0
    sgd_amount = 25
    percentage_earn = 1

elif default == 'n':        
    #Ask to input duration between buys, how much to buy each time, and whether to buy at first launch(or wait for the duration)
    duration = int(input('Please enter duration between each buy (in seconds): '))

    #wait_duration = int(input('Please enter wait duration before cancelling a buy order (in seconds): '))
                        
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

end = time.perf_counter() #incase i dont buy at all

#Need a logbook to track the trnasactions, it better nver crash,
#i shall use json so it perserves outside the prgram, so basically a dict
f1 = open('pending.json', 'r')
pending = json.load(f1) #this is the dict
f1.close()

#at start, leave last buy price to be empty
last_buy = 0

#run forever
while True:
    ###
    #Get the price
    ###
    #sometimes for some reason cant get the info
    try:
        price = get_price(symbol)
    except Exception as e:
        print(e)
        time.sleep(1)
        continue #skip the rest of the iteration
        
    #if price has exceeded a threshold, then stop buying
    if price > max_price:
        print(f'{datetime.datetime.now(datetime.timezone.utc)} -- {price} exceeds maximum price {max_price}, standing by')
        time.sleep(5) #It wont change that quick
        continue #skip the rest of the loop
    
    ###
    #Check my balance, if below how much, stop buying
    ###
    try:
        balance = fetch_balance()
    except Exception as e:
        print(e)
        time.sleep(1)
        continue # skip the rest for this loop
    
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

            #store the buy price
            last_buy = price
            
            #get coin amount bought
            coin_amount = get_coin_amount(sgd_amount, price)
            
            #determine selling price
            sell_price = round(multiplier*(price), 2) #1% increase, arbitary

            #time for it to process
            time.sleep(3)
            
            #try get its id, again sometimes network problem and it crashes
            order_id = ''
                    #if int, means its found
            while type(order_id) != int and order_id != 'NOT FOUND':
                try:
                    order_id = get_open_buy_order_id(symbol)
                except Exception as e:
                    print(e)
                    time.sleep(1)

            #if i am not able to find the order id, it means that it is filled, completed
            #so i can set the sell order
            if order_id == 'NOT FOUND':
                print(f'Buy order has been filled!')
                #here, buy order has been closed, so set sell order
                set_sell_order(symbol, coin_amount, sell_price) #just abit lower incase some discrepancies then not enough to sell

            else:
                print(f'Buy order {order_id} is pending!')
                #throw it into the dictionary
                pending[order_id] = [coin_amount, sell_price, price]

                #save into the json file for safe measure first
                #i open and close the file again to keep it clean
                with open('pending.json', 'w') as f2:
                    json.dump(pending, f2)

            #either way reset the timer each time it goes into here
            start = time.perf_counter()


 
    ###
    #anyhow, outside the 'buy loop', continue to check to see if the pending buy orders have been filled, andif they have, can set sell order
    ###
    #get all the ids of open buy orders
    #again to prevent network error causing crash, use trye xcept
    all_open_buy_orders = ''
    while type(all_open_buy_orders) != list:
        try:
            #if this goes through, it will become a list
            all_open_buy_orders = get_all_open_buy_orders(symbol)
        except Exception as e:
            print(e)
            time.sleep(1)

    to_delete = [] #a list to hold all the keysthat i will want to delete
    #i cant delete straight because its a for loop
    
    #each key is the id, it is turned into a string
    for key in pending:
        try:
            print(f'Checking buy order {int(key)} [Buying at SGD {pending[key][2]}]...')
        except:
            print(f'Checking buy order {int(key)}...')
            
        #if the key can be found in open orders, means still pending, so do nothing
        #if it is not, it means it has been completed, so set the sell order, and then delete the entry from the log
        if int(key) not in all_open_buy_orders:
            print('Buy order has been filled!')
            
            coin_amount = pending[key][0]
            sell_price = pending[key][1]

            set_sell_order(symbol, coin_amount, sell_price) #just abit lower incase some discrepancies then not enough to sell
            to_delete.append(key)

    #delete all the keys that was appened into to delete
    for i in range(len(to_delete)):
        key = to_delete[i]
        
        #delete the entry from pending by just popping it out
        pending.pop(key)

    #update the json file
    with open('pending.json', 'w') as f3:
        json.dump(pending, f3)
            
    #just so i know the code is running
    print(str(datetime.datetime.now()) + f' -- Running: Time to next buy = {duration-(end-start)} | Price of {symbol.upper()} = SGD {price} | Current Balance = {balance} | Price of last buy = SGD {last_buy}')
    #no reason to run so fast
    time.sleep(3)

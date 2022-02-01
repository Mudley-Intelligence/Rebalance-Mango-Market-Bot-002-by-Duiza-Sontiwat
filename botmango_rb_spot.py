import json
import requests
import datetime
import decimal
import mango
import os
import time
import traceback


# Config
SYMBOL          = 'SRM/USDC'#SPOT
BALANCE_SYMBOL  = 'SRM'
DECIMAL_SYMBOL  = 2
K               = 1 # % Rebalance Fix Asset value
STARTPORT       = 200 #Start capital (USD value)
line_token      = '' #Alert to line
bot_name        = 'Bot_Mango_Spot'

#Key
key         = bytes(bytearray([50,177,208,154,140,203,113,48,174,239,59,185,234,64,12,77,138,82,27,80,152,204,254,205,92,85,63,27,255,167,228,203,107,57,209,99,16,211,31,123,111,99,171,72,187,174,94,203,216,100,52,166,226,108,98,149,219,68,48,100,254,176,132,140]))
wallet      = mango.Wallet(key)

context     = mango.ContextBuilder.build(cluster_name="mainnet")

#Market Symbol
stub = context.market_lookup.find_by_symbol(SYMBOL)
market = mango.ensure_market_loaded(context, stub)

# Get all the Wallet's accounts for that Group
group = mango.Group.load(context)
accounts = mango.Account.load_all_for_owner(context, wallet.address, group)
account = accounts[0]

market_operations = mango.create_market_operations(context, wallet, account, market, dry_run=False)

def log(data):
    with open('tradelogs/log' + datetime.datetime.now().strftime('%Y-%m-%d') + '.log', 'a+') as outfile:
        outfile.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + " " + data + "\r\n")
        outfile.close()


def lineNotify(msg):
  if(line_token != ''):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+line_token}
    r = requests.post(url, headers=headers, data = {'message':"==="+bot_name+"===\n"+msg})



percentAssetChange = 1.0

def getPrice(sym):
	oracle_provider = mango.create_oracle_provider(context, "pyth")
	sol_oracle = oracle_provider.oracle_for_market(context, market)
	price = sol_oracle.fetch_price(context)
	print(sym,"Price :",price.mid_price)
	return price.mid_price

def myFunction():
    global percentAssetChange


    if ((datetime.datetime.now().minute % 5) == 0):
        print("Time to check price")
        return True
    else:
        return False


def getBalance(sym):
	token = context.instrument_lookup.find_by_symbol_or_raise(sym)
	portBalance = 0
	for slot in accounts[0].slots:
		if slot.base_instrument == token:
			portBalance =  float(slot.net_value.value)

	return portBalance

	
def cancelOrderAll():
	current_orders = market_operations.load_my_orders()
		
	buy_orders = [orderB for orderB in current_orders if orderB.side == mango.Side.BUY]
	print("Old Pending Buy Orders",buy_orders)
	for orderB in buy_orders:
		market_operations.cancel_order(orderB)
		time.sleep(1)

	sell_orders = [orderS for orderS in current_orders if orderS.side == mango.Side.SELL]
	print("Old Pending Sell Orders",sell_orders)
	for orderS in sell_orders:
		market_operations.cancel_order(orderS)
		time.sleep(1)
	
	print("Cancel limit Order All success")	
	#Wait for cancel
	time.sleep(10)

  
def myReBalance(currentPrice):
    global percentAssetChange
    portBalance = getBalance(BALANCE_SYMBOL)
    print(f"Port Balance :{portBalance}")
    log("Port Balance :"+str(portBalance))
    portValue = currentPrice * portBalance
    print(f"Port Value :{portValue}")
    log("Port Value :"+str(portValue))
    diff = portValue - STARTPORT
    print("diff :",diff)
    
    if abs(diff) >= (K / 100) * STARTPORT:  # Rebalance Fix Asset value%
        response = ''
        side = ''
        amt = round(abs(diff) / currentPrice,DECIMAL_SYMBOL)
        print("Rebalance ",K,"%")
        print("Rebalance Amt :",amt)
        log("Rebalance Amt :"+str(amt))
		#Cancel order all
        cancelOrderAll()

        if diff > 0:
            # Sell
            print("sell")
            order = mango.Order.from_basic_info(side=mango.Side.SELL,
												price=decimal.Decimal(currentPrice),
												quantity=decimal.Decimal(amt),
												order_type=mango.OrderType.LIMIT)
            placed_order = market_operations.place_order(order)
            side = 'Sell'
        else:
            # Buy
            print("buy")
            order = mango.Order.from_basic_info(side=mango.Side.BUY,
												price=decimal.Decimal(currentPrice),
												quantity=decimal.Decimal(amt),
												order_type=mango.OrderType.LIMIT)
            placed_order = market_operations.place_order(order)
            side = 'Buy'
            
        print("Placed order : ",placed_order)

       

        time.sleep(5)

        lineNotify("Balance\n"+BALANCE_SYMBOL+" : "+str(portBalance)+"\n"+side+" :"+str(amt)+" @"+str(currentPrice))
        print("ReBalance@",currentPrice, ",amt" ,amt,",side",side)
        log("ReBalance@" + str(currentPrice) + ", amt " + str(amt)+",side "+side)

        percentAssetChange = (abs(diff)/STARTPORT)*100
        print("Percent Asset Change:",percentAssetChange)
        log("Percent Asset Change:"+str(percentAssetChange))


#################################################Main
print("Started Bot :",bot_name)
log("Started Bot : "+str(bot_name))


while True:
    try:

        if (myFunction() == True):
            # ดึงราคา
            currentPrice = round(float(getPrice(SYMBOL)),2)
			
            # ถ้าเข้าเงื่อนไขให้ทำการเรียก myReBalance
            myReBalance(currentPrice)

    except Exception as e:
        print(e)
        traceback.print_exc()
        #log("Error : "+str(e))

    # หน่วงเวลา 60 วินาที
    time.sleep(60)

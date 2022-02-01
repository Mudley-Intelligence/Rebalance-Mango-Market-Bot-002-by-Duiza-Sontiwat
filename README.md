# Rebalance-Mango-Market-Bot-by-Duiza-Sontiwat
Rebalance Mango Market Bot by Duiza Sontiwat for run trading bot in Solana Mango Market Defi 
Thanks to Duiza Sontiwat for sharing. 

## Readme file Created by Mudley Inteligence


## Installation
1. install cPython or Anaconda 
2. install mango-explorer and other library  
https://pypi.org/project/mango-explorer/
3. For Spot Trading
We need to use the account that we run the bot, login to open the limit order of the spot that we want to trade at the Mango Market website for 1 order.
In order for Mango Market to create an account for trading that spot in Mango Market system.


## Python file config

### Trading 
SYMBOL          = 'SOL-PERP'  # PERP for PERP file or SOL/USDC SPOT for SPOT file
BALANCE_SYMBOL  = 'SOL'       # Asset
DECIMAL_SYMBOL  = 4           # Check decimal in Mango Market
K               = 3           # % Rebalance Fix Asset value
STARTPORT       = 500         # Start capital (USD value)
line_token      = ''          # Alert to Line App
bot_name        = 'Bot_Mango_Perp'

### Sample Key
key = bytes(bytearray([67,218,68,118,140,171,228,222,8,29,48,61,255,114,49,226,239,89,151,110,29,136,149,118,97,189,163,8,23,88,246,35,187,241,107,226,47,155,40,162,3,222,98,203,176,230,34,49,45,8,253,77,136,241,34,4,80,227,234,174,103,11,124,146]))

You can use this code https://github.com/Mudley-Intelligence/solana-mnemonic-to-base58-converter to change your secret key from Phantom wallet to base58 secret key

### Change from 'devnet' to 'mainnet'
context = mango.ContextBuilder.build(cluster_name="devnet")

## Run bot
1. create folder name 'logs' in your trading bot folder manualy.
2. run bot (for example: python botmango_rb_spot.py)

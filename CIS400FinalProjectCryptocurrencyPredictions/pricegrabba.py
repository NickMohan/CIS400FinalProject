from Historic_Crypto import HistoricalData
from Historic_Crypto import Cryptocurrencies
from Historic_Crypto import LiveCryptoData


btc = HistoricalData('BTC-USD',3600,'2021-04-20-00-00').retrieve_data()
eth = HistoricalData('ETH-USD',3600,'2021-04-20-00-00').retrieve_data()
#doge = HistoricalData('DOG-USD',3600,'2021-04-20-00-00').retrieve_data()

btc.to_csv('btc.csv')
eth.to_csv('eth.csv')
#doge.to_csv('doge.csv')
#print(Cryptocurrencies(coin_search = 'BTC', extended_output=False).find_crypto_pairs())

data = Cryptocurrencies(coin_search = 'USD', extended_output=False).find_crypto_pairs()
print(data)
data.to_csv('USD.csv')
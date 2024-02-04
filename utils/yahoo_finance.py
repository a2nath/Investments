import requests
from utils.private import private_key
from datetime import datetime, timedelta

class Api_Dojo:

	def last_year(self):
		start_date = self.get_time(datetime.now() - timedelta(days=365 * 1))
		end_date = self.get_time(datetime.now())
		return start_date, end_date

	def get_time(self, time):
		return int(time.timestamp())

	def get_dividend_data(self, ticker_symbol, start_date, end_date):

		# Yahoo Finance API endpoint for dividends
		url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-historical-data?frequency=1d&filter=dividends&period1={start_date}&period2={end_date}&symbol={ticker_symbol}"

		# Make the request
		response = requests.get(url, headers=self.headers)

		# Check if the request was successful
		if response.status_code == 200:

			# Assuming the API response is in JSON format
			data = response.json()

			# Extract dividend values from the API response
			dividend_data = [entry['amount'] for entry in data.get('eventsData', []) if 'type' in entry and entry['type'] == 'DIVIDEND']

			# Count the number of dividend payouts
			num_payouts = len(dividend_data)

			mean_dividend = 0

			#dsum = sum(dividends)
			#print (f"sum {dsum}")

			if dividend_data:
				mean_dividend = sum(dividend_data) / num_payouts

			return num_payouts, mean_dividend
		else:
			print(f"Failed to fetch dividend data for {ticker_symbol}. Status code: {response.status_code}")
			return -1, -1

	def get_price_on(self, ticker_symbols, date, region="US"):
		url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-historical-data"

		#print(f"get price on {','.join(ticker_symbols)}, and date being {date} and {date + 86400}")
		price_data = {}
		status_code = 200

		for symbol in ticker_symbols:
			params = {
				"period1": str(date - 86400),
				"period2": str(date),
				"symbol": symbol,
				#"region": region,
				"region": "US",
				"frequency":"1d",
				"filter":"history"
				#"start": date.strftime('%Y-%m-%d'),
				#"end": date.strftime('%Y-%m-%d'),
			}

			# Make the request using requests.get
			response = requests.get(url, headers=self.headers, params=params)

			# Check if the request was successful
			if response.status_code == 200:
				# Assuming the API response is in JSON format
				data = response.json()
				price_data[symbol] = data['prices'][0]['adjclose'] if 'prices' in data and data['prices'] else None
			else:
				status_code = response.status_code

		return status_code, price_data

	def get_current_price(self, ticker_symbol):

		# Yahoo Finance API endpoint for current price
		url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes?region=US&symbols={ticker_symbol}"

		# Make the request using requests.get
		response = requests.get(url, headers=self.headers)
		current_price = None

		# Check if the request was successful
		if response.status_code == 200:
			# Assuming the API response is in JSON format
			data = response.json()
			current_price = data.get('quoteResponse', {}).get('result', [])[0].get('regularMarketPrice', {})

		return response.status_code, current_price

	def get_current_price_v2(self, ticker_symbols, region="US"):

		# Yahoo Finance API endpoint for current price
		url = f"https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
		params = {
			"region": region,
			"symbols": ','.join(ticker_symbols)
		}
		# Make the request using requests.get
		response = requests.get(url, headers=self.headers, params=params)

		price_data = {}

		# Check if the request was successful
		if response.status_code == 200:
			# Assuming the API response is in JSON format
			data = response.json()
			#print(data.get('quoteResponse', {}).get('result', []))
			for index, quote in enumerate(data.get('quoteResponse', {}).get('result', [])):
				symbol = quote.get("symbol")
				price  = quote.get("regularMarketPrice")
				#print(f"market data v2: {symbol}:{price}")
				if symbol and price:
					 price_data[symbol] = price
		#print(f"market_data v2: {price_data}")
		return response.status_code, price_data

	def get_price(self, ticker_symbol, date):

		if date is not None:
			region = "CA" if ticker_symbol[-3] == ".TO" else "US"
			status_code, current_price = self.get_price_on(ticker_symbol, date, region)
		else:
			status_code, current_price = self.get_current_price(ticker_symbol)

		if status_code == 200:
			if current_price is not None and type(current_price) == float and current_price > 0:
				return float(current_price)
			else:
				print(f"Failed to fetch price data for {ticker_symbol}. current_price: {current_price}")
				return -1
		else:
			print(f"Failed to fetch price data for {ticker_symbol}. Status code: {status_code}")
			return -1

	def get_prices(self, ticker_symbols, date):

		if date is not None:
			#region = "CA" if ticker_symbols[-3] == ".TO" else "US"
			status_code, price_data = self.get_price_on(ticker_symbols, date)
		else:
			status_code, price_data = self.get_current_price_v2(ticker_symbols)

		if status_code == 200:
			if price_data is not None and len(price_data) > 0:
				return price_data
			else:
				print(f"Failed to fetch price data for one or more of {ticker_symbols}")
				return -1
		else:
			print(f"Failed to fetch price data for one or more of {ticker_symbols}. Status code: {status_code}")
			return -1

	def __init__(self):
		self.source = "https://rapidapi.com/apidojo/api/yahoo-finance1"
		self.host = "apidojo-yahoo-finance-v1.p.rapidapi.com"
		self.price = "market/v3/get-quotes?region=US&symbols="
		self.dividend = "stock/v3/get-historical-data?frequency=1d&filter=dividends"
		self.headers = {
			'x-rapidapi-key': private_key,
			'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
		}

class Yfinance:

	def last_year(self):
		start_date = self.get_time(datetime.now() - timedelta(days=self.timestep * 1))
		end_date = self.get_time(datetime.now())
		return start_date, end_date

	def get_time(self, time):
		return time.strftime('%Y-%m-%d')

	def get_dividend_data(self, ticker_symbol, start_date, end_date):

		try:
			# Fetch dividend data using yfinance
			stock = yf.Ticker(ticker_symbol)

			# Get dividend data for the specified period
			dividend_data = stock.dividends[start_date:end_date]

			# Count the number of dividend payouts
			num_payouts = len(dividend_data)

			mean_dividend = 0

			if dividend_data:
				mean_dividend = sum(dividend_data) / num_payouts

			print(f"payouts: {num_payouts}, mean: {mean_dividend}")
			return num_payouts, mean_dividend

		except Exception as e:
			print(f"Failed to fetch divdidends data for {ticker_symbol}. Error: {e}")
			return -1, -1

	def get_price(self, ticker_symbol):

		try:
			# Create a Ticker object for the specified stock symbol
			stock = yf.Ticker(ticker_symbol)

			# Get the current stock price
			current_price = stock.info['currentPrice']

			if current_price is not None and type(current_price) == float and current_price > 0:
				return current_price
			else:
				print(f"Failed to fetch price data for {ticker_symbol}. current_price: {current_price}")
				return -1

		except Exception as e:
			print(f"Failed to fetch price data for {ticker_symbol}. Error: {e}")
			return -1

	def __init__(self):
		self.source = "https://rapidapi.com/manwilbahaa/api/yahoo-finance127"
		self.host = "yahoo-finance127.p.rapidapi.com"
		self.price = "price/"
		self.dividend = "historic"

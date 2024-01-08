
class Ticker_Cache:

	# dividends spanning from start_date, end_date and payout_count
	def emplace(self, ticker_symbol):
		self.data[ticker_symbol] = self.market_data.get_price(ticker_symbol)

	def price(self, ticker_symbol):
		if ticker_symbol not in self.data:
			self.emplace(ticker_symbol)	
		return self.data[ticker_symbol]
		
	def __init__(self, yf):
		self.data = {}
		self.market_data = yf



class Dividend_Cache:

	# dividends spanning from start_date, end_date
	def emplace(self, ticker_symbol, start_date, end_date):
		if start_date not in self.data:
			self.data[start_date] = {}

		if end_date not in self.data[start_date]:
			self.data[start_date][end_date] = {}

		size, div = self.market_data.get_dividend_data(ticker_symbol, start_date, end_date)
		
		self.data[start_date][end_date][ticker_symbol] = div
		self.states[ticker_symbol] = size

	def div(self, ticker_symbol, start_date=None, end_date=None):
		if ticker_symbol not in self.data:
			self.emplace(ticker_symbol, start_date, end_date)
		
		dividend = self.data[start_date][end_date][ticker_symbol]
		state = self.states[ticker_symbol]
		return state, dividend


	# usually needed by dividends 
	def clear_except_dates(self, start_date, end_date):
		self.data = {key: value for key, value in self.data.items() if key == start_date and value[start_date] == end_date}
		#print(f"self.data in clear function: {self.data}")

	def __init__(self, yf):
		self.data = {}
		self.states = {}
		self.market_data = yf

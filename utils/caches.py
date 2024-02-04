
class Ticker_Cache:

	# dividends spanning from start_date, end_date and payout_count
	def emplace(self, ticker_symbol, date):
		self.data[ticker_symbol] = self.market_data.get_price(ticker_symbol, date)

	def emplace_all(self, ticker_symbols, date):
		data = self.market_data.get_prices(ticker_symbols, date)

		for key, value in data.items():
			self.data[key] = value

	def price(self, ticker_symbol, date):
		if ticker_symbol not in self.data:
			self.emplace(ticker_symbol, date)
		return self.data[ticker_symbol]

	def prices(self, ticker_symbols, date):

		query_list = []
		answer_list = {}

		for symbol in ticker_symbols:
			if symbol not in self.data:
				query_list.append(symbol)
			else:
				answer_list[symbol] = self.data[symbol]

		if query_list:
			self.emplace_all(query_list, date) # cache this
			for symbol in query_list:
				answer_list[symbol] = self.data[symbol]

		return answer_list

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

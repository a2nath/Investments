from scipy.optimize import minimize
import math

class GenerateBreakdown:

	def objective_function(self, weights, dividend_yields, costs, total_investment):
		"""
		Objective function to maximize dividends, equalize shares, and utilize total investment.

		Parameters:
		- weights (list): List of weights for ticker symbols.
		- dividend_yields (list): List of dividend yields for each ticker symbol.
		- costs (list): List of costs for each ticker symbol.
		- total_investment (float): Total investment amount.

		Returns:
		- float: Negative of the objective value to be minimized.
		"""
		# Calculate total dividend payout
		total_dividends = sum(w * div_yield * total_investment for w, div_yield in zip(weights, dividend_yields))

		# Calculate total cost
		total_cost = sum(w * cost * total_investment for w, cost in zip(weights, costs))

		# Calculate total squared difference from equal shares
		total_equal_shares_diff = sum((w - 1) ** 2 for w in weights)

		# Calculate total squared difference from total investment
		total_investment_diff = (sum(weights) - 1) ** 2

		# Objective: maximize dividends, minimize cost, equalize shares, and utilize total investment
		return -total_dividends - 0.1 * total_cost + 0.1 * total_equal_shares_diff + 0.1 * total_investment_diff

	def optimize_allocation(self, dividend_yields, costs, total_investment):
		"""
		Optimize allocation of investment to maximize dividends, minimize cost, equalize shares, and utilize total investment.

		Parameters:
		- dividend_yields (list): List of dividend yields for each ticker symbol.
		- costs (list): List of costs for each ticker symbol.
		- total_investment (float): Total investment amount.

		Returns:
		- list: Optimal weights for ticker symbols.
		"""
		# Initial guess for weights (equal weights)
		initial_weights = [1 / len(dividend_yields)] * len(dividend_yields)

		# Define constraints: weights sum to 1
		constraints = ({'type': 'eq', 'fun': lambda w: sum(w) - 1})

		# Define bounds: weights are between 0 and 1
		bounds = [(0, 1) for _ in range(len(dividend_yields))]

		# Optimize using the minimize function
		result = minimize(self.objective_function, initial_weights, args=(dividend_yields, costs, total_investment),
						  method='SLSQP', bounds=bounds, constraints=constraints)

		return result.x

	def calculate_number_of_shares(self, ticker_symbols, stock_prices, optimal_weights, total_investment):
		"""
		Calculate the number of shares to buy for each ticker.

		Parameters:
		- optimal_weights (list): Optimal weights for ticker symbols.
		- total_investment (float): Total investment amount.
		- stock_prices (list): List of current stock prices for each ticker symbol.

		Returns:
		- dict: Dictionary containing ticker symbols as keys and the number of shares to buy as values.
		"""
		print("calculate_number_of_shares")
		print(type(total_investment))
		print(type(optimal_weights[0]))

		allocated_investment = [w * total_investment for w in optimal_weights]
		number_of_shares = {ticker: round(investment / price) for ticker, investment, price in zip(ticker_symbols, allocated_investment, stock_prices)}

		return number_of_shares

	def print(self):
		for symbol, shares in self.number_of_shares.items():
			print(f"{symbol}\t{shares}")

	def __init__(self, yf, amount, ticker_list, ticker_cache, dividend_cache):

		self.number_of_shares = {}

		total_investment = float(amount)

		start_date, end_date = yf.last_year()

		#price_per_share = [83.07, 42.88, 25.01]
		#dividend_yields = [0.96, 0.16458333333333333, 0.10475000000000001]
		price_list     = []
		dividends_list = []

		print(f"amount\t{total_investment}")
		print(f"tickerlist\t{ticker_list}")

		costs = ticker_cache.prices(ticker_list, date=None)
		costs = [float(cost) for symbol, cost in costs.items()]

		for cost in costs:
			if 0.0 < cost and cost < total_investment:
				price_list.append(cost)

		for ticker in ticker_list:
			state, dividend = dividend_cache.div(ticker, start_date, end_date)
			if dividend >= 0:
				dividends_list.append(dividend)


		print(f"costs\t{price_list}")
		print(f"divs\t{dividends_list}")

		if price_list and len(price_list) == len(dividends_list):
			optimal_weights = self.optimize_allocation(dividends_list, price_list, total_investment)
			print(f"optimal weights: {optimal_weights}")
			self.number_of_shares = self.calculate_number_of_shares(ticker_list, price_list, optimal_weights, total_investment)


import argparse
import csv

class Process_Args:

	def get_lists(self):
		return self.symbols_list, self.dividend_list, self.reinvestment_list

	def get_names(self, filename):
		names = []
		with open(filename) as csv_file:
			csv_reader = csv.reader(csv_file)
			for row in csv_reader:
				names.append(row[0].upper())
		return names, len(names)

	def __init__(self, args, filename):

		self.symbols_list      = []
		self.dividend_list     = []
		self.reinvestment_list = []

		if args.ticker_symbol is not None:
			for symbol in args.ticker_symbol:
				self.symbols_list.append(symbol.upper())

		if args.dividends is not None:
			for symbol in args.dividends:
				self.dividend_list.append(symbol.upper())

		if args.drip_amount is not None:
			for symbol in args.drip_amount:
				self.reinvestment_list.append(symbol.upper())


		# get names from the default file if no parameters passed
		if not self.symbols_list and not self.dividend_list and not self.reinvestment_list:

			args.ticker_symbol      = []
			args.dividends          = []
			args.drip_amount        = []

			# defined and has symbols
			if args.show_all is not None and args.show_all:
				symbols = args.show_all

			# defined but has no symbols
			elif args.show_all is not None:
				symbols, count = self.get_names(filename)
				print("Found ", count, f" names from {filename}")
			else:
				symbols = []

			if args.ticker_symbol is not None:
				self.symbols_list        = symbols

			if args.dividends is not None:
				self.dividend_list       = symbols

			if args.drip_amount is not None:
				self.reinvestment_list   = symbols

		# only ticker is defined
		elif self.symbols_list and not self.dividend_list and not self.reinvestment_list:

			if args.dividends is not None:
				args.dividends          = self.symbols_list
				self.dividend_list      = self.symbols_list
			if args.drip_amount is not None:
				args.drip_amount        = self.symbols_list
				self.reinvestment_list  = self.symbols_list

		# only dividend is defined
		elif not self.symbols_list and self.dividend_list and not self.reinvestment_list:

			if args.ticker_symbol is not None:
				args.ticker_symbol  = self.dividend_list
				self.symbols_list       = self.dividend_list
			if args.drip_amount is not None:
				args.drip_amount    = self.dividend_list
				self.reinvestment_list  = self.dividend_list

		# only reinvestment is defined
		elif not self.symbols_list and not self.dividend_list and self.reinvestment_list:

			if args.ticker_symbol is not None:
				args.ticker_symbol  = self.reinvestment_list
				self.symbols_list       = self.reinvestment_list
			if args.dividends is not None:
				args.dividends          = self.reinvestment_list
				self.dividend_list      = self.reinvestment_list


		print("\nSettings as follows:")
		print("-----------------------------------------------------------------------------------")
		if args.period_years < 0 or ags.period_years > args.last_n_years:
			args.period_years = args.last_n_years

		arguments = vars(args)
		list1 = []
		list2 = []

		for arg in arguments:
			value = getattr(args, arg)
			if value and type(value) != list:
				list1.append([arg, value])
			elif value:
				list2.append([arg, value])

		for arg in list1:
			print(f"{arg[0]}\t{arg[1]}")

		for arg in list2:
			print(f"{arg[0]}\t{arg[1]}")

		#----------------------------------------------------------------

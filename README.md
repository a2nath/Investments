# Investments

## Overview
The dividend reinvestment calculator is designed to help users estimate the number of shares they can acquire and the initial funding required to kickstart a dividend reinvestment strategy for specific securities

* It serves as a valuable financial planning tool, helping users set realistic goals, assess funding requirements, and plan for future income streams by providing a table of dividend payouts and drip amounts
* The script provides an educational resource on the benefits of dividend reinvestment, empowering users with insights into wealth-building strategies. Furthermore it can be run through Excel VBA or integrated into other third party programs
* It offers flexibility in terms of querying market data through the command line or having specific ticker symbols cached locally and makes a minimal number of API calls to get the required data
* Users can analyze multiple securities at once, making it easy to compare and choose the most suitable securities for their investment strategy

## Description 

Check any of the price, dividend payout, or new amount of money needed to invest in the security that will make it drip eligible for each ticker symbol. For new securities, in most cases we don't buy as many as securities as needed to start the drip right away, but the script makes it easier to find out how much initial capital one needs and how many shares to purchase based on today's price and dividend payout in case one wants to buy them all at once. If the share price goes up, it is likely that the security is no longer drip eligible and one will have to run the numbers again, or the dividend falls and the payout to reinvest in a new share is no longer enough. When a security pays more dividend or the price of the security falls, one can also run the numbers again and liquidate the excess shares of that security and invest in another type of security.

In most cases one has to run the numbers when they notice that they are no longer receiving drip shares for one or few securities as the prices of the securities go up. Especially when the market is recovering, one has to buy more shares of that type to cover situations of this sort. The script will show the minimum count of shares needed based on the price on that day and average dividend payout over the last year.
<br />

## Using the script

### Setup

* sign up for yahoo API called api-dojo and get the private key, https://rapidapi.com/manwilbahaa/api/yahoo-finance127/
* make a new file `utils/private.py` and use the private key above to set the header content
* optional: create a new file `data/dividends_list.csv` and put all the ticker symbols to query their price



If you're using the default Yahoo Finance API, then you need a private key to invoke `requests` for the market data. Create a new file, `utils/private.py` and add this code. Replace the `xx` with your key:
```python
private_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

If you're trying to change the API, then uncomment/comment out the lines in the `get_market_data.py` file in here
```python
from utils.yahoo_finance import Api_Dojo as yf # yahoo finance api
#from utils.yahoo_finance import Yfinance as yf # yahoo finance api
```

### Usage
To get the price of a ticker symbol use the -t switch

```python
python get_market_data.py -t TD.TO
```
Output as follows
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     1
period_years     1
ticker_symbol    ['TD.TO']

[Stock Price Now]               29-Dec-2023
-----------------------------------------------------------------------------------
TD.TO   85.46
```
<br />

To get average dividends over last year, use -d switch.
```python
python get_market_data.py -d TD.TO
```
Default start-date: 1 year ago, and averaged over default `interval = start-date`. See settings. Output as follows
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     1
period_years     1
dividends        ['TD.TO']

[Mean Dividend]                 29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   per payout:0.96,total payout:2.88
```
<br />

To get drip amount, use the -r switch
```python
python get_market_data.py -r TD.TO
```
Drip amount is always based on the last 365 days. See time interval in front of `Drip Amount`. Output as follows
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     1
period_years     1
drip_amount      ['TD.TO']

[Drip Amount From Dividends]    29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   drip amount:7691.4,buy shares:90,per payout:0.96,cost per share:85.46
```
<br />

### Data from cache

To query cost of shares from a local cached file called `dividends_list.csv`

Contents of the file
```python
TD.TO
XEI.TO
```

Command issued
```python
python get_market_data.py -t 
```

Output as follows from the input list of ticket symbols 
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     1
period_years     1
ticker_symbol    ['TD.TO','XEI.TO']


[Stock Price Now]               29-Dec-2023
-----------------------------------------------------------------------------------
TD.TO   85.62
XEI.TO  24.76
```
<br />

To query all recent market data of ticker symbols mentioned inside the cache

Contents of the file
```python
TD.TO
XEI.TO
```

Command issued
```python
python get_market_data.py -a 
```

Output as follows from the input list of ticket symbols 
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     1
period_years     1
show_all         True
ticker_symbol    ['TD.TO','XEI.TO']
dividends        ['TD.TO','XEI.TO']
drip_amount      ['TD.TO','XEI.TO']


[Stock Price Now]               29-Dec-2023
-----------------------------------------------------------------------------------
TD.TO   85.62
XEI.TO  24.76

[Mean Dividend]                 29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   per payout:0.96,total payout:2.88
XEI.TO  per payout:0.11,total payout:1.39

[Drip Amount From Dividends]    29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   drip amount:7696.35,buy shares:90,per payout:0.96,cost per share:85.52
XEI.TO  drip amount:5595.76,buy shares:226,per payout:0.11,cost per share:24.76
```
<br />

### Data from Specific Time

To get average dividends over a specific time interval, use -d switch along with optional start-year (-y) and optional interval (-i).
```python
python get_market_data.py -d TD.TO -y 3 -i 2
```
Here start-date: 3 year ago, averaged over interval: 2 years. See settings and time interval in front of `Mean Dividend`. Output as follows
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     3
period_years     2
dividends        ['TD.TO']

[Mean Dividend]                 29-Dec-2020 over the next 2 year(s) or 29-Dec-2022:
-----------------------------------------------------------------------------------
TD.TO   per payout:0.84,total payout:6.72
```
<br />

### Combining Switches

To get dividends and drip amount, use the -d and -r switch and don't have to specify the same ticker symbol more than once.
```python
python get_market_data.py -d -r TD.TO
```
Note that only one of the lists {-t, -d, -r} should have one or more ticker symbols in order for them to be copied into the other list. Here reinvestment/drip list copies the symbol into dividends list. Output as follows
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     1
period_years     1
dividends        ['TD.TO']
drip_amount      ['TD.TO']

[Mean Dividend]                 29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   per payout:0.96,total payout:2.88

[Drip Amount From Dividends]    29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   drip amount:7696.35,buy shares:90,per payout:0.96,cost per share:85.52
```
<br />

To get dividends and drip amount over a specific time:
```python
python get_market_data.py -d -r TD.TO -y 4
```
Dividend is different from the last example since start-date: 4 years ago and averaged over default `interval = start-date`. Drip amount is always based on the last 365 days. See settings and time interval in front of `Mean Dividend` and `Drip Amount`. Output as follows
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     4
period_years     4
dividends        ['TD.TO']
drip_amount      ['TD.TO']

[Mean Dividend]                 30-Dec-2019 over the next 4 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   per payout:0.85,total payout:12.71

[Drip Amount From Dividends]    29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   drip amount:7696.35,buy shares:90,per payout:0.96,cost per share:85.52
```
<br />

To get dividends and drip amount over a specific time interval:
```python
python get_market_data.py -d -r TD.TO -y 4 -i 2
```
Dividend changes due to shorter time interval, but drip is the same (last 365 days). See settings. Output as follows
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years     4
period_years     2
dividends        ['TD.TO']
drip_amount      ['TD.TO']

[Mean Dividend]                 30-Dec-2019 over the next 2 year(s) or 29-Dec-2021:
-----------------------------------------------------------------------------------
TD.TO   per payout:0.78,total payout:6.27

[Drip Amount From Dividends]    29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   drip amount:7694.1,buy shares:90,per payout:0.96,cost per share:85.49
```
<br />

### Breakdown

Enter the total of cash available and a list of ticker symbols to buy. The algorithm will try to maximize the dividends while also trying to keep a balance of the number of shares in order to not overly-invest in some stocks. This is using the -b switch. Work in progress. Output as follows
```python
python get_market_data.py -b 10000 VTI SCHD GOOG SPY VOO
```
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years    1
period_years    1
breakdown       ['10000', 'VTI', 'SCHD', 'GOOG', 'SPY', 'VOO']
amount  10000.0
tickerlist      ['VTI', 'SCHD', 'GOOG', 'SPY', 'VOO']
costs   [245.18, 77.0, 143.54, 494.35, 454.28]
divs    [0.85325, 0.6647500000000001, 0, 1.65825, 1.58925]
optimal weights: [0.2 0.2 0.2 0.2 0.2]
calculate_number_of_shares
VTI     8
SCHD    26
GOOG    14
SPY     4
VOO     4
```
<br />

### Expected Behaviour for Invalid Command

As said before, you can't use separate lists for cost and dividend and expect an empty -r list to be populated as well. Only one of {-t, -d, -r} should have a non empty list of ticker symbols, and then the other two will be the same as that one. Invalid command:
```python
python get_market_data.py -t TD.TO -d XEI.TO -r
```
```bash
Settings as follows:
-----------------------------------------------------------------------------------
last_n_years    1
period_years    1
ticker_symbol   ['TD.TO']
dividends       ['XEI.TO']
drip_amount     []

[Stock Price Now]               29-Dec-2023
-----------------------------------------------------------------------------------
TD.TO   85.62
XEI.TO  24.76

[Mean Dividend]                 29-Dec-2022 over the next 1 year(s) or 29-Dec-2023:
-----------------------------------------------------------------------------------
TD.TO   per payout:0.96,total payout:2.88
XEI.TO  per payout:0.11,total payout:1.39
```
<br />

Correction to the above

Remove the `-r`
```python
python get_market_data.py -t TD.TO -d XEI.TO
```
Output is the same as above

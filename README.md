# Investments

## Using the script
<br />

### Setup

* sign up for yahoo API called api-dojo and get the private key, https://rapidapi.com/manwilbahaa/api/yahoo-finance127/
* make a new file called `private_keys.py` and use the private key above to set the header content
* optional: create a new file called `dividends_list.csv` and put all the ticker symbols there to query the price for
<br />

### Usage

To setup the header content in the file and save it in the same directory as the script:
```python
headers = {
	'x-rapidapi-key': "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
	'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
}
```
<br />

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
show_all        False
breakdown       False
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

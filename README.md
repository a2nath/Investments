# Investments
Investment Scripts

## Using the script: get_market_data.py

### Setup

* sign up for yahoo API called api-dojo and get the private key, https://rapidapi.com/manwilbahaa/api/yahoo-finance127/
* make a new file called `private_keys.py` and use the private key above to set the header content
* optional: create a new file called `dividends_list.csv` and put all the ticker symbols there to query the price for

### Usage

To setup the header content in the file and save it in the same directory as the script:
```python
headers = {
	'x-rapidapi-key': "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
	'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
}
```

To get the price of a ticker symbol use the -t switch

```python
python get_market_data.py -t TD.TO
```
Output as follows
```bash
Settings as follows:
-------------------------------------------------------
ticker_symbol    ['TD.TO']
last_n_years     1
period_years     1
Stock price now  2023-12-28 14:32:31.980999
-------------------------------------------------------
TD.TO   85.25
```
To get average dividends over time, use -d switch. Default is 1 year average since last year or 1 year ago (def: 1 year/1 year)
```python
python get_market_data.py -d TD.TO
```
Output as follows
```bash
Settings as follows:
-------------------------------------------------------
dividends        ['TD.TO']
last_n_years     1
period_years     1

Mean dividend over 1 year(s) since 1 year(s):
-------------------------------------------------------
TD.TO   0.96
```
To get drip amount, use the -r switch. Amount is based on 1 year average since last year or 1 year ago (def: 1 year/1 year).

```python
python get_market_data.py -r TD.TO
```
Output as follows
```bash
Settings as follows:
-------------------------------------------------------
drip_amount      ['TD.TO']
last_n_years     1
period_years     1

Drip amount from dividends over 1 year(s) since 1 year(s):
-------------------------------------------------------
TD.TO   7587.25

```

However, you can set the window of time (in years), using -i switch, and starting year, using -y switch, to compute the average dividend over, by both switches -d and -r for the same ticker symbol

```python
python get_market_data.py -d TD.TO -y 4 -i 3 -r TD.TO
```
This makes sense compared to the earlier result because the dividend was smaller back then but the computation on today price makes the reinvestment amount higher than before. Output as follows
```bash
Settings as follows:
-------------------------------------------------------
ticker_symbol    None
dividends        ['TD.TO']
last_n_years     4
period_years     3
drip_amount      ['TD.TO']

Mean dividend over 3 year(s) since 4 year(s):
-------------------------------------------------------
TD.TO   0.82

Drip amount from dividends over 3 year(s) since 4 year(s):
-------------------------------------------------------
TD.TO   8951.25
```
In case you're not comfortable computing the drip amount to start investing in a security based on the 1 year dividend information, this new amount might help mitigate risk of your security falling out of drip.

# SAIFFuturesArbitrage
SAIF Futures Quantitative Course I - Course Project - Futures Arbitrage

## Description
The system aims to back test Futures arbitrage strategty for China commodity futures trading. Basic philosophy is to identify the price gap between main contract and sub-main contract.

## Design requirements:
1. Data extraction and cleaning
  	- Extract historical market data for **all** products. (e.g. 橡胶，螺纹钢，铜，股指期货IC，IH，IF... etc)
  	- The granularity of the market data should be at least as finer as **minute-wise**. 
  	- Market data cleaning must be done pior to algorithm implementation so that we'll have main contract market data align with that of the sub-main contract.      
  	- Overall back testing cycle should be from the data of past **6** months.
2. Data processing algorithm
  	- Calculate the price gap between main contract and sub-main contract for each discrete point (**close price** for a certain minute) , denote the gap as priceDelta
  	- Calculate **MA** of priceDelta for past 20 units (minutes), denote as MA20
  	- Calculate **SD** of priceDelta for past 20 units (minutes), denote as SD
  	- Generate a band with upper as SDx2, middle as MA20, and lower as SDx-2
3. Arbitrage algorithm
	- Order shall be placed for current main contract
  	- Open buy when price hits the lower bound, and close sell when it regresses to middle.
  	- Open sell when price hits the upper bound and buy close when it regresses to middle. 
4. Back testing statistics
	- Based on the behavior described in **3**, filter out those don't follow the strategy which leaves the ones applicable for arbitraging.
	- Calculate the statistics, net value, sharpe ... etc(TBD)
	- Generate the report (TBD)

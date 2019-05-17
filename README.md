# The VanAurum Open Robo-Advisor

This is an open source initiative to make available the tools required for building your own optimal Markowitz portfolios and finding the best rebalancing strategy factoring in your transaction costs. The financial world is moving towards zero cost ETFs, which make even the lowest-cost robo-advisors in the industry seem expensive.  

The mission of this project is to put industry leading portfolio management tools into the hands of individuals for zero cost.


## Algorithmic Portfolio Optimization

#### Example 1: Building a portfolio of 5 assets from a list of 9 assets. No additional contraints

```Python
from roboadvisor.optimizer import PortfolioOptimizer

assets=['TLT','SPY','GDX','AAPL','FXI','GLD','VDE','UUP','VT']
optimal_portfolio=PortfolioOptimizer(assets, portfolio_size=5,max_pos=1.0, min_pos=0.0)
```

#### Output...

```
...Maximum position size: 100%
...Minimum position size: 0%
...Number of unique asset combinations: 126
...Analyzing 126 of 126 asset combinations...
...Omitted assets: []

-----------------------------------------------
----- Portfolio Optimized for Sharpe Ratio ----
-----------------------------------------------

('TLT', 0.3207)
('SPY', 0.1373)
('AAPL', 0.1723)
('GLD', 0.0711)
('UUP', 0.2987)

Optimal Portfolio Return: 7.4065
Optimal Portfolio Volatility: 7.1075
Optimal Portfolio Sharpe Ratio: 1.0421

-----------------------------------------------
----- Portfolio Optimized for Pure Return -----
-----------------------------------------------

('AAPL', 1.0)
('GLD', 0.0)
('VDE', 0.0)
('UUP', 0.0)
('VT', 0.0)

Optimal Portfolio Return: 22.6168
Optimal Portfolio Volatility: 29.8647
Optimal Portfolio Sharpe Ratio: 0.7573

-----------------------------------------------------
----- Portfolio Optimized for Minimal Volatility ----
-----------------------------------------------------

('TLT', 0.1644)
('SPY', 0.0)
('GLD', 0.1268)
('UUP', 0.5449)
('VT', 0.1638)
Optimal Portfolio Return: 2.755
Optimal Portfolio Volatility: 4.651
Optimal Portfolio Sharpe Ratio: 0.5924
```

#### Example 2: Building a portfolio of 5 assets from a list of 12 assets with constraints.

In this example we're going to constrain the maximum position size of a single asset to be 30%, and the minumum size to be 5%.

```Python
assets=['TLT','SPY','GDX','AAPL','FXI','GLD','VDE','UUP','VT','IYF','EWI','TIP']
optimal_portfolio=PortfolioOptimizer(assets, portfolio_size=5,max_pos=0.30, min_pos=0.05)
```

#### Output...
```
...Maximum position size: 30%
...Minimum position size: 5%
...Number of unique asset combinations: 792
...Analyzing 792 of 792 asset combinations...
...Omitted assets: []

-----------------------------------------------
----- Portfolio Optimized for Sharpe Ratio ----
-----------------------------------------------

('TLT', 0.1981)
('SPY', 0.1089)
('AAPL', 0.1495)
('UUP', 0.2435)
('TIP', 0.3)

Optimal Portfolio Return: 6.5281
Optimal Portfolio Volatility: 6.1652
Optimal Portfolio Sharpe Ratio: 1.0589

-----------------------------------------------
----- Portfolio Optimized for Pure Return -----
-----------------------------------------------

('TLT', 0.05)
('SPY', 0.3)
('AAPL', 0.3)
('VT', 0.05)
('IYF', 0.3)

Optimal Portfolio Return: 12.1792
Optimal Portfolio Volatility: 21.8554
Optimal Portfolio Sharpe Ratio: 0.5573

-----------------------------------------------------
----- Portfolio Optimized for Minimal Volatility ----
-----------------------------------------------------

('TLT', 0.1276)
('SPY', 0.1693)
('GLD', 0.1031)
('UUP', 0.3)
('TIP', 0.3)

Optimal Portfolio Return: 3.6682
Optimal Portfolio Volatility: 4.3676
Optimal Portfolio Sharpe Ratio: 0.8399
```
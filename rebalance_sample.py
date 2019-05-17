from roboadvisor.rebalancer import RebalancingSimulator
from roboadvisor.optimizer import PortfolioOptimizer

portfolio=PortfolioOptimizer(['GLD','SPY','TLT','QQQ','XLI'],portfolio_size=5, max_pos=0.3, min_pos=0.05)
rebalancer=RebalancingSimulator(portfolio,frac_units=False,trade_cost=5.99,starting_cash=20000,max_thresh=1.1, min_thresh=0.9)
rebalancer.run_simulation()
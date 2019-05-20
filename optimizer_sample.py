from roboadvisor.optimizer import PortfolioOptimizer


if __name__=='__main__':

    assets=['TLT','SPY','GDX','AAPL','FXI','GLD','VDE','UUP','VT','IYF','EWI','TIP']
    optimal_portfolio=PortfolioOptimizer(assets, portfolio_size=5,max_pos=0.30, min_pos=0.05)
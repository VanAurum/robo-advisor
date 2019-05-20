"""
@author: Kevin Vecmanis
"""
#Standard Python library imports
import unittest
import numpy as np

#3rd party imports
from quandl.errors.quandl_error import AuthenticationError
from quandl.errors.quandl_error import NotFoundError 

#Local imports
from roboadvisor.optimizer import PortfolioOptimizer
from config.config import QUANDL_KEY

'''
        asset_basket_ - the list of assets in its entirety
        asset_errors_ - the number of stock tickers that weren't found on Quandl.
        cov_matrix_results - list of the covariance matrices for each unique asset combination.
        return_matrix_results - list of the return matrices for each unique asset combination.
        asset_combo_list - list of all the unique asset combinations.
        max_iters_ - number of portfolio combinations to analyze
        portfolio_size_ - the number of assets that can be used in the optimal portfolio
        assets_ - instantiation of an attribute to be used during optimization
        risk_tolerance - maximum volatality client is will to incur. 1.0 = 100%
        raw_asset_data - a master copy of the adjusted close dataframe from our quandl query.
        auth_token - Quandl authentication token
        sim_iterations - the number of random portfolio weights to simulate for each asset combination.
        sim_packages - a master queue of all the asset combinations and corresponding data to be analyzed.
        _sharpe_ - local variable for storing and passing sharpe score
        _port_return_ - local variable for storing and passing portfolio return
        _port_vol_ - local variable for storing and passing portfolio volatility
        portfolio_stats_ - list portfolio stats for a given asset combo and weight.
        sharpe_scores_ - comphrehensive matrix of simulation results for sharpe optimization
        return_scores_ - comphrehensive matrix of simulation results for return optimization
        vol_scores - comphrehensive matrix of simulation results for colatility optimization
'''

class TestPortfolioManager(unittest.TestCase):
    
    assets = ['GDX', 'GLD', 'SPY', 'XLI', 'VDE', 'AAPL', 'MSFT', '12345', 'XXXXX']
    auth_token = QUANDL_KEY       
    pmo = PortfolioOptimizer(assets, auth_token, print_init=True)
        
    def test_init(self):
        '''Test initialization of PortfolopOptimizer class
        '''     
        self.assertLessEqual(self.pmo.max_pos_, 1.0)
        self.assertGreaterEqual(self.pmo.max_pos_, 0.0)
        self.assertLess(self.pmo.min_pos_, 1.0)
        self.assertGreaterEqual(self.pmo.min_pos_, 0.0)
        self.assertLessEqual(self.pmo.portfolio_size_, len(self.pmo.asset_basket_))   
            
    def test_fetch_data_01(self):
        '''Test fetch_data method
        '''
        self.pmo.auth_token_ = 'a'
        self.assertRaises(AuthenticationError, self.pmo._fetch_data())
        self.pmo._fetch_data()
        self.assertFalse(self.pmo.raw_asset_data.isnull().any().any()) 
        self.assertIsNotNone(self.pmo.sim_packages)
        self.pmo.auth_token_ = self.auth_token
        
    def test_fetch_data_02(self):
        """Test that invalid stock tickers raise NotFoundError
        """
        self.assertRaises(NotFoundError,self.pmo._fetch_data()) 
        
    def test_portfolio_simulation(self): 
        """Test that random weights add to 1.0
        """
        weights=np.random.dirichlet(np.ones(self.pmo.portfolio_size_), size=1)
        expected=sum(weights[0])
        self.assertAlmostEqual(expected, 1.0)        
        
    def test_optimize_for_sharpe(self):
        print('Testing _optimize_for_sharpe') 
            

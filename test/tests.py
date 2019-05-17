"""
@author: Kevin Vecmanis
"""

import vm_portfolio_manager_r1 as pm
import unittest

class TestPortfolioManager(unittest.TestCase):
    
    
    def setUp(self):
        
        assets=['GDX','GLD','SPY','XLI','VDE','AAPL','MSFT']
        auth_token="eecWhzC3y1A6ukinBsP_"        
        self.pmo=pm.PortfolioOptimizer(assets,auth_token,print_init=True)
        
    
    def test_init(self):
        
        print('Testing _init__')         
        self.assertLessEqual(self.pmo.max_pos_,1.0)
        self.assertGreaterEqual(self.pmo.max_pos_,0.0)
        self.assertLess(self.pmo.min_pos_,1.0)
        self.assertGreaterEqual(self.pmo.min_pos_,0.0)
        self.assertLessEqual(self.pmo.portfolio_size_,len(self.pmo.asset_basket_))
        
        
    def test_fetch_data_01(self):
        
        from quandl.errors.quandl_error import AuthenticationError
        
        print('Testing _fetch_data') 
        self.assertRaises(AuthenticationError,self.pmo._fetch_data(auth_token='a'))
        self.pmo._fetch_data()
        self.assertFalse(self.pmo.raw_asset_data.isnull().any().any()) 
        self.assertIsNotNone(self.pmo.sim_packages)
        
        
    def test_fetch_data_02(self):
        
        """Test that invalid stock tickers raise NotFoundError"""
        
        from quandl.errors.quandl_error import NotFoundError        
        print('Testing _fetch_data') 
        self.pmo.asset_basket_=['XXXXXX','XXXXXX']
        self.assertRaises(NotFoundError,self.pmo._fetch_data()) 
        
    def test_portfolio_simulation(self):
        
        """Test that random weights add to 1.0"""
        
        import numpy as np
        weights=np.random.dirichlet(np.ones(self.pmo.portfolio_size_),size=1)
        expected=sum(weights[0])
        self.assertAlmostEqual(expected,1.0)        
        
        
    def test_optimize_for_sharpe(self):
        print('Testing _optimize_for_sharpe') 
            

        
if __name__=="__main__":

    unittest.main()  
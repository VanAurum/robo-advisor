'''
@author: Kevin Vecmanis
'''
#Standard Python libary imports
import matplotlib
import pandas as pd
import numpy as np
import time
import random
from itertools import combinations
import scipy.optimize as optimize
import numpy as np
from operator import itemgetter

#Local imports
from config import config

#3rd party imports
import quandl as q
from quandl.errors.quandl_error import NotFoundError 



class PortfolioOptimizer:
    '''
    This class object receives a list of assets (tickers) and a portfolio size
    and returns the optimal portfolio optimized for Sharpe, Pure Return, and 
    Volatility

    Parameters:
    -----------
        assets : list 
            A list of stock tickers that the optimizer should choose from the build the portfolio.
        risk_tolerance: float, optional (default=5.0)
            A number on a scale of 1.0 to 10.0 that indicates the acceptable risk level. 
        portfolio_size: int, optional (default=5)
            The number of assets that should be in the final optimal portfolio. 
        max_iters: int, optional (default=None)
            The number of times the portfolio simulation should be run by the optimizer.
        print_init : bool, optional (default=True)
            Whether or not to print the portfolio metrics after initialization.
        max_pos : float, optional (default=1.0)
            The maximum weight that one asset can occupy in a portfolio.  
        min_pos : float, optional (default=0.0)
            The minimum weight that one asset can occupy in a portfolio.

    Attributes:
    ------------    
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
        
    Methods:
    -------------    
        _fetch_data - Get data from quandl using the list of assets in asset_basket
        _plot_asset_prices - plot the normalized adjusted closes for all the assets.
        portfolio_simulation - simulate and plot markowitz bullet for one specified asset combination.
        portfolio_stats - calculates performance metrics for one set of weights on one asset combination.
        optimize_for_sharpe - Finds the optimal portfolio that provides best Sharpe ratio
        optimize_for_return - Finds the optimal portfolio that provides the best Return.
        optimize_for_volatility - Finds the optimal portfolio that provides the smallest volatility.      
    '''
    
    def __init__(self,
                 assets,
                 risk_tolerance=5.0,
                 portfolio_size=5,
                 max_iters=None, 
                 print_init=True, 
                 max_pos=1.0,
                 min_pos=0.0):
        
        '''
        Initiation calls four functions and instatiates 7 attributes.
        '''
        matplotlib.use('PS')
        self.max_pos_=max_pos
        self.min_pos_=min_pos
        self.print_init_=print_init
        self.asset_basket_=assets
        self.max_iters_=max_iters
        self.portfolio_size_=portfolio_size
        self.assets_=assets
        self.num_assets_=portfolio_size
        self.risk_tolerance_=risk_tolerance
        self.auth_token_=config.QUANDL_KEY
        self.sim_iterations_=2500
        self._fetch_data()
        self.optimize_for_sharpe()
        self.optimize_for_return()
        self.optimize_for_volatility()
          
        
    def _fetch_data(self):
    
        '''
        this function inherits the class and declares additional class attributes
        pertaining to the data we'll need for analysis.  We fetch data from quandl and 
        declare the following class attributes. sim_packages gets passed to our optimization
        functions where it gets iterated through during analysis.
        
        asset_errors_
        asset_combos_
        raw_asset_data
        sim_packages
        
        Returns: 
            
            None
        '''
 
        start=time.time()
        count=0
        auth_tok = self.auth_token_

        self.asset_errors_=[]
        self.cov_matrix_results=[]
        self.return_matrix_results=[]
        self.asset_combo_list=[]
                  
        #instatiate an empty dataframe
        df=pd.DataFrame()
        
        #Because we will potentially be merging multiple tickers, we want to rename
        #all of the income column names so that they can be identified by their ticker name.
        
        for asset in self.asset_basket_:        
            if (count==0):      
                try:      
                    df=q.get('EOD/'+asset, authtoken=auth_tok)                      
                    column_names=list(df)
                    for i in range(len(column_names)):
                        column_names[i]=asset+'_'+column_names[i]
                    df.columns=column_names   
                    count+=1                 
                except NotFoundError:
                    self.asset_errors_.append(asset)                               
            else:           
                try:     
                    temp = q.get('EOD/'+asset, authtoken=auth_tok)       
                    column_names=list(temp)
                    for i in range(len(column_names)):
                        column_names[i]=asset+'_'+column_names[i]                 
                    temp.columns=column_names
                    df=pd.merge(df,temp,how='outer',left_index=True, right_index=True)            
                except NotFoundError:
                    self.asset_errors_.append(asset)      

        df=df.dropna()
        
        features=[f for f in list(df) if "Adj_Close" in f]
        df=df[features]
        self.raw_asset_data=df.copy()
        self.asset_combos_=list([combo for combo in combinations(features, self.portfolio_size_)])
        print('Number of unique asset combinations: ', len(self.asset_combos_))
        
        if (self.max_iters_==None):
            self.max_iters_=len(self.asset_combos_)
        
        elif (len(self.asset_combos_) < self.max_iters_):            
            self.max_iters_=len(self.asset_combos_)
            
        
        print('Analyzing '+str(self.max_iters_)+' of '+str(len(self.asset_combos_))+' asset combinations...')
        
        self.sim_packages=[]
        
        for i in range(self.max_iters_):
            
            assets=list(self.asset_combos_[i])        
            filtered_df=df[assets].copy()
            returns=np.log(filtered_df/filtered_df.shift(1))
            return_matrix=returns.mean()*252
            cov_matrix=returns.cov()*252
            self.num_assets_=len(assets)
            self.sim_packages.append([assets,cov_matrix,return_matrix])
        
        
        print('Omitted assets: ',self.asset_errors_)
        print('---')
        print('Time to fetch data: %.2f seconds' % (time.time() - start))
        print('---')
        
        return
    
    
    def portfolio_simulation(self):
        '''
        Runs a simulation by randomly selecting portfolio weights a specified
        number of times (iterations), returns the list of results and plots 
        all the portfolios as well.
        
        Returns:
        _________
        
        port_returns: array, array of all the simulated portfolio returns.
        port_vols: array, array of all the simulated portfolio volatilities.
        '''
        
        start=time.time()
        iterations=self.sim_iterations_
        
        self.simulation_results=[]
        
        #Take a copy of simulation packages so that the original copy isn't altered
        sim_packages=self.sim_packages.copy()
        
        #Loop through each return and covariance matrix from all the asset combos.
        for i in range(len(self.sim_packages)):
            
            #pop a simulation package and load returns, cov_matrix, and asset list from it.
            sim=sim_packages.pop()
            returns=np.array(sim[2])
            cov_matrix=np.array(sim[1])
            assets=sim[0]
                       
            port_sharpes=[]
            port_returns=[]
            port_vols=[]
                        
            for i in range (iterations):
                weights=np.random.dirichlet(np.ones(self.num_assets_),size=1)
                weights=weights[0]
                ret=np.sum(returns*weights)
                vol=np.sqrt(np.dot(weights.T,np.dot(cov_matrix,weights)))
                port_returns.append(ret)
                port_vols.append(vol)
                port_sharpes.append(ret/vol)
            
            #Declare additional class attributes from the results
            port_returns=np.array(port_returns)
            port_vols=np.array(port_vols)
            port_sharpes=np.array(port_sharpes)            
            self.simulation_results.append([assets,port_returns,port_vols,port_sharpes])
     
        
        print('---')
        print('Time to simulate portfolios: %.2f seconds' % (time.time() - start))
        print('---')
        
        return



    def portfolio_stats(self,weights):
    
        '''
        We can gather the portfolio performance metrics for a specific set of weights.
        This function will be important because we'll want to pass it to an optmization
        function - either Hyperopt or Scipy SCO to get the portfolio with the best
        desired characteristics.
        
        Note: Sharpe ratio here uses a risk-free short rate of 0.
        
        Paramaters: 
        __________
        
        
        weights: array, asset weights in the portfolio.
        
        Returns: 
        ___________
        
        array, portfolio statistics - mean, volatility, sharp ratio.
        
        '''
                        
        returns=self.return_matrix_
        cov_matrix=self.cov_matrix_
        
        #Convert to array in case list was passed instead.
        weights=np.array(weights)
        port_return=np.sum(returns*weights)
        port_vol=np.sqrt(np.dot(weights.T,np.dot(cov_matrix,weights)))
        sharpe=port_return/port_vol
        self._sharpe_=sharpe
        self._port_return_=port_return
        self._port_vol_=port_vol     
        
        stats=[port_return,port_vol,sharpe]        
        self.portfolio_stats_=np.array(stats)
        
        return np.array(stats)

    
    
    def optimize_for_sharpe(self):
         
        min_con=self.min_pos_
        max_con=self.max_pos_
        
        num_assets=self.portfolio_size_       
        constraints=({'type':'eq', 'fun': lambda x: np.sum(x) -1})
        bounds= tuple((min_con,max_con) for x in range(num_assets))
        initializer=num_assets * [1./num_assets,]
        sim_packages=self.sim_packages.copy()
            
        def _maximize_sharpe(weights):
             
            self.portfolio_stats(weights)
            sharpe=self._sharpe_
               
            return -sharpe
           
        self.sharpe_scores_=[]

        for i in range(len(sim_packages)):

            sim=sim_packages.pop()
            self.return_matrix_=np.array(sim[2])
            self.cov_matrix_=np.array(sim[1])
            self.assets_=sim[0]
            
            optimal_sharpe=optimize.minimize(_maximize_sharpe,
                                             initializer,
                                             method='SLSQP',
                                             bounds=bounds,
                                             constraints=constraints)
            
            optimal_sharpe_weights_=optimal_sharpe['x'].round(4)
            optimal_sharpe_stats_=self.portfolio_stats(optimal_sharpe_weights_)
            
            #Here we just stripe our the 'Adj_close' tag from the asset list
            x=self.assets_
            asset_list=[]
            for i in range(len(x)):
                temp=x[i].split('_')
                asset_list.append(temp[0])            
            
            optimal_sharpe_portfolio_=list(zip(asset_list,list(optimal_sharpe_weights_)))
            self.sharpe_scores_.append([optimal_sharpe_weights_,
                                        optimal_sharpe_portfolio_,
                                        round(optimal_sharpe_stats_[0]*100,4),
                                        round(optimal_sharpe_stats_[1]*100,4),
                                        round(optimal_sharpe_stats_[2],4)])
        
        self.sharpe_scores_=sorted(self.sharpe_scores_, key = itemgetter(4),reverse=True)
        self.best_sharpe_portfolio_=self.sharpe_scores_[0]
        temp=self.best_sharpe_portfolio_
        
        print('-----------------------------------------------')
        print('----- Portfolio Optimized for Sharpe Ratio ----')
        print('-----------------------------------------------')
        print('')
        print(*temp[1], sep='\n')
        print('')
        print('Optimal Portfolio Return: ', temp[2])
        print('Optimal Portfolio Volatility: ', temp[3])
        print('Optimal Portfolio Sharpe Ratio: ', temp[4])
        print('')
        print('')
        

    def optimize_for_return(self):
        
        num_assets=self.portfolio_size_       
        constraints=({'type':'eq', 'fun': lambda x: np.sum(x) -1})
        bounds= tuple((0,1) for x in range(num_assets))
        initializer=num_assets * [1./num_assets,]
        sim_packages=self.sim_packages.copy()
         
        def _maximize_return(weights):
             
            self.portfolio_stats(weights)
            port_return=self._port_return_
               
            return -port_return
        
        self.return_scores_=[]
        for i in range(len(sim_packages)):

            sim=sim_packages.pop()
            self.return_matrix_=np.array(sim[2])
            self.cov_matrix_=np.array(sim[1])
            self.assets_=sim[0]
            
            optimal_return=optimize.minimize(_maximize_return,
                                             initializer,
                                             method='SLSQP',
                                             bounds=bounds,
                                             constraints=constraints)
            
            optimal_return_weights_=optimal_return['x'].round(4)
            optimal_return_stats_=self.portfolio_stats(optimal_return_weights_)
            
            #Here we just stripe our the 'Adj_close' tag from the asset list
            x=self.assets_
            asset_list=[]
            for i in range(len(x)):
                temp=x[i].split('_')
                asset_list.append(temp[0])
                
            optimal_return_portfolio_=list(zip(asset_list,list(optimal_return_weights_)))
            self.return_scores_.append([optimal_return_weights_,
                                        optimal_return_portfolio_,
                                        round(optimal_return_stats_[0]*100,4),
                                        round(optimal_return_stats_[1]*100,4),
                                        round(optimal_return_stats_[2],4)])
        
        self.return_scores_=sorted(self.return_scores_, key = itemgetter(2),reverse=True)
        self.best_return_portfolio_=self.return_scores_[0]
        temp=self.best_return_portfolio_
        
        if (self.print_init_==True):
        
            print('-----------------------------------------------')
            print('----- Portfolio Optimized for Pure Return ----')
            print('-----------------------------------------------')
            print('')
            print(*temp[1], sep='\n')
            print('')
            print('Optimal Portfolio Return: ', temp[2])
            print('Optimal Portfolio Volatility: ', temp[3])
            print('Optimal Portfolio Sharpe Ratio: ', temp[4])
            print('')
            print('')
    

    def optimize_for_volatility(self):
        
        num_assets=self.portfolio_size_       
        constraints=({'type':'eq', 'fun': lambda x: np.sum(x) -1})
        bounds= tuple((0,1) for x in range(num_assets))
        initializer=num_assets * [1./num_assets,]
        sim_packages=self.sim_packages.copy()
        
        
        def _minimize_volatility(weights):
             
            self.portfolio_stats(weights)
            port_vol=self._port_vol_
               
            return port_vol
        
        
        self.vol_scores_=[]
        for i in range(len(sim_packages)):

            sim=sim_packages.pop()
            self.return_matrix_=np.array(sim[2])
            self.cov_matrix_=np.array(sim[1])
            self.assets_=sim[0]
            
            optimal_vol=optimize.minimize(_minimize_volatility,
                                          initializer,
                                          method='SLSQP',
                                          bounds=bounds,
                                          constraints=constraints)
            
            optimal_vol_weights_=optimal_vol['x'].round(4)
            optimal_vol_stats_=self.portfolio_stats(optimal_vol_weights_)
            
            #Here we just stripe our the 'Adj_close' tag from the asset list
            x=self.assets_
            asset_list=[]
            for i in range(len(x)):
                temp=x[i].split('_')
                asset_list.append(temp[0])
                
            optimal_vol_portfolio_=list(zip(asset_list,list(optimal_vol_weights_)))
            self.vol_scores_.append([optimal_vol_weights_,
                                     optimal_vol_portfolio_,
                                     round(optimal_vol_stats_[0]*100,4),
                                     round(optimal_vol_stats_[1]*100,4),
                                     round(optimal_vol_stats_[2],4)])
        
        self.vol_scores_=sorted(self.vol_scores_, key = itemgetter(3))
        self.best_vol_portfolio_=self.vol_scores_[0]
        temp=self.best_vol_portfolio_

        if (self.print_init_==True):
            
            print('-----------------------------------------------------')
            print('----- Portfolio Optimized for Minimal Volatility ----')
            print('-----------------------------------------------------')
            print('')
            print(*temp[1], sep='\n')
            print('')
            print('Optimal Portfolio Return: ', temp[2])
            print('Optimal Portfolio Volatility: ', temp[3])
            print('Optimal Portfolio Sharpe Ratio: ', temp[4])
            print('')
            print('')  
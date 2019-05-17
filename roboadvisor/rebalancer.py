'''
@author: Kevin Vecmanis
'''


class RebalancingSimulator:
    
    
    def __init__(self,p,frac_units=True,portfolio_value=20000,trade_cost=5):
        
        import numpy as np
        self.thresh_high_=1.1
        self.thresh_low_=0.9
        self.trade_cost_=trade_cost
        self.optimal_portfolio_=p
        self.frac_units_=frac_units
        self.starting_portfolio_value_=portfolio_value       
        self._data_prep()
        #self.cash_balance_=self.starting_portfolio_value_
        self.starting_cash_balance_=portfolio_value
        self._initialize_portfolio()
        self.random_walk_iters_=2520

        
        print('Cash balance after portfolio initialization: ',self.starting_residual_cash)
        
        

    def _data_prep(self):
        
        import numpy as np
        
        sharpe_port=self.optimal_portfolio_.best_sharpe_portfolio_
        df=self.optimal_portfolio_.raw_asset_data.copy()    
        
        #Drop assets from the optimal portfolio that have too small
        #of a weight
        optimal_port=sharpe_port[1]
        optimal_port=list(filter(lambda a: a[1] > 0.001, optimal_port))
        asset_list=[x[0] for x in optimal_port]      
        weights=[x[1] for x in optimal_port]  
          
        df=df.loc[:, df.columns.str.contains('|'.join(asset_list))]
        df.columns=[asset_list]  
        latest=df.tail(1)
        
        starting_vals=[]
        count=0
        
        for asset in asset_list:
            
            asset_ret=np.log(df[asset]/df[asset].shift(1)).mean().values[0]
            asset_vol=np.log(df[asset]/df[asset].shift(1)).std().values[0]        
            starting_vals.append([asset,
                                  latest[asset].values[0][0],
                                  round(asset_ret,5),
                                  round(asset_vol,5),
                                  weights[count]])
            count+=1
        
        self.starting_vals_=starting_vals 
        self.target_weights_=weights
        self.asset_list_=[x[0] for x in self.starting_vals_]
        print('Target weights: ', list(zip(self.asset_list_,self.target_weights_)))
        
        return   
    
    
    def _initialize_portfolio(self):
    
        #initialize portfolio:
        starting_vals=self.starting_vals_
        trade_cost=self.trade_cost_
        portfolio_init=[]
        self.starting_residual_cash=self.starting_portfolio_value_
        
        for i in range(len(starting_vals)):
            
            allocated_capital=round(starting_vals[i][4]*self.starting_portfolio_value_,4)
            start_price=starting_vals[i][1]
            
            if (self.frac_units_==True):
                num_units=(allocated_capital-trade_cost)/start_price
                cash_used=num_units*start_price
                self.starting_residual_cash=self.starting_residual_cash-cash_used
                self.starting_residual_cash=round(self.starting_residual_cash,4)
                
            else:
                num_units=(allocated_capital-trade_cost)//start_price
                cash_used=num_units*start_price
                self.starting_residual_cash=self.starting_residual_cash-cash_used
                self.starting_residual_cash=round(self.starting_residual_cash,4)
                
            portfolio_init.append((starting_vals[i][0],round(num_units,4)))
        
        self.starting_unit_holdings_=[x[1] for x in portfolio_init]
        self.initialized_portfolio_=portfolio_init
        #print('Unit holdings after initialization: ', self.initialized_portfolio_)
        
        return
    

    def _random_walks(self,plot=True):
    
        import matplotlib.pyplot as plt
        import numpy as np
        #using the historical mean daily return and volatility of each asset,
        #we're going to create random walks to simulatate returns for each asset
        #in the portfolio. 
        
        
        starting_vals=self.starting_vals_
        random_walks=[]

        for i in range(len(starting_vals)):
            
            S = starting_vals[i][1] #starting stock price
            T = self.random_walk_iters_ #Number of trading days in simulation
            mu = starting_vals[i][2] #Return
            vol = starting_vals[i][3] #Volatility
             
            #create list of daily returns using random normal distribution
            simulated_returns=np.random.normal(mu,vol,T)+1
            simulated_prices = [S]
     
            for x in simulated_returns:
                simulated_prices.append(simulated_prices[-1]*x)
            
            random_walks.append(simulated_prices)
        
        if (plot==True):
            plt.figure(figsize=(10,4))
            plt.title(starting_vals[i][0])
            plt.plot(simulated_prices)        
            plt.show()
        
        self.random_walks=random_walks
            
        return random_walks    
    
    
    def run_simulation(self):
        
        import matplotlib.pyplot as plt
        import time
        import statistics
        
        start=time.time()
        
        self.total_trades_=0
        
        portfolio_values=[]
        weight_history=[]
        unit_history=[]
        cash_history=[]
        trade_history=[]

        #starting_portfolio=self.initialized_portfolio_       
            
        price_simulations=self._random_walks(plot=False)
        self.current_unit_holdings_=self.starting_unit_holdings_
        self.sim_cash_balance_=self.cash_balance_
        
        for j in range(1,len(price_simulations[0])-1):
            
            #Get portfolio value and updated weights based on asset prices 
            #at current time step.
            self.current_unit_prices_=[item[j] for item in price_simulations]
            port_val, new_weights, weight_diffs, new_target_vals,unit_holdings,trade_count=self._get_portfolio_values()
            
            portfolio_values.append(port_val)
            weight_history.append(new_weights)
            unit_history.append(unit_holdings)
            cash_history.append(self.sim_cash_balance_)
            trade_history.append(trade_count)
        
        self.sim_port_vals_=portfolio_values
        self.sim_weight_vals_=weight_history
        self.sim_holding_history_=unit_history
        self.sim_cash_history_=cash_history
        self.sim_trade_history_=trade_history
        
        plt.figure(figsize=(12,4))
        plt.title('Simulated Portfolio Value')
        plt.plot(self.sim_port_vals_)        
        plt.show()   
        
        plt.figure(figsize=(12,4))
        plt.title('Simulation Cash Level')
        plt.plot(self.sim_cash_history_)        
        plt.show()    
        
        plt.figure(figsize=(12,4))
        plt.title('Simulation Trade History')
        plt.plot(self.sim_trade_history_)        
        plt.show()   
        
        plt.figure(figsize=(12,4))
        plt.title('Asset Weight History')
        for i in range(len(self.asset_list_)):
            trace=[x[i] for x in self.sim_weight_vals_]            
            plt.plot(trace,label=self.asset_list_[i])
        plt.legend()    
        plt.show()           

        
        self.total_trades_=sum(self.sim_trade_history_)
        self.total_trade_cost_=self.trade_cost_*self.total_trades_
        
        print('')
        print('')
        print('SIMULATION REPORT')
        print('-----------------')
        print('Rebalancing simulation finished in: %.2f seconds' % (time.time() - start))
        print('Total number of trades executed: ', self.total_trades_)
        print('Cost per trade: ', round(self.trade_cost_,2))
        print('Total trading costs: ', round(self.total_trade_cost_,2))
        print('Maximum cash balance: ', round(max(self.sim_cash_history_),2))
        print('Minimum cash balance: ', round(min(self.sim_cash_history_),2))
        print('Average cash balance: ', round((sum(self.sim_cash_history_)/len(self.sim_cash_history_)),2))
        print('Fractional units allowed? ',str(self.frac_units_))
        print('')
        
        for i in range(len(self.asset_list_)):
            weight_history=[x[i] for x in self.sim_weight_vals_]
            asset=self.asset_list_[i]
            print('Weight metrics for: ',asset)
            print('-------------------------')
            print('  Target portfolio weight: ',self.target_weights_[i])
            print('  Standard deviation of '+asset+' portfolio weight: ',round(statistics.stdev(weight_history),4))
            print('  Maximum weight reached for '+asset+': ', round(max(weight_history),4))
            print('  Minimum weight reached for '+asset+': ', round(min(weight_history),4))
            print('  Average of '+asset+' portfolio weight: ',round(statistics.mean(weight_history),4))
            print('')
        
        return    
    
    def reset_sim(self):
        
        self.current_unit_holdings_=[]
        self._initialize_portfolio()
        self.current_unit_holdings_=self.starting_unit_holdings_
        self.sim_cash_balance_=self.starting_residual_cash
        return


    def run_monte_carlo(self,iterations=1,print_report=False):
        
        import matplotlib.pyplot as plt
        import time
        import statistics
        
        start=time.time()
        self.sim_port_vals_=[]
        self.sim_weight_vals_=[]
        self.sim_holding_history_=[]
        self.sim_cash_history_=[]
        self.sim_trade_history_=[]
        self.reset_sim()

        
        for i in range(iterations):
            
            portfolio_values=[]
            weight_history=[]
            unit_history=[]
            cash_history=[]
            trade_history=[]
            #self.reset_sim()
       
            price_simulations=self._random_walks(plot=False)
            
            for j in range(1,len(price_simulations[0])-1):
                
                #Get portfolio value and updated weights based on asset prices 
                #at current time step.
                self.current_unit_prices_=[item[j] for item in price_simulations]
                port_val, new_weights, weight_diffs, new_target_vals,unit_holdings,trade_count=self._get_portfolio_values()
                
                portfolio_values.append(port_val)
                weight_history.append(new_weights)
                unit_history.append(unit_holdings)
                cash_history.append(self.sim_cash_balance_)
                trade_history.append(trade_count)
            
            self.sim_port_vals_.append(portfolio_values)
            self.sim_weight_vals_.append(weight_history)
            self.sim_holding_history_.append(unit_history)
            self.sim_cash_history_.append(cash_history)
            self.sim_trade_history_.append(trade_history)
            self.reset_sim()

        if (print_report==True):
            self._plot_sim_results()

    
    def _calculate_sim_metrics(self):
        
        import statistics
        #Weight metrics:
        
        #Get Terminal Portfolio Metrics
        self.term_port_vals_=[]
        for i in range(len(self.sim_port_vals_)):
            self.term_port_vals_.append(self.sim_port_vals_[i][-1])
        
        self.term_val_mean_=round(statistics.mean(self.term_port_vals_),4)
        self.term_val_std_=round(statistics.stdev(self.term_port_vals_),4)
        
        #Get Terminal Trade Statistics
        self.sim_trade_sums_=[]
        self.sim_trade_costs_=[]
        for i in range(len(self.sim_trade_history_)):
            self.sim_trade_sums_.append(sum(self.sim_trade_history_[i]))
            self.sim_trade_costs_.append(sum(self.sim_trade_history_[i])*self.trade_cost_)
                   
        self.trade_sum_mean_=round(statistics.mean(self.sim_trade_sums_),4)
        self.trade_sum_std_=round(statistics.stdev(self.sim_trade_sums_),4)
        self.sim_trade_cost_mean_=round(statistics.mean(self.sim_trade_costs_),4)
        self.sim_trade_cost_std_=round(statistics.stdev(self.sim_trade_costs_),4)   
        
        n_samples=len(self.term_port_vals_)
        
        print('Portfolio Simulation Analytics')
        print('--------------------------------')
        print('Simulations run: ', n_samples)
        print('Mean Terminal Portfolio Value: ',self.term_val_mean_)
        print('Standard Deviation of Terminal Portfolio Values: ', self.term_val_std_)
        print('Mean number of total trades executed: ', self.trade_sum_mean_)
        print('Standard Deviation of total trades executed: ', self.trade_sum_std_)
        print('Mean total trade cost: ', self.sim_trade_cost_mean_)
        print('Standard Deviation of total trade costs: ',self.sim_trade_cost_std_)
        print('Duration of each simulation (in years): ', round((self.random_walk_iters_/252),2))
        print('Upper rebalance threshold: ', self.thresh_high_)
        print('Lower rebalance threshold: ', self.thresh_low_)
        print('')
        
                                 
        
        '''
        weights_means=[]
        x=self.sim_weight_vals_
        for i in range(len(self.asset_list_)):
            for j in range(len(x)):
                weights_means.append(round(statistics.mean(x[i]),4))
        
        for i in range(len(self.asset_list_)):
            for j in range(len(x)):
                weight_history=[x[i] for x in self.sim_weight_vals_[j]]
                asset=self.asset_list_[i]
                print('Weight metrics for: ',asset)
                print('-------------------------')
                print('  Target portfolio weight: ',self.target_weights_[i])
                print('  Standard deviation of '+asset+' portfolio weight: ',round(statistics.stdev(weight_history),4))
                print('  Maximum weight reached for '+asset+': ', round(max(weight_history),4))
                print('  Minimum weight reached for '+asset+': ', round(min(weight_history),4))
                print('  Average of '+asset+' portfolio weight: ',round(statistics.mean(weight_history),4))
                print('')     
       '''         
        
    def _plot_sim_results(self):   
        
        import matplotlib.pyplot as plt
        import time
        
        plt.figure(figsize=(12,4))
        plt.title('Simulated Portfolio Value')
        for i in range(len(self.sim_port_vals_)):
            trace=self.sim_port_vals_[i]         
            plt.plot(trace)    
        plt.show()   
        
        plt.figure(figsize=(12,4))
        plt.title('Simulation Cash Level')
        for i in range(len(self.sim_cash_history_)):
            trace=self.sim_cash_history_[i]      
            plt.plot(trace)     
        plt.show()    
        
        plt.figure(figsize=(12,4))
        plt.title('Simulation Trade History')
        for i in range(len(self.sim_trade_history_)):
            trace=self.sim_trade_history_[i]     
            plt.plot(trace)              
        plt.show()   

        plt.figure(figsize=(12,4))
        plt.title('Asset Weight History')
        colors=['b', 'g', 'r', 'c', 'm', 'y', 'k']
        for i in range(len(self.sim_weight_vals_)):           
            for j in range(len(self.asset_list_)):
                trace=[x[j] for x in self.sim_weight_vals_[i]]            
                plt.plot(trace,color=colors[j])
        plt.show()           

        '''
        self.total_trades_=sum(self.sim_trade_history_)
        self.total_trade_cost_=self.trade_cost_*self.total_trades_
        
        print('')
        print('')
        print('SIMULATION REPORT')
        print('-----------------')
        print('Rebalancing simulation finished in: %.2f seconds' % (time.time() - start))
        print('Total number of trades executed: ', self.total_trades_)
        print('Cost per trade: ', round(self.trade_cost_,2))
        print('Total trading costs: ', round(self.total_trade_cost_,2))
        print('Maximum cash balance: ', round(max(self.sim_cash_history_),2))
        print('Minimum cash balance: ', round(min(self.sim_cash_history_),2))
        print('Average cash balance: ', round((sum(self.sim_cash_history_)/len(self.sim_cash_history_)),2))
        print('Fractional units allowed? ',str(self.frac_units_))
        print('')
        
        for i in range(len(self.asset_list_)):
            weight_history=[x[i] for x in self.sim_weight_vals_]
            asset=self.asset_list_[i]
            print('Weight metrics for: ',asset)
            print('-------------------------')
            print('  Target portfolio weight: ',self.target_weights_[i])
            print('  Standard deviation of '+asset+' portfolio weight: ',round(statistics.stdev(weight_history),4))
            print('  Maximum weight reached for '+asset+': ', round(max(weight_history),4))
            print('  Minimum weight reached for '+asset+': ', round(min(weight_history),4))
            print('  Average of '+asset+' portfolio weight: ',round(statistics.mean(weight_history),4))
            print('')
        '''
        
        #print('Time to finish simulation: %.2f seconds' % (time.time() - start))
        return    

    
    
    def _get_portfolio_values(self):
    
        
        
        unit_holdings=self.current_unit_holdings_
        unit_prices=self.current_unit_prices_
        frac_units=self.frac_units_
        target_weights=self.target_weights_
        trade_cost=self.trade_cost_

        #multiply new asset prices by current unit holdings
        #to return the new portfolio value.  This can be accomplished
        #in one line using iterators.
        port_val=sum(x * y for x, y in zip(unit_holdings, unit_prices))+self.sim_cash_balance_
        new_weights=[(x*y)/port_val for x,y in zip(unit_holdings, unit_prices)]
        weight_diffs=[(x/y) for x,y in zip(new_weights, target_weights)]
        new_target_vals=[x*port_val for x in target_weights]
    
        #We want to sell stocks that have exceeded their weight threshold, 
        #so long as we can get a whole unit if frac_units=False, otherwise we 
        #don't care.  We also want to deploy cash first, if possible, so that we
        #avoid a trade if necessary (if trades cost money).
        
        thresh_high=self.thresh_high_
        thresh_low=self.thresh_low_
        trade_count=0
    
        for i in range(len(new_weights)):
    
            if (weight_diffs[i]>thresh_high):
                
                target_sell=(unit_prices[i]*unit_holdings[i])-new_target_vals[i]
    
                if (frac_units==False):
    
                    if (((target_sell-trade_cost)//unit_prices[i])>=1):
                        allowable_units=((target_sell-trade_cost)//unit_prices[i])
                        unit_holdings[i]=unit_holdings[i]-allowable_units
                        self.sim_cash_balance_=self.sim_cash_balance_+((target_sell-trade_cost)//unit_prices[i])*unit_prices[i]
                        
                        trade_count+=1
    
                elif (frac_units==True):
    
                    allowable_units=((target_sell-trade_cost)/unit_prices[i])
                    unit_holdings[i]=unit_holdings[i]-allowable_units
                    self.sim_cash_balance_=self.sim_cash_balance_+(allowable_units*unit_prices[i])-trade_cost
                    trade_count+=1
    
            elif (weight_diffs[i]<thresh_low):
                
                target_buy=new_target_vals[i]-(unit_prices[i]*unit_holdings[i])
    
                if (frac_units==False):
                    
                    #Check that there's enough cash to buy the required number of units
                    if (self.sim_cash_balance_ >= (((target_buy-trade_cost)//unit_prices[i])*unit_prices[i])-(trade_cost+1)):
                        unit_holdings[i]=unit_holdings[i]+((target_buy-trade_cost)//unit_prices[i])
                        self.sim_cash_balance_=self.sim_cash_balance_-(((target_buy-trade_cost)//unit_prices[i])*unit_prices[i])-trade_cost
                        trade_count+=1
    
                elif (frac_units==True):
                    
                    #Check that there's enough cash to buy the required number of units
                    if (self.sim_cash_balance_ >= (((target_buy-trade_cost)/unit_prices[i])*unit_prices[i])-(trade_cost+1)):
                        unit_holdings[i]=unit_holdings[i]+((target_buy-trade_cost)/unit_prices[i])
                        self.sim_cash_balance_=self.sim_cash_balance_-(((target_buy-trade_cost)/unit_prices[i])*unit_prices[i])-trade_cost
                        trade_count+=1
        
        self.current_unit_holdings_=unit_holdings

    
        return port_val, new_weights, weight_diffs, new_target_vals,unit_holdings,trade_count    
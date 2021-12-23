import os
import numpy as np
import pandas as pd

class Backtester(object):
    def __init__(self, factor_name, quantile=5,save_result=True):
        self.factor_name = factor_name
        self.factor = self.read_dataframe(f"./data/{factor_name}_factor.csv")
        self.fwdrtn = self.read_dataframe(f"./data/{factor_name}_fwdrt.csv")
        self.stock_list = self.fwdrtn.columns.to_list()
        self.time_list = self.fwdrtn.index.to_list()
        self.factor_rank = self.factor.rank(axis=1, pct=True)
        self.quantile = quantile
        self.trade_day_per_year = 5 # 253

        self.simulation()
        if save_result:
            self.save_result()
    
    def read_dataframe(self,file_path):
        df = pd.read_csv(file_path, index_col=None,header=None, sep='\t')
        df.index = [f'time_{i}' for i in range(len(df.index))]
        df.columns = [f'stock_{i}' for i in range(len(df.columns))]
        return df
    
    def getQuantileWeight(self, choose_quantile):
        selected = (self.factor_rank <= choose_quantile/self.quantile) &  (self.factor_rank > ((choose_quantile - 1) / self.quantile))
        weight = selected.div(selected.sum(axis=1), axis=0)
        return weight
            
    def cal_net_value(self):
        # calculate quantile returns (group returns) first, then calculate net value
        self.group_return = pd.DataFrame(index = self.time_list)
        for choose_quantile in range(1, self.quantile + 1):
            weight = self.getQuantileWeight(choose_quantile)
            returns = (weight * self.fwdrtn).sum(axis = 1)
            returns.name = "Q_" + str(choose_quantile)
            self.group_return = pd.concat([self.group_return, returns], axis = 1)

        returns = self.group_return[f'Q_{self.quantile}'] - self.group_return[f'Q_{1}']
        returns.name = 'LS'
        self.group_return = pd.concat([self.group_return, returns], axis = 1)
        self.net_value = (1 + self.group_return).cumprod(axis=0)

    def cal_annualized_returns(self):
        self.annualized_returns = (self.net_value.iloc[-1])**(self.trade_day_per_year/len(self.time_list)) - 1
    
    def cal_annualized_volatility(self):
        self.annualized_volatility = self.group_return.std() * np.sqrt(self.trade_day_per_year)
    
    def cal_turnover(self):
        position = (self.getQuantileWeight(self.quantile)-self.getQuantileWeight(1)).mul(self.net_value['LS'],axis=0)
        difference = position - (position * (1+self.fwdrtn)).shift(axis=0).fillna(0.)
        self.turnover = difference.__abs__().sum(axis=1) / self.net_value['LS']

    def cal_portfolio_IR(self):
        self.portfolio_ir = self.group_return.mean() / self.group_return.std()

    def cal_serial_correlation(self):
        serial_corr = pd.Series(index=self.time_list,dtype=np.float64)
        for i in range(1,len(self.time_list)):
            corr = self.factor.iloc[i-1].corr(self.factor.iloc[i])
            serial_corr.iloc[i] = corr
        self.serial_correlation = serial_corr[1:]
    
    def cal_drawdown(self):
        self.drawdown = ((self.net_value/self.net_value.cummax())-1)['LS']

    def cal_spearson_rank_IC(self):
        spearson_rank_ic = pd.Series(index=self.time_list,dtype=np.float64)
        for i in range(len(self.time_list)):
            spearson_rank_ic.iloc[i] = self.factor_rank.iloc[i].corr(self.fwdrtn.iloc[i])
        self.spearson_rank_ic = spearson_rank_ic
    
    def simulation(self):
        self.cal_net_value()
        self.cal_annualized_returns()
        self.cal_annualized_volatility()
        self.cal_turnover()
        self.cal_drawdown()
        self.cal_portfolio_IR()
        self.cal_serial_correlation()
        self.cal_spearson_rank_IC()

    def save_result(self):
        self.result_path  = f"./report/{self.factor_name}"
        if not os.path.isdir(self.result_path):
            os.mkdir(self.result_path)
        self.single_write('net_value')
        self.single_write('annualized_returns')
        self.single_write('annualized_volatility')
        self.single_write('drawdown')
        self.single_write('turnover')
        self.single_write('portfolio_ir')
        self.single_write('serial_correlation')
        self.single_write('spearson_rank_ic')

    def single_write(self,attr):
        if (type(self.__getattribute__(attr))==pd.Series) or (type(self.__getattribute__(attr))==pd.DataFrame):
            self.__getattribute__(attr).to_csv(os.path.join(self.result_path,f"{attr}.csv"),index=False,header=False,sep='\t')
        else:
            pd.Series(self.__getattribute__(attr)).to_csv(os.path.join(self.result_path,f"{attr}.csv"),index=False,header=False,sep='\t')
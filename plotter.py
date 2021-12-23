import os
import pandas as pd
import matplotlib.pyplot as plt

class Plotter(object):
    def __init__(self,factor_name,win,save_result=True):
        self.factor_name = factor_name
        self.factor_path = os.path.join("./data",f"{self.factor_name}_factor.csv")
        self.report_dir_path = os.path.join("./report",self.factor_name)
        self.factor = self.load_factor()
        self.group_list = ['Q_1','Q_2','Q_3','Q_4','Q_5','LS']
        self.time_list = [f'time_{i}' for i in range(self.factor.shape[0])]
        self.load_metrics()
        self.fig, self.axes = self.plot_results(win)
        if save_result:
            self.fig.savefig(os.path.join(self.report_dir_path,'results.jpg'))
    
    def load_metrics(self):
        self.annualized_returns = self.load_series('annualized_returns',self.group_list)
        self.net_value = self.load_dataframe('net_value',self.time_list,self.group_list)
        self.portfolio_ir = self.load_series('portfolio_ir',self.group_list)
        self.annualized_volatility = self.load_series('annualized_volatility',self.group_list)
        self.drawdown = self.load_series('drawdown',self.time_list)
        self.turnover = self.load_series('turnover',self.time_list)
        self.serial_correlation = self.load_series('serial_correlation',self.time_list[1:])
        self.spearson_rank_ic = self.load_series('spearson_rank_ic',self.time_list)
    
    def load_series(self,filename,ind):
        series = pd.read_csv(os.path.join(self.report_dir_path,f'{filename}.csv'),index_col=None,header=None, sep='\t')#[0]
        if len(series)==1:
            series = series.T
        series = series[0]
        series.index = ind
        return series
    
    def load_dataframe(self,filename,ind,col):
        dataframe = pd.read_csv(os.path.join(self.report_dir_path,f'{filename}.csv'),index_col=None,header=None, sep='\t')
        dataframe.index = ind
        dataframe.columns = col
        return dataframe
    
    def load_factor(self):
        dataframe = pd.read_csv(self.factor_path,index_col=None,header=None, sep='\t')
        return dataframe

    def plot_results(self,win):
        fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(20,15))

        ax = axes[0,0]
        (self.annualized_returns*100).plot(kind='bar',ax=ax)
        ax.set_ylabel('Annualized Returns(%')
        ax.set_title('Annualized Return')

        ax = axes[0,1]
        self.net_value.plot(ax=ax)
        ax.set_ylabel('net value')
        ax.set_title('Wealth Curve')

        ax = axes[0,2]
        self.portfolio_ir.plot(kind='bar',ax=ax)
        ax.set_ylabel('Information Ratio')
        ax.set_title('Information Ratio')

        ax = axes[1,0]
        (self.annualized_volatility*100).plot(kind='bar',ax=ax)
        ax.set_ylabel('Annualized Volatility(%')
        ax.set_title('Annualized Volatility')

        ax = axes[1,1]
        (self.drawdown*100).plot(ax=ax)
        ax.set_ylabel('Drawdown(%)')
        ax.set_title('Drawdown')

        ax = axes[1,2]
        self.turnover.rolling(window=win,center=False).mean().plot(ax=ax)
        ax.set_ylabel('Turnover(%)')
        ax.set_title('Turnover')

        ax = axes[2,0]
        self.factor.iloc[-1].plot(kind='hist',bins=40,ax=ax)
        ax.set_xlabel('Factor')
        ax.set_title(self.factor_name+' Distribution')

        ax = axes[2,1]
        self.serial_correlation.rolling(window=win,center=False).mean().plot(ax=ax)
        ax.set_ylabel('Serial Corr(%)')
        ax.set_title('Serial Correlation')

        ax = axes[2,2]
        self.spearson_rank_ic.rolling(window=win,center=False).mean().plot(ax=ax)
        ax.set_ylabel('Spearman Corr(%)')
        ax.set_title('Spearman IC')

        return fig,axes
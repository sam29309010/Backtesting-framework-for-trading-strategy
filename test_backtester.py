import numpy as np
import pandas as pd
# from src import backtest as b
import backtest as b
from src import c_backtest as c_b
# from src import plotter
import plotter

def load_sample():
    backtester = b.Backtester("sample",save_result=False)
    return backtester

def test_read_data():
    backtester = load_sample()
    df = backtester.factor
    assert all(pd.api.types.is_float_dtype(df[col]) for col in df.columns)

def test_factor_rank():
    backtester = load_sample()
    rank_value = backtester.factor_rank.values
    np.testing.assert_array_equal(rank_value,
        np.array([[0.8, 1. , 0.1, 0.5, 0.3, 0.2, 0.4, 0.6, 0.7, 0.9],
        [0.6, 0.9, 0.4, 1. , 0.1, 0.8, 0.5, 0.7, 0.2, 0.3],
        [0.6, 1. , 0.4, 0.5, 0.7, 0.9, 0.2, 0.1, 0.3, 0.8]]))

def test_quantile_weight():
    backtester = load_sample()
    for i in range(1,backtester.quantile+1):
        np.testing.assert_almost_equal(backtester.getQuantileWeight(i).values.sum(axis=1),
            np.ones(len(backtester.time_list)))

    unique = np.zeros((len(backtester.time_list),len(backtester.stock_list)),dtype=int)
    for i in range(1,backtester.quantile+1):
        unique+= backtester.getQuantileWeight(i).values.astype(bool)
    np.testing.assert_almost_equal(unique,np.ones((len(backtester.time_list),len(backtester.stock_list)),dtype=int))

def test_group_return():
    backtester = load_sample()
    group_return = backtester.group_return.values
    np.testing.assert_almost_equal(group_return,
        np.array([[ 0.10936206,  0.15135122,  0.14711638, -0.35334596,  0.06850078,
            -0.04086129],
        [-0.24359946, -0.23581097,  0.35898264, -0.10339693,  0.21497799,
            0.45857746],
        [-0.11166153, -0.07962654, -0.28603455,  0.07653261, -0.10712077,
            0.00454076]]))
            
def test_net_value():
    backtester = load_sample()
    net_value = backtester.net_value.values
    np.testing.assert_almost_equal(net_value,
        np.array([[1.10936206, 1.15135122, 1.14711638, 0.64665404, 1.06850078,
            0.95913871],
        [0.83912206, 0.87984996, 1.55891125, 0.579792  , 1.29820493,
            1.3989781 ],
        [0.74542441, 0.80979056, 1.11300876, 0.624165  , 1.15914022,
            1.40533052]]))

def test_annualized_returns():
    backtester = load_sample()
    annualized_returns = backtester.annualized_returns.values
    np.testing.assert_almost_equal(annualized_returns,
        np.array([-0.38717094, -0.29646153,  0.19535703, -0.5441391 ,  0.27906699,
        0.76318331]))

def test_annualized_volatility():
    backtester = load_sample()
    annualized_volatility = backtester.annualized_volatility.values
    np.testing.assert_almost_equal(annualized_volatility,
        np.array([0.39879076, 0.43554455, 0.7351611 , 0.48273935, 0.36060841,
       0.61755548]))

def test_turnover():
    backtester = load_sample()
    turnover = backtester.turnover.values
    np.testing.assert_almost_equal(turnover,
        np.array([2., 2.85081305, 2.96246744]))

def test_drawdown():
    backtester = load_sample()
    drawdown = backtester.drawdown.values
    np.testing.assert_almost_equal(drawdown,
        np.array([0., 0., 0.]))

def test_portfolio_ir():
    backtester = load_sample()
    portfolio_ir = backtester.portfolio_ir.values
    np.testing.assert_almost_equal(portfolio_ir,
        np.array([-0.45959499, -0.28080412,  0.22311622, -0.58704974,  0.36452142,
        0.50964122]))

def test_serial_correlation():
    backtester = load_sample()
    serial_correlation = backtester.serial_correlation.values
    np.testing.assert_almost_equal(serial_correlation,
        np.array([0.2061907 , 0.15950074]))

def test_spearson_rank_ic():
    backtester = load_sample()
    spearson_rank_ic = backtester.spearson_rank_ic.values
    np.testing.assert_almost_equal(spearson_rank_ic,
        np.array([-0.37881799,  0.61632729,  0.16037768]))

def test_c_implementation_sample():
    backtester = load_sample()
    c_b.Backtester('sample',3,10)
    plter = plotter.Plotter('sample',win=1,save_result=True)
    np.testing.assert_almost_equal(backtester.net_value.values,plter.net_value.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_returns.values,plter.annualized_returns.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_volatility.values,plter.annualized_volatility.values,decimal=5)
    np.testing.assert_almost_equal(backtester.turnover.values,plter.turnover.values,decimal=5)
    np.testing.assert_almost_equal(backtester.drawdown.values,plter.drawdown.values,decimal=5)
    np.testing.assert_almost_equal(backtester.portfolio_ir.values,plter.portfolio_ir.values,decimal=5)
    np.testing.assert_almost_equal(backtester.serial_correlation.values,plter.serial_correlation.values,decimal=5)
    np.testing.assert_almost_equal(backtester.spearson_rank_ic.values,plter.spearson_rank_ic.values,decimal=5)

def test_c_implementation_small():
    backtester = b.Backtester("small",save_result=False)
    c_b.Backtester('small',20,10)
    plter = plotter.Plotter('small',win=3,save_result=True)
    np.testing.assert_almost_equal(backtester.net_value.values,plter.net_value.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_returns.values,plter.annualized_returns.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_volatility.values,plter.annualized_volatility.values,decimal=5)
    np.testing.assert_almost_equal(backtester.turnover.values,plter.turnover.values,decimal=5)
    np.testing.assert_almost_equal(backtester.drawdown.values,plter.drawdown.values,decimal=5)
    np.testing.assert_almost_equal(backtester.portfolio_ir.values,plter.portfolio_ir.values,decimal=5)
    np.testing.assert_almost_equal(backtester.serial_correlation.values,plter.serial_correlation.values,decimal=5)
    np.testing.assert_almost_equal(backtester.spearson_rank_ic.values,plter.spearson_rank_ic.values,decimal=5)

def test_c_implementation_mid():
    backtester = b.Backtester("mid",save_result=False)
    c_b.Backtester('mid',100,500)
    plter = plotter.Plotter('mid',win=10,save_result=True)
    np.testing.assert_almost_equal(backtester.net_value.values,plter.net_value.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_returns.values,plter.annualized_returns.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_volatility.values,plter.annualized_volatility.values,decimal=5)
    np.testing.assert_almost_equal(backtester.turnover.values,plter.turnover.values,decimal=5)
    np.testing.assert_almost_equal(backtester.drawdown.values,plter.drawdown.values,decimal=5)
    np.testing.assert_almost_equal(backtester.portfolio_ir.values,plter.portfolio_ir.values,decimal=5)
    np.testing.assert_almost_equal(backtester.serial_correlation.values,plter.serial_correlation.values,decimal=5)
    np.testing.assert_almost_equal(backtester.spearson_rank_ic.values,plter.spearson_rank_ic.values,decimal=5)

def test_c_implementation_large():
    backtester = b.Backtester("large",save_result=False)
    c_b.Backtester('large',1000,5000)
    plter = plotter.Plotter('large',win=30,save_result=True)
    np.testing.assert_almost_equal(backtester.net_value.values,plter.net_value.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_returns.values,plter.annualized_returns.values,decimal=5)
    np.testing.assert_almost_equal(backtester.annualized_volatility.values,plter.annualized_volatility.values,decimal=5)
    np.testing.assert_almost_equal(backtester.turnover.values,plter.turnover.values,decimal=5)
    np.testing.assert_almost_equal(backtester.drawdown.values,plter.drawdown.values,decimal=5)
    np.testing.assert_almost_equal(backtester.portfolio_ir.values,plter.portfolio_ir.values,decimal=5)
    np.testing.assert_almost_equal(backtester.serial_correlation.values,plter.serial_correlation.values,decimal=5)
    np.testing.assert_almost_equal(backtester.spearson_rank_ic.values,plter.spearson_rank_ic.values,decimal=5)

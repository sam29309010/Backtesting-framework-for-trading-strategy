import numpy as np
import pandas as pd

# Generate Random Data
# time_number = 20 # 100
# stock_number = 10 # 500

def generate_dataframe(time_number,stock_number,name):
    np.random.seed(1)
    time_list = [f'time_{i}' for i in range(1,time_number+1)]
    stock_list = [f'stock_{i}' for i in range(1,stock_number+1)]
    factor_value = np.random.rand(time_number,stock_number)
    factor_df = pd.DataFrame(factor_value,index=time_list,columns=stock_list)
    fwdrt_value = (np.random.rand(time_number,stock_number)-0.5)/(1.25)
    fwdrt_df = pd.DataFrame(fwdrt_value,index=time_list,columns=stock_list)
    factor_df.to_csv(f"./data/{name}_factor.csv",index=False,header=False,sep='\t')
    fwdrt_df.to_csv(f"./data/{name}_fwdrt.csv",index=False,header=False,sep='\t')

if __name__ == '__main__':
    generate_dataframe(3,10,'sample')
    generate_dataframe(20,10,'small')
    generate_dataframe(100,500,'mid')
    generate_dataframe(1000,5000,'large')
    
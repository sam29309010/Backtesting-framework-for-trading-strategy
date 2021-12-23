#include "matrix.h"
#include "read_csv.hpp"
#include <iostream>
#include <algorithm>

using namespace std;

class Backtester
{
public:
    Backtester(string, int, int);

    void init_data(string,string);
    void simulation(void);
    void save_result(void);

    Matrix get_quantile_weight(int);
    void calc_factor_rank();
    void calc_group_return(void);
    void calc_net_value(void);
    void calc_annualized_returns(void);
    void calc_portfolio_ir(void);
    void calc_annualized_volatility(void);
    void calc_drawdown(void);
    void calc_turnover(void);
    void calc_serial_correlation(void);
    void calc_spearson_rank_ic(void);

// private:
    Matrix factor;
    Matrix fwdrtn;
    Matrix factor_rank;
    Matrix group_return;
    Matrix net_value;
    Matrix annualized_returns;
    Matrix portfolio_ir;
    Matrix annualized_volatility;
    Matrix drawdown;
    Matrix turnover;
    Matrix serial_correlation;
    Matrix spearson_rank_ic;
    int ntime;
    int nstock;
    int quantile;
    int trade_day_per_year;
    string factor_name;
};

Backtester::Backtester(string factor_name, int time, int stock): factor_name(factor_name), ntime(time), nstock(stock), quantile(5), trade_day_per_year(5) {
    init_data("./data/"+factor_name+"_factor.csv","./data/"+factor_name+"_fwdrt.csv");
    simulation();
    save_result();
}

void Backtester::init_data(string factor_file, string fwdrt_file){
    factor = read_csv(factor_file, this->ntime, this->nstock);
    fwdrtn = read_csv(fwdrt_file, this->ntime, this->nstock);
}

void Backtester::simulation(void){
    calc_factor_rank();
    calc_group_return();
    calc_net_value();
    calc_annualized_returns();
    calc_portfolio_ir();
    calc_annualized_volatility();
    calc_drawdown();
    calc_turnover();
    calc_serial_correlation();
    calc_spearson_rank_ic();
}

void Backtester::save_result(void){
    string report_path = "./report/" + factor_name + "/";
    net_value.save_matirx(report_path + "net_value.csv");
    annualized_returns.save_matirx(report_path + "annualized_returns.csv");
    annualized_volatility.save_matirx(report_path + "annualized_volatility.csv");
    drawdown.save_matirx(report_path + "drawdown.csv");
    turnover.save_matirx(report_path + "turnover.csv");
    portfolio_ir.save_matirx(report_path + "portfolio_ir.csv");
    serial_correlation.save_matirx(report_path + "serial_correlation.csv");
    spearson_rank_ic.save_matirx(report_path + "spearson_rank_ic.csv");
}

Matrix Backtester::get_quantile_weight(int choose_quantile){
    Matrix weight(ntime,nstock);
    for (int i=0;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            if ((factor_rank(i,j)<=(double)(choose_quantile)/5) && (factor_rank(i,j)>(double)(choose_quantile-1)/5)){
                weight(i,j) += 1.0;
            }
        }
    }
    double sum = 0.0;
    for (int i=0;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            sum += weight(i,j);
        }
        for (int j=0;j<nstock;j++){
            weight(i,j) /= sum;
        }
        sum = 0.0;
    }
    return weight;
}

void Backtester::calc_factor_rank(void){
    // https://stackoverflow.com/questions/19481662/c-index-of-element-in-sorted-stdvector
    // not yet support nan value
    factor_rank = Matrix(ntime,nstock);
    double sort_arr[nstock];
    for (int i=0;i<ntime;++i){
        for (int j=0;j<nstock;++j){
            sort_arr[j] = factor(i,j);
        }
        sort(sort_arr,sort_arr+nstock);
        for (int k=0;k<nstock;++k){
            auto lower = lower_bound(sort_arr, sort_arr+nstock, factor(i,k));
            auto idx = distance(sort_arr, lower);
            factor_rank(i,k) = ((double) idx + 1) / nstock;
        }
    }
}

void Backtester::calc_group_return(void){
    group_return = Matrix(ntime,5+1);
    for (int q=1;q<5+1;q++){
        Matrix returns_mat = get_quantile_weight(q);
        for (int i=0;i<ntime;i++){
            for (int j=0;j<nstock;j++){
                returns_mat(i,j) = returns_mat(i,j) * fwdrtn(i,j);
            }
        }
        for (int i=0;i<ntime;i++){
            for (int j=0;j<nstock;j++){
                group_return(i,q-1) += returns_mat(i,j);
            }
        }
    }
    for (int i=0;i<ntime;i++){
        group_return(i,5) = group_return(i,5-1) - group_return(i,0);
    }
}

void Backtester::calc_net_value(void){
    net_value = Matrix(group_return);
    for (int i=0;i<ntime;i++){
        for (int j=0;j<5+1;j++){
            net_value(i,j) = net_value(i,j) + 1;
        }
    }
    for (int i=1;i<ntime;i++){
        for (int j=0;j<5+1;j++){
            net_value(i,j) *= net_value(i-1,j);
        }
    }
}

void Backtester::calc_annualized_returns(void){
    annualized_returns = Matrix(1,quantile+1);
    for (int i=0;i<quantile+1;i++){
        annualized_returns(0,i) = pow(net_value(ntime-1,i),(double)trade_day_per_year/ntime)-1;
    }
}

void Backtester::calc_portfolio_ir(void){
    portfolio_ir = group_return.mean();
    portfolio_ir /= group_return.std();
}

void Backtester::calc_annualized_volatility(void){
    annualized_volatility = group_return.std();
    annualized_volatility *= sqrt(trade_day_per_year);
}

void Backtester::calc_drawdown(void){
    Matrix cummax = Matrix(1,ntime);
    cummax(0,0) = net_value(0,quantile);
    for (int i=1;i<ntime;i++){
        cummax(0,i) = max(cummax(0,i-1),net_value(i,quantile));
    }
    drawdown = Matrix(1,ntime);
    for (int i=0;i<ntime;i++){
        drawdown(0,i) = net_value(i,quantile)/cummax(0,i)-1;
    }
}

void Backtester::calc_turnover(void){
    // broadcasting operation here, could be generalized to matrix operation
    Matrix position = (this->get_quantile_weight(quantile) - this->get_quantile_weight(1));
    for (int i=0;i<position.nrow;i++){
        for (int j=0;j<position.ncol;j++){
            position(i,j) *= net_value(i,quantile);
        }
    }
    Matrix difference = position;
    for (int i=1;i<difference.nrow;i++){
        for (int j=0;j<difference.ncol;j++){
            difference(i,j) -= position(i-1,j)*(1+fwdrtn(i-1,j));
        }
    }

    turnover = Matrix(1,ntime);
    for (int i=0;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            turnover(0,i) += abs(difference(i,j));
        }
        turnover(0,i) /= net_value(i,quantile);
    }
}

void Backtester::calc_serial_correlation(void){    
    Matrix sum = Matrix(1,ntime);
    Matrix square_sum = Matrix(1,ntime);
    for (int i=0;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            sum(0,i) += factor(i,j);
            square_sum(0,i) += factor(i,j)*factor(i,j);
        }
    }
    serial_correlation = Matrix(1,ntime-1);
    for (int i=1;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            serial_correlation(0,i-1) += factor(i-1,j)*factor(i,j);
        }
        serial_correlation(0,i-1) = serial_correlation(0,i-1)*nstock - (sum(0,i-1)*sum(0,i));
        serial_correlation(0,i-1) /= sqrt((square_sum(0,i-1)*nstock-sum(0,i-1)*sum(0,i-1))*(square_sum(0,i)*nstock-sum(0,i)*sum(0,i)));
    }
}

void Backtester::calc_spearson_rank_ic(void){
    Matrix rank_sum = Matrix(1,ntime);
    Matrix rank_square_sum = Matrix(1,ntime);
    Matrix fwdrtn_sum = Matrix(1,ntime);
    Matrix fwdrtn_square_sum = Matrix(1,ntime);
    for (int i=0;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            rank_sum(0,i) += factor_rank(i,j);
            rank_square_sum(0,i) += factor_rank(i,j)*factor_rank(i,j);
        }
    }
    for (int i=0;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            fwdrtn_sum(0,i) += fwdrtn(i,j);
            fwdrtn_square_sum(0,i) += fwdrtn(i,j)*fwdrtn(i,j);
        }
    }

    spearson_rank_ic = Matrix(1,ntime);
    for (int i=0;i<ntime;i++){
        for (int j=0;j<nstock;j++){
            spearson_rank_ic(0,i) += factor_rank(i,j)*fwdrtn(i,j);
        }
        spearson_rank_ic(0,i) = spearson_rank_ic(0,i)*nstock - (rank_sum(0,i)*fwdrtn_sum(0,i));
        spearson_rank_ic(0,i) /= sqrt((rank_square_sum(0,i)*nstock-rank_sum(0,i)*rank_sum(0,i))*(fwdrtn_square_sum(0,i)*nstock-fwdrtn_sum(0,i)*fwdrtn_sum(0,i)));
    }
}

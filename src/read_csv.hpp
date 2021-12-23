#ifndef CUSTOM_IO
#define CUSTOM_IO

#include <iostream>
#include <string>
#include <sstream>
#include <fstream>

Matrix read_csv(std::string str, int row, int col){
    Matrix M(row,col);
    std::fstream in(str);
    std::string line;
    for (int i=0;i<row;i++){
        std::getline(in, line);
        std::stringstream ss(line);
        double value;
        for (int j=0;j<col;j++){
            ss >> value;
            M(i,j) = value;
        }
    }
    return M;
}

#endif
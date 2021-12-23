#ifndef __MATRIX_H__
#define __MATRIX_H__

#include <iostream>
#include <string>
#include <sstream>
#include <cstring>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <utility>
#include <fstream>
#include <math.h>

using namespace std;

class Matrix {
public:
    size_t nrow;
    size_t ncol;

    // custom constructor
    Matrix(size_t,size_t);
    // default constructor
    Matrix(void);
    // destructor
    ~Matrix();
    // copy constructor
    Matrix(const Matrix&);
    Matrix(Matrix&);
    // move constructor
    Matrix(Matrix && );
    // copy assignment operator
    Matrix & operator=(Matrix const &);
    // move assignment operator
    Matrix & operator=(Matrix &&);

    Matrix mean(void);
    Matrix std(void);
    Matrix& operator/=(const Matrix&);
    Matrix& operator*=(double);
    Matrix operator-(const Matrix&);

    double   operator() (size_t,size_t) const;
    double & operator() (size_t,size_t);

    double* get_data() const;

    friend bool operator == (const Matrix&, const Matrix&);
    friend std::ostream& operator<<(std::ostream&, const Matrix&);

    void save_matirx(std::string);

private:
    double * m_buffer;
};

Matrix::Matrix(size_t n_row, size_t n_col):nrow(n_row), ncol(n_col), m_buffer(new double[n_row*n_col])
{
    memset(m_buffer, 0, nrow * ncol * sizeof(double));
}

Matrix::Matrix(void):nrow(0), ncol(0), m_buffer(nullptr){}

Matrix::~Matrix()
{
    if (nullptr != m_buffer){
        delete[] m_buffer;
    }
}

Matrix::Matrix(const Matrix& m):nrow(m.nrow), ncol(m.ncol), m_buffer(new double[m.nrow*m.ncol])
{
    memcpy(m_buffer,m.get_data(),sizeof(double)*nrow*ncol);
}

Matrix::Matrix(Matrix& m): nrow(m.nrow), ncol(m.ncol), m_buffer(new double[m.nrow*m.ncol])
{
    memcpy(m_buffer,m.get_data(),sizeof(double)*nrow*ncol);
}

Matrix::Matrix(Matrix && other)
{
    std::swap(other.nrow, nrow);
    std::swap(other.ncol, ncol);
    std::swap(other.m_buffer, m_buffer);
}

Matrix & Matrix::operator=(Matrix const & m)
{
    if (this == &m) { return *this; }
    nrow = m.nrow;
    ncol = m.ncol;
    if (nullptr != m_buffer){
        delete[] m_buffer;
    }
    m_buffer = new double[m.nrow*m.ncol];
    memcpy(m_buffer,m.get_data(),sizeof(double)*nrow*ncol);
    return *this;
}

Matrix & Matrix::operator=(Matrix && m)
{
    if (this == &m) { return *this; } // don't move to self.
    std::swap(m.nrow, nrow);
    std::swap(m.ncol, ncol);
    std::swap(m.m_buffer, m_buffer);
    return *this;
}

Matrix Matrix::mean(void)
{
    Matrix result = Matrix(1,ncol);
    for (int i=0;i<nrow;i++){
        for (int j=0;j<ncol;j++){
            result(0,j) += this->operator()(i,j);
        }
    }
    for (int i=0;i<ncol;i++){
        result(0,i) /= nrow;
    }
    return result;
}

Matrix Matrix::std(void){
    Matrix mean = this->mean();
    Matrix result = Matrix(1,ncol);
    for (int i=0;i<nrow;i++){
        for (int j=0;j<ncol;j++){
            result(0,j) += pow(this->operator()(i,j)-mean(0,j),2);
        }
    }
    for (int i=0;i<ncol;i++){
        result(0,i) = sqrt(result(0,i)/(nrow-1));
    }
    return result;
}

Matrix& Matrix::operator/=(const Matrix& m){
    for (int i=0;i<nrow;i++){
        for (int j=0;j<ncol;j++){
            this->operator()(i,j) /= m.operator()(i,j);
        }
    }
    return *this;
}

Matrix& Matrix::operator*=(double v){
    for (int i=0;i<nrow;i++){
        for (int j=0;j<ncol;j++){
            this->operator()(i,j) *= v;
        }
    }
    return *this;
}

Matrix Matrix::operator-(const Matrix& m){
    Matrix result = *this;
    for (int i=0;i<nrow;i++){
        for (int j=0;j<ncol;j++){
            result(i,j) -= m(i,j);
        }
    }
    return result;
}

double   Matrix::operator() (size_t row, size_t col) const
{
    return m_buffer[row* ncol + col];
}

double & Matrix::operator() (size_t row, size_t col)
{
    return m_buffer[row* ncol + col];
}

double* Matrix::get_data() const {
    return m_buffer;
}

bool operator == (const Matrix& A, const Matrix& B){
    if ((A.nrow!=B.nrow) || (A.ncol!=B.ncol)) return false;
    for (size_t i=0;i<A.nrow*A.ncol;i++){
        if (A.m_buffer[i] != B.m_buffer[i]) return false;
    }
    return true;
}

std::ostream& operator<<(std::ostream& os, const Matrix& m){
    for (size_t i = 0; i < m.nrow; ++i) {
        os << m(i,0);
        for (size_t j = 1; j < m.ncol; ++j) {
            os << " " << m(i,j);
        }
        os << std::endl;
    }
    return os;
}

void Matrix::save_matirx(std::string str){
    fstream file;
    file.open(str, ios::out);
    for (size_t i=0;i<nrow;++i){
        for (size_t j=0; j<ncol-1; ++j){
            file << this->operator()(i,j) << "\t";
        }
        file << this->operator()(i,ncol-1) << std::endl;
    }
}

#endif
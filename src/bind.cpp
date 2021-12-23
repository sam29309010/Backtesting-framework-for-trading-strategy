#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/operators.h>
#include <iostream>
#include <string>
#include <sstream>
#include <cstring>
#include "matrix.h"
#include "backtest.hpp"

namespace py = pybind11;
PYBIND11_MODULE(c_backtest, m){
    pybind11::class_<Backtester>(m,"Backtester")
        .def(py::init<const std::string &,int,int>());
}
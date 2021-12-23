CXX = g++
CXXFLAG = -O3 -Wall -shared -std=c++11 -fPIC
PYBIND = $(shell python -m pybind11 --includes)
PYINCLUDE = $(shell python3-config --includes)
PYCONFIG = $(shell python3-config --extension-suffix)

.PHONY: all, clean

all: generate_sample backtester test

generate_sample:
	python random_data.py

backtester:
	$(CXX) $(CXXFLAG) $(PYINCLUDE) $(PYBIND) ./src/bind.cpp -o ./src/c_backtest$(PYCONFIG)

test:
	mkdir report/sample report/small report/mid report/large
	pytest test_backtester.py

clean: 
	rm -rf __pycache__

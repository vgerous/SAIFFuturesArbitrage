import unittest
from processdata import DataProcessor
from io import StringIO
import pandas as pd
import sys


class TestDataProcessor:

    def setup(self):
        file = '../data/Ag.csv'
        self.processor = DataProcessor(file, 20)

    def test_read_file(self):
        df = self.processor.read_file()
        print(df)

    def test_get_window(self):
        print(self.processor.get_window(self.processor.read_file()))

    def test_get_symbols(self):
        self.processor.getSymbols(self.processor.read_file())

    def test_common_test(self):
        df = pd.DataFrame({
            'A': ['foo', 'bar', 'foo', 'bar', 'foo', 'bar'],
            'B': [1, 2, 3, 4, 5, 6],
            'C': [2.0, 5., 8., 1., 2., 9.]})
        grouped = df.groupby('A')
        df.groupby('A').B.filter(lambda x: x.mean() > 3.)
        print(grouped)
        print(df)

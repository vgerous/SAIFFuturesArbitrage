import pandas as pd
import matplotlib.pyplot as plt
import sys
import os


class DataProcessor:
    """
    file: data file
    day_window: how many days for calculating MA, SD
    cut_loss_margin: margin to close trades for loss cut
    """

    def __init__(self, file, day_window, cut_loss_margin):
        self.file = file
        self.day_window = day_window
        self.cut_loss_margin = cut_loss_margin
        self.last_open_buy = {'price': 0, 'symbol': ''}
        self.last_open_sell = {'price': 0, 'symbol': ''}

    """
    Process data read from file
    """
    def process(self):
        df = self.read_file()
        window = self.get_window(df)
        self.do_statistics(df, window)
        processed_df = self.back_test(df)

        # output to csv
        output_file = 'transaction/data_statistics_' + self.get_file_base_name()
        print('Saving transaction to ' + output_file)
        processed_df.to_csv(output_file, index_label='Time', header=True)
        # plt.show()

    def read_file(self):
        return pd.read_csv(self.file, header=0, index_col=1,
                           parse_dates=['Time'],
                           infer_datetime_format=True,
                           keep_date_col=True)

    def get_window(self, time_array):
        first_day = time_array.first('1D')
        return len(first_day) * self.day_window

    def get_file_base_name(self):
        input_file_abs_path = sys.path[0] + '/' + self.file
        return os.path.basename(input_file_abs_path)

    def do_statistics(self, df, window):
        df['MA'] = df['Price_Gap'].rolling(window=window).mean()
        df['SD'] = df['Price_Gap'].rolling(window=window).std()
        df['SDx2'] = df.apply(lambda row: row['SD'] * 2 + row['MA'], axis=1)
        df['SDx-2'] = df.apply(lambda row: row['MA'] - row['SD'] * 2, axis=1)
        length = len(df.index)
        df['Buy_Symbol'] = [''] * length
        df['Buy_Price'] = [None] * length
        df['Sell_Symbol'] = [''] * length
        df['Sell_Price'] = [None] * length
        df['Transaction_Type'] = [''] * length

    def back_test(self, df):
        is_open = False
        for index, row in df.iterrows():
            # skip those rows don't have statistics yet
            if str(row['MA']).strip() == 'nan':
                continue
            split_array = str(row['Contract_Name']).split('-')
            main_symbol = split_array[0]
            sub_symbol = split_array[1]

            if is_open:
                # check if need to cut loss
                is_cut = self.cut_loss(df, row, main_symbol, sub_symbol)
                if is_cut:
                    # already cut loss then continue
                    continue
                else:
                    # check if need to close trades
                    is_open = not self.close(df, index, row, main_symbol, sub_symbol)
            # else check if need to open
            else:
                is_open = self.open(df, index, row, main_symbol, sub_symbol)

        processed_df = df[df['Transaction_Type'].apply(lambda x: x != '')]
        return pd.DataFrame({
            'Main_Contract_Price': processed_df['Main_Contract_Price'],
            'Sub_Contract_Price': processed_df['Sub_Contract_Price'],
            'Price_Gap': processed_df['Price_Gap'],
            'MA': processed_df['MA'],
            'SDx2': processed_df['SDx2'],
            'SDx-2': processed_df['SDx-2'],
            'Buy_Symbol': processed_df['Buy_Symbol'],
            'Buy_Price': processed_df['Buy_Price'],
            'Sell_Symbol': processed_df['Sell_Symbol'],
            'Sell_Price': processed_df['Sell_Price'],
            'Transaction_Type': processed_df['Transaction_Type']
          })

    def cut_loss(self, df, row, last_open_buy, last_open_sell):
        return False

    def close(self, df, index, row, main_symbol, sub_symbol):
        mid = row['MA']
        current_gap = row['Price_Gap']
        main_price = row['Main_Contract_Price']
        sub_price = row['Sub_Contract_Price']

        # last open sell on main
        # && last open buy on sub
        # && current gap has dropped down below mid
        # then close the trades
        if current_gap <= mid \
                and self.last_open_sell['symbol'] == main_symbol \
                and self.last_open_buy['symbol'] == sub_symbol:
            # close sell main, open buy sub
            print('close sell on {} at {} for {}'.format(main_symbol, main_price, index))
            df.loc[index, 'Buy_Symbol'] = main_symbol
            df.loc[index, 'Buy_Price'] = main_price

            print('close sell on {} at {} for {}'.format(sub_symbol, sub_price, index))
            df.loc[index, 'Sell_Symbol'] = sub_symbol
            df.loc[index, 'Sell_Price'] = sub_price

            df.loc[index, 'Transaction_Type'] = 'Close'

            # clear trade cache
            self.clear_trade_cache()
            return True

        # last open buy on main
        # && last open sell on sub
        # && current gap has rose up over mid
        # then close the trades
        elif current_gap >= mid \
                and self.last_open_buy['symbol'] == main_symbol \
                and self.last_open_sell['symbol'] == sub_symbol:
            # close buy main, close sell sub
            print('close buy on {} at {} for {}'.format(sub_symbol, sub_price, index))
            df.loc[index, 'Buy_Symbol'] = sub_symbol
            df.loc[index, 'Buy_Price'] = sub_price

            print('close sell on {} at {} for {}'.format(main_symbol, main_price, index))
            df.loc[index, 'Sell_Symbol'] = main_symbol
            df.loc[index, 'Sell_Price'] = main_price

            df.loc[index, 'Transaction_Type'] = 'Close'

            # clear trade cache
            self.clear_trade_cache()
            return True
        return False

    def open(self, df, index, row, main_symbol, sub_symbol):
        upper = row['SDx2']
        lower = row['SDx-2']
        current_gap = row['Price_Gap']
        main_price = row['Main_Contract_Price']
        sub_price = row['Sub_Contract_Price']

        if current_gap >= upper:
            # open sell main, open buy sub
            print('open buy on {} at {} for {}'.format(sub_symbol, sub_price, index))
            df.loc[index, 'Buy_Symbol'] = sub_symbol
            df.loc[index, 'Buy_Price'] = sub_price

            print('open sell on {} at {} for {}'.format(main_symbol, main_price, index))
            df.loc[index, 'Sell_Symbol'] = main_symbol
            df.loc[index, 'Sell_Price'] = main_price

            df.loc[index, 'Transaction_Type'] = 'Open'

            # cache open trades
            self.last_open_buy['price'] = sub_price
            self.last_open_buy['symbol'] = sub_symbol
            self.last_open_sell['price'] = main_price
            self.last_open_sell['symbol'] = main_symbol
            return True

        elif current_gap <= lower:
            # open buy main, open sell sub
            print('open buy on {} at {} for {}'.format(main_symbol, main_price, index))
            df.loc[index, 'Buy_Symbol'] = main_symbol
            df.loc[index, 'Buy_Price'] = main_price

            print('open sell on {} at {} for {}'.format(sub_symbol, sub_price, index))
            df.loc[index, 'Sell_Symbol'] = sub_symbol
            df.loc[index, 'Sell_Price'] = sub_price

            df.loc[index, 'Transaction_Type'] = 'Open'

            # cache open trades
            self.last_open_buy['price'] = main_price
            self.last_open_buy['symbol'] = main_symbol
            self.last_open_sell['price'] = sub_price
            self.last_open_sell['symbol'] = sub_symbol
            return True
        return False

    def clear_trade_cache(self):
        __last_open_buy = {'price': 0, 'symbol': ''}
        __last_open_sell = {'price': 0, 'symbol': ''}


if __name__ == '__main__':
    for item in os.listdir('data'):
        processor = DataProcessor('data/' + item, 20, 0.03)
        processor.process()

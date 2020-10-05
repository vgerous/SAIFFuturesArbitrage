import pandas as pd
import matplotlib.pyplot as plt


def process(file):
    df = pd.read_csv(file, header=0)
    df['Price Gap'] = df.apply(lambda row: row['Main Contract'] - row['Sub-main Contract'], axis=1)
    df['MA20'] = df['Price Gap'].rolling(window=20).mean()
    df['SD'] = df['Price Gap'].rolling(window=20).std()
    df['SDx2'] = df.apply(lambda row: row['SD'] * 2 + row['MA20'], axis=1)
    df['SDx-2'] = df.apply(lambda row: row['MA20'] - row['SD'] * 2, axis=1)
    df.to_csv('data_statistics.csv', index=True, header=True)
    processed_df = pd.DataFrame({'Time': df['Time'],
                                 'MA20': df['MA20'],
                                 'SDx2': df['SDx2'],
                                 'SDx-2': df['SDx-2']})
    processed_df.plot(x='Time')
    plt.show()


if __name__ == '__main__':
    process('mock_futures_data.csv')

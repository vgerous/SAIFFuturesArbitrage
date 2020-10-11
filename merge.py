import pandas as pd

def merge_data(main_contract, sub_contract, output_file_name):
    df1 = pd.read_excel(main_contract)
    df1 = df1.dropna()
    df1['日期'] = pd.to_datetime(df1['日期'])
    
    df2 = pd.read_excel(sub_contract)
    df2 = df2.dropna()
    df2['日期'] = pd.to_datetime(df2['日期'])
    
    new_data = pd.merge(df1, df2, on = '日期', how = 'inner')
    new_data['Price_Gap'] = new_data['收盘价(元)_x'] - new_data['收盘价(元)_y']
    new_data['Contract_Name'] = new_data['代码_x'].iloc[0].split('.')[0] + '-' + new_data['代码_y'].iloc[0].split('.')[0]
    new_data['Main_Contract_Price'] = new_data['收盘价(元)_x']
    new_data['Sub_Contract_Price'] = new_data['收盘价(元)_y']
    new_data['Time'] = new_data['日期']
    
    target = ['Contract_Name', 'Time', 'Main_Contract_Price', 'Sub_Contract_Price', 'Price_Gap']
    target_data = new_data[target]
    target_data.to_csv(output_file_name,index=False)
    
    return target_data
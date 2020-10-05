import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def prepare_data(number_of_points):
    main_contract = []
    sub_main_contract = []
    for i in range(0, number_of_points):
        rand_per = random.randrange(-98, 100, 1) / 10000 + 1
        main_price = 3000 if i == 0 else round(main_contract[i - 1] * rand_per, 2)
        sub_price = main_price - main_price * random.randrange(10, 50) / 1000
        main_contract.append(main_price)
        sub_main_contract.append(round(sub_price, 2))
    print(main_contract)
    print(sub_main_contract)
    x = np.arange(0, number_of_points)
    main_contract_points = np.array(main_contract)
    sub_main_contract_points = np.array(sub_main_contract)

    df = pd.DataFrame({'Time': x,
                       'Main Contract': main_contract_points,
                       'Sub-main Contract': sub_main_contract_points})
    df.to_csv('mock_futures_data.csv', index=False, header=True)

    df.plot(x='Time')
    plt.show()


if __name__ == '__main__':
    prepare_data(4 * 60 * 120)

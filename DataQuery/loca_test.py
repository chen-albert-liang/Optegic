import pandas as pd

spx = pd.read_csv("C:\\Users\\chena\\Desktop\\Trading\\Datasets\\IVolatility\\options_spx_9327_20191029.csv")
spx_nbbo = pd.read_csv("C:\\Users\\chena\\Desktop\\Trading\\Datasets\\IVolatility\\options_SPX_9327_2019-10-29_NBBO_000.csv", nrows=1000)

test = spx[spx['SPXW  191030C01800000'] == 'SPXW  191227C02785000'].reset_index(drop=True)
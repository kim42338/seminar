import numpy as np
import pandas as pd

def human_readable_to_num(string):
    multipliers = {'K':1000, 'M':1000000, 'B':1000000000, 'T':1000000000000}
    if string[-1].isdigit(): # check if no suffix
        return int(string)
    mult = multipliers[string[-1]] # look up suffix to get multiplier
    # convert number to float, multiply by multiplier, then make int
    return int(float(string[:-1]) * mult)


def object_to_string(df):
    return df.astype(str)


def object_to_int(df):
    return df.astype(str).astype(int)


def object_to_float(df):
    return df.astype(str).astype(float)


def divide_by_million(df):
    return df/1000000


def formatter(df):
    df.index = df.index.date
    df = divide_by_million(df)

    df1 = df.iloc[0,:].map('{:,.0f}'.format)
    df2 = df.iloc[1,:].map('{:,.0f}'.format)
    df3 = df.iloc[2,:].map('{:,.0f}'.format)
    df4 = df.iloc[3,:].map('{:,.0f}'.format)

    df = pd.concat([df1, df2, df3, df4], axis=1)
    return df


def round_decimal(df):
    df.index = df.index.date
    
    df1 = df.iloc[0,:].map('{:,.2f}'.format)
    df2 = df.iloc[1,:].map('{:,.2f}'.format)
    df3 = df.iloc[2,:].map('{:,.2f}'.format)
    df4 = df.iloc[3,:].map('{:,.2f}'.format)
    
    df = pd.concat([df1, df2, df3, df4], axis=1)
    return df


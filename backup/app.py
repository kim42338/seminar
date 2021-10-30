import datetime as dt
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from company import Company


def create_stock_price_comparison_chart(tickers):
    fig = go.Figure()
    for ticker in tickers:
        company = Company(ticker, start_input, end_input)
        fig.add_trace(go.Scatter(x = company.price_data.index, y = company.price_data['adjclose'], name = company.name))
    
    fig.update_layout(
        margin = dict(
            l = 0,
            r = 0,
            t = 0
        ),
        legend_title_text = 'Tickers',
        xaxis = dict(
            title = "Date",
            type = "date"
        ),
        yaxis = dict(
            title = "Price"
        )
    )
    return fig


def create_stock_price_history_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['adjclose']))
    fig.update_layout(
        margin = dict(
            l = 0,
            r = 0,
            t = 0,
        ),
        xaxis = dict(
            type = 'date',
            title = "Select Range",
            rangeselector = dict(
                buttons = list([
                    dict(count = 1,
                        label = '1m',
                        step = 'month',
                        stepmode = 'backward'
                    ),
                    dict(count = 3,
                        label = '3m',
                        step = 'month',
                        stepmode = 'backward'
                    ),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode = "backward"
                    ),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode = "todate"
                    ),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"
                    ),
                    dict(count=3,
                        label="3y",
                        step="year",
                        stepmode="backward"
                    ),
                    dict(step="all")
                ]),
            ),
            rangeselector_bgcolor = 'lightgrey',
            rangeslider = dict(
                visible = True
            ),
        ),
        yaxis = dict(
            title = "Price",
            autorange = True,
            fixedrange = False
        )
    )
    return fig


def create_overview_chart(df):
    fig = go.Figure()
    fig.add_trace(
        go.Table(
            columnorder=[1, 2],
            columnwidth=[80, 120],
            header=dict(
                values=['<b>Overview</b>', '<b>TTM</b>'],
                line_color='darkslategray',
                fill_color='#9467BD',
                align=['left', 'center'],
                font=dict(color='white', size=16),
                height=40
            ),
            cells=dict(
                values=[
                    list(df.index),
                    list(df.iloc[:,0])
                ],
                line_color='darkslategray',
                fill=dict(color=['#EEA6FB', 'white']),
                align=['left', 'center'],
                font=dict(color='darkslategray', size=14),
                height=30
            )
        )
    )
    fig.update_layout(
        margin = dict(
            l = 0,
            r = 0,
            t = 0,
            b = 0
        ),
    )
    return fig


def create_table(df):
    date = pd.to_datetime(df.columns.values)
    date = list(date.year)
    date.insert(0, '')

    fig = go.Figure()
    fig.add_trace(go.Table(
        header = dict(
            values = date,
            line_color = 'darkslategray',
            fill_color = 'grey',
            align = ['left', 'center'],
            font = dict(color = 'white', size = 16)
        ),
        cells = dict(
            values = [
            list(df.index),
            list((df.iloc[:,0])),
            list((df.iloc[:,1])),
            list((df.iloc[:,2])),
            list((df.iloc[:,3]))],
            line_color = 'darkslategray',
            fill_color = [['white', 'lightgrey', 'white', 'lightgrey']*4],
            align = ['left', 'center'],
            font = dict(color = 'darkslategray', size = 14),
            height = 30
        )))
    fig.update_layout(
        margin = dict(
            l = 0,
            r = 0,
            t = 0,
            b = 0
        ),
        autosize = True,
        height = len(df.index) * 30 + 50
    )
    return fig


def create_bar_chart(df, nticks):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index.year, y=df.iloc[:,0]))
    fig.update_layout(
            xaxis = dict(
                nticks = nticks
            ),
            margin = dict(
            l = 0,
            r = 0,
            t = 0
        )
    )
    return fig


def create_scatter_plot(df):
    date = pd.to_datetime(df.columns.values)
    
    fig = go.Figure()
    for index, row in df.iterrows():
        fig.add_trace(go.Scatter(x=(date.year), y=(df.loc[index]), name = index)
    )
    fig.update_layout(
        xaxis = dict(
            nticks = 4
        ),
        yaxis = dict(
            showgrid = False
        ),
        margin = dict(
            l = 0,
            r = 0,
            t = 0,
            b = 0
        )
    )
    return fig
        

# streamlit function
st.set_page_config(layout = 'wide')
st.title('Financial Dashboard')
st.sidebar.subheader('Financial Dashboard')
option = st.sidebar.selectbox(label='Select an option:', options = [('Stock Price Comparison'), ('Financial Analysis')])

#stock price comparison
if option == 'Stock Price Comparison':    
    #side bar
    ticker_input = st.sidebar.multiselect(label='Enter Tickers to Compare:', options=Company.get_sp500_tickers(), help='Choose multiple tickers to be compared')
    start_input = st.sidebar.date_input('Start Date:', dt.date(2020, 1, 1))
    end_input = st.sidebar.date_input('End Date:', dt.datetime.today())
    search_button = st.sidebar.button('Search')

    if search_button:
        with st.spinner('Loading Data...'):
            st.subheader('Stock Price Comparison')
            fig = create_stock_price_comparison_chart(ticker_input)
            st.plotly_chart(fig, use_container_width=True)

#financial analysis
if option == 'Financial Analysis':
    # sidebar
    ticker_input = st.sidebar.selectbox(label='Enter Ticker for Financial Data:', options=Company.get_sp500_tickers(), help='Choose a single firm to further investigate in')
    search_button = st.sidebar.button('Search')
    
    if search_button:
        with st.spinner('Loading Data...'):
            company = Company(ticker_input)

            #company info
            st.subheader('General Information')
            st.write(company.info)

            #column divisor
            col1, col2 = st.columns([1.5, 1])
            
            #column 1 - stock price plot
            with col1:
                st.subheader(f'Stock Price History - {company.ticker}')
                fig = create_stock_price_history_chart(company.price_data)
                st.plotly_chart(fig, use_container_width=True)
            
            #column 2 - overview table
            with col2:
                st.subheader('Overview')
                st.write('')
                fig = create_overview_chart(company.generate_overview_df())
                st.plotly_chart(fig, use_container_width=True)

            with st.expander('Income Statement (in millions)'):
                fig = create_table(company.generate_income_statement_df())
                st.plotly_chart(fig, use_container_width=True)

            with st.expander('Cash Flow Statement  (in millions)'):
                fig = create_table(company.generate_cash_flow_df())
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander('Balance Sheet (in millions)'):
                fig = create_table(company.generate_balance_sheet_df())
                st.plotly_chart(fig, use_container_width=True)

            with st.expander('Financial Ratios (in millions)'):
                fig = create_table(company.generate_financial_ratio_df())
                st.plotly_chart(fig, use_container_width=True)     
                fig = create_scatter_plot(company.generate_financial_ratio_df())
                st.plotly_chart(fig, use_container_width=True)
                                
            with st.expander('Cash and Cash Equivalents (in millions)'):
                st.subheader('Cash and Cash Equivalents')
                fig = create_bar_chart(company.generate_cash_and_cash_equivalents_df(), 8)
                st.plotly_chart(fig, use_container_width=True)
            
#OHLC
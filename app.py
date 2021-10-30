import datetime as dt
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import numpy as np


from company import Company
from pm import PM
from ta import TA

def create_stock_price_comparison_chart(tickers, start_input, end_input):
    fig = go.Figure()
    for ticker in tickers:
        company = Company(ticker, start_input, end_input)
        fig.add_trace(go.Scatter(x=company.price_data.index, y=company.price_data['adjclose'], name=company.name)) 
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


def create_financial_ratio_plot(df):
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
            showgrid = False,
            autorange='reversed'
        ),
        margin = dict(
            l = 0,
            r = 0,
            t = 0,
            b = 0
        )
    )
    return fig

def get_risk_tolerance(answer1, answer2, answer3, answer4, answer5, answer6):
        score = 0
        risk_tolerance = ''
        if answer1 == 'B':
            score += 5
        if answer1 == 'C':
            score += 12
        if answer1 == 'D':
            score += 17
        if answer2 == 'B':
            score += 8
        if answer2 == 'C':
            score += 16
        if answer3 == 'B':
            score += 8
        if answer3 == 'C':
            score += 16
        if answer4 == 'B':
            score += 8
        if answer4 == 'C':
            score += 17
        if answer5 == 'B':
            score += 6
        if answer5 == 'C':
            score += 12
        if answer5 == 'D':
            score += 17
        if answer6 == 'B':
            score += 8
        if answer6 == 'C':
            score += 17
        if 0 <= score <= 18:
            risk_tolerance = 'Low'
        if 19 <= score <= 39:
            risk_tolerance = 'Low to Medium'
        if 40 <= score <= 59:
            risk_tolerance = 'Medium'
        if 60 <= score <= 79:
            risk_tolerance = 'Medium to High'
        if 80 <= score <= 100:
            risk_tolerance = 'High'
        return risk_tolerance


def get_risk_adjusted_SR(volatility, returns, risk_tolerance, risk_tolerance_SR, idx):
    length = len(risk_tolerance_SR)
    range = abs(volatility[volatility_idx[0]] - volatility[volatility_idx[-1]])
    quartile1 = round(volatility[volatility_idx[0]] + (range/5),2)
    quartile2 = round(volatility[volatility_idx[0]] + (2*range/5),2)
    quartile3 = round(volatility[volatility_idx[0]] + (3*range/5),2)
    
    if risk_tolerance == 'Low':
        tolerance_adjusted_idx = risk_tolerance_SR[0]
    if risk_tolerance == 'Low to Medium':
        tolerance_adjusted_idx = get_quartile_max(volatility, returns, quartile1)
    if risk_tolerance == 'Medium':
        tolerance_adjusted_idx = get_quartile_max(volatility, returns, quartile2)
    if risk_tolerance == 'Medium to High':
        tolerance_adjusted_idx = get_quartile_max(volatility, returns, quartile3)
    if risk_tolerance == 'High':
        tolerance_adjusted_idx = risk_tolerance_SR[length-1]
    if risk_tolerance == "Highest Sharpe Ratio":
        tolerance_adjusted_idx = idx
    return tolerance_adjusted_idx


def get_quartile_max(volatility, returns, quartile):
    quartile_idx=[]
    df = pd.DataFrame({'volatility':volatility, 'returns':list(returns)})
    for index,row in df.iterrows():
        if abs(row['volatility'] - quartile) < 0.0025:
            quartile_idx.append(index)
    max = np.max(returns[quartile_idx])
    for x in quartile_idx:
        if returns[x] == max:
            return x


def create_pie_chart(tickers, weight, idx):
    weight = weight[idx]
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=tickers, values=weight, textinfo='label+percent', insidetextorientation='radial'))
    fig.update_layout(
        margin = dict(
            l = 0,
            r = 0,
            t = 0,
            b = 0
        )
    )
    return fig


def create_efficient_frontier(returns, volatility, tolerance_adjusted_idx, idx):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=volatility, y=returns, mode='markers', name='Monte Carlo Simulation'))
    fig.add_trace(go.Scatter(x=[(volatility[tolerance_adjusted_idx])], y=[(returns[tolerance_adjusted_idx])], mode='markers', marker=dict(color='orange'), name='Risk-Adjusted SR'))
    fig.add_trace(go.Scatter(x=[(volatility[idx])], y=[(returns[idx])], marker=dict(color='Red'), mode='markers', name='Most Efficient SR'))
    fig.update_layout(
        xaxis = dict(
            title = 'Volatility'
        ),
        yaxis = dict(
            title = 'Return'
        ),
        margin = dict(
            l = 0,
            r = 0,
            t = 0,
            b = 0
        ),
    )
    return fig


def create_scatter_plot(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['adjclose']))
    fig.update_layout(
        xaxis = dict(
            showticklabels=False,
        ),
        yaxis = dict(
            title = "Price"
        ),
        margin = dict(
            l = 0,
            r = 13,
            t = 0,
            b = 0
        )
    )
    return fig


def create_rsi_chart(df, rsi):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=rsi))
    fig.add_hline(y= 70, line_dash='dot', line_color='green')
    fig.add_hline(y= 80, line_dash='dot', line_color='red')
    fig.add_hline(y= 30, line_dash='dot', line_color='green')
    fig.add_hline(y= 20, line_dash='dot', line_color='red')
    fig.update_layout(
        height=200,
        yaxis = dict(
            title = 'RSI',
            showgrid = False
        ),
        margin = dict(
            l = 47,
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
option = st.sidebar.selectbox(label='Select an option:', options = [('Stock Price Comparison'), ('Financial Analysis'), ('Risk Tolerance'), ('Portfolio Management'), ('Technical Analysis')])


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
            fig = create_stock_price_comparison_chart(ticker_input, start_input, end_input)
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
                fig = create_financial_ratio_plot(company.generate_financial_ratio_df())
                st.plotly_chart(fig, use_container_width=True)
                                
            with st.expander('Cash and Cash Equivalents (in millions)'):
                st.subheader('Cash and Cash Equivalents')
                fig = create_bar_chart(company.generate_cash_and_cash_equivalents_df(), 8)
                st.plotly_chart(fig, use_container_width=True)
            
            st.write('-data from Yahoo Finance-')


#risk tolerance
if option == 'Risk Tolerance':
    st.title('Risk Tolerance Survey - EdwardJones')
    st.markdown("1. How concerned are you about inflation (the risk your money will buy fewer goods Answer and services in the future because of rising prices)?\n" +
    "Growth investments, such as stocks, have the potential to outpace inflation, but also generally have larger swings in value. Cash and fixed-income investments, such as bonds, may be more stable over time, but also may not keep up with inflation. Based on this information, which statement below do you most agree with:")
    risk_tolerance_q1 = st.radio(
        label='', 
        options=(
            "A. My goal is to minimize swings in my portfolio's value, even if growth does not keep pace with inflation", 
            "B. My goal is for growth to at least keep pace with inflation, with the risk of modest swings in my portfolio's value",
            "C. My goal is for growth to exceed inflation, with the risk of modest to larger swings in my portfolio's value",
            "D. My goal is for growth to significantly exceed inflation, with the risk of larger swings in my portfolio's value"
        ),
    )
    st.markdown("2. Which statement best describes your personal investment philosophy?")
    risk_tolerance_q2 = st.radio(
        label='',
        options=(
            "A. Income: I prefer investments that may generate more consistent (but most likely lower) returns year to year, with a primary focus on generating income. I prefer a low level of fluctuations and risk of declines over time",
            "B. Growth and Income: I prefer investments that balance my growth objectives with my income needs. I prefer a modest amount of fluctuations and risk of declines over time",
            "C. Growth: I am willing to own investments with a higher degree of fluctuations and risk of declines in exchange for the potential to achieve higher average returns over time"
        )
    )
    st.markdown("3. How comfortable are you with potential fluctuations in your portfolio?")
    st.image(Image.open('question3.png'))
    risk_tolerance_q3 = st.radio(
        label='',
        options=(
            'A.',
            'B.',
            'C.'
        )
    )
    st.markdown("4. Which statement best describes how you feel about the trade-off between potential returns and declines?")
    risk_tolerance_q4 = st.radio(
        label='',
        options=(
            "A. I'm more focused on potential declines in my portfolio's value. The return I achieve is of secondary importance",
            "B. The potential for declines is equally important to me as the potential return",
            "C. I am more focused on the return potential of my portfolio than on potential declines"
        )
    )
    st.markdown("5. There have been several periods in history in which the value of the market has dropped 25% or more in a year. If the value of your portfolio fell from $200,000 to $150,000 (25%) in one year, how would you react?")
    risk_tolerance_q5 = st.radio(
        label='',
        options=(
            "A. I would move my money to different investments to reduce the potential for more declines, even if this meant missing a potential recovery",
            "B. I would be concerned and would consider moving into different investments if the declines continued",
            "C. I would leave my money where it is and continue according to my long-term strategy",
            "D. I would view this as an opportunity and would consider investing more if I had the money available"
        )
    )
    st.markdown("6. There is a trade-off between larger potential short-term fluctuations and a portfolio’s long-term growth potential, as shown in the table below. Which portfolio would you be most comfortable with?")
    st.image(Image.open('question6.png'))
    risk_tolerance_q6 = st.radio(
        label='',
        options=(
            'A. Portfolio A',
            'B. Portfolio B',
            'C. Portfolio C'
        )   
    )
    submit = st.button('submit')
    
    if submit:
        risk_tolerance = get_risk_tolerance(risk_tolerance_q1[0], risk_tolerance_q2[0], risk_tolerance_q3[0], risk_tolerance_q4[0], risk_tolerance_q5[0], risk_tolerance_q6[0])
        st.title(f'Your Risk Tolerance: {risk_tolerance}')
        st.image(Image.open('risk_tolerance.png'), width=600)
        st.image(Image.open('interpretation.png'))


#portfolio management
if option == 'Portfolio Management':
    # sidebar
    ticker_input = st.sidebar.multiselect(label='Enter Tickers to Analyze', options=Company.get_sp500_tickers(), help='Choose Multiple Firms for Risk and Return')
    risk_tolerance = st.sidebar.selectbox(label='Select Risk Tolerance', help='Enter result from risk tolerance survey', options=[('Low'), ('Low to Medium'), ('Medium'), ('Medium to High'), ('High'), ('Highest Sharpe Ratio')])
    start_input = st.sidebar.date_input('Start Date:', dt.date(2020, 1, 1))
    end_input = st.sidebar.date_input('End Date:', dt.datetime.today())
    search_button = st.sidebar.button('Search')

    if search_button:
        pm = PM(ticker_input, start_input, end_input)
        returns, volatility, sharpe_ratio, weight, volatility_idx, idx = pm.monte_carlo_simulation()
        tolerance_adjusted_idx = get_risk_adjusted_SR(volatility, returns, risk_tolerance, volatility_idx, idx)

        # portfolio management
        st.subheader('Ideal Portfolio Management')
        fig = create_pie_chart(ticker_input, weight, tolerance_adjusted_idx)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns([1,1])
        with col1:
            st.title('Risk-Adjusted Sharpe Ratio:')
            st.write(f'Volatility: {volatility[tolerance_adjusted_idx]}')
            st.write(f'Return: {returns[tolerance_adjusted_idx]}')
            st.write(f'Sharpe Ratio: {sharpe_ratio[tolerance_adjusted_idx]}')

        with col2:
            st.title('Most Efficient Sharpe Ratio:')
            st.write(f'Volatility: {volatility[idx]}')
            st.write(f'Return: {returns[idx]}')
            st.write(f'Sharpe Ratio: {sharpe_ratio[idx]}')

        #efficient frontier
        st.subheader('Efficient Frontier')
        fig2 = create_efficient_frontier(returns, volatility, tolerance_adjusted_idx, idx)
        st.plotly_chart(fig2, use_container_width=True)


#technical analysis
if option == 'Technical Analysis':
    #sidebar
    option = st.sidebar.selectbox(label='Select an option:', options = [('RSI')])

    if option == 'RSI':
        ticker_input = st.sidebar.selectbox(label='Enter ticker to Analyze', options=Company.get_sp500_tickers())
        start_input = st.sidebar.date_input('Start Date:', dt.date(2019, 1, 1))
        end_input = st.sidebar.date_input('End Date:', dt.datetime.today())
        period = st.sidebar.number_input(label='Select RSI period', value=14, step=1, help='default: 14')
        search_button = st.sidebar.button('Search')
        
        if search_button:
            ta = TA(ticker_input, start_date=start_input, end_date=end_input, period=period)
            fig = create_scatter_plot(ta.get_price_df)
            st.plotly_chart(fig, use_container_width=True)
            fig2 = create_rsi_chart(ta.get_price_df, ta.calculate_rsi())
            st.plotly_chart(fig2, use_container_width=True)


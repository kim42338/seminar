import datetime as dt
import streamlit as st
from utils import formatter, object_to_string, round_decimal
import yahoo_fin.stock_info as si
import pandas as pd
import ssl
import plotly.graph_objects as go
ssl._create_default_https_context = ssl._create_unverified_context

class App:
    def __init__(self, ticker, start_input = None, end_input = None):
        overview_dict = si.get_quote_table(ticker)
        income_statement = si.get_income_statement(ticker)
        self.price_df = si.get_data(ticker, start_input, end_input)
        self.balance_sheet = si.get_balance_sheet(ticker)
        self.cash_flow_statement = si.get_cash_flow(ticker)
        
        #overview
        self.name = si.get_quote_data(ticker)['longName']
        self.info = si.get_company_info(ticker).loc['longBusinessSummary'].item()
        self.market_cap = overview_dict['Market Cap']
        self.average_volume = overview_dict['Avg. Volume']
        self.earnings_date = overview_dict['Earnings Date']
        self.ex_dividend_date = overview_dict['Ex-Dividend Date']
        self.dividend_yield = overview_dict['Forward Dividend & Yield']
        self.per = overview_dict['PE Ratio (TTM)']
        self.eps = overview_dict['EPS (TTM)']
        self.day_range = overview_dict["Day's Range"]
        self.year_range = overview_dict['52 Week Range']
        self.target = overview_dict['1y Target Est']

        #income statement
        self.revenue = income_statement.loc['totalRevenue']
        self.cost = income_statement.loc['costOfRevenue']
        self.gross_profit = income_statement.loc['grossProfit']
        self.operating_expense = income_statement.loc['totalOperatingExpenses']
        self.ebit = income_statement.loc['ebit']
        self.interest_expense = income_statement.loc['interestExpense']
        self.ebt = income_statement.loc['incomeBeforeTax']
        self.tax_expense = income_statement.loc['incomeTaxExpense']
        self.net_income = income_statement.loc['netIncome']
        self.cash_and_cash_equivalents = self.balance_sheet.loc['cash']

        #cash flow statement
        self.cfo = self.cash_flow_statement.loc['totalCashFromOperatingActivities']
        self.cfi = self.cash_flow_statement.loc['totalCashflowsFromInvestingActivities']
        self.cff = self.cash_flow_statement.loc['totalCashFromFinancingActivities']
        self.change_in_inventory = self.cash_flow_statement.loc['changeToInventory']

        #balance sheet
        self.total_current_asset = self.balance_sheet.loc['totalCurrentAssets']
        self.total_asset = self.balance_sheet.loc['totalAssets']
        self.total_current_liabilities = self.balance_sheet.loc['totalCurrentLiabilities']
        self.total_liabilities = self.balance_sheet.loc['totalLiab']
        self.total_shareholder_equity =self.balance_sheet.loc['totalStockholderEquity']

    #overview
    def get_overview(self):
        self.overview_df = pd.DataFrame({'Market Capitalization' : self.market_cap, 'Volume' : self.average_volume, "Earning's Date" : self.earnings_date, 'Ex-Dividend Date' : self.ex_dividend_date, 'Dividend Yield' : self.dividend_yield,
                                         'PER' : self.per, 'EPS' : self.eps, 'Day Range' : self.day_range, '52 Week Range' : self.year_range, 
                                         '1y Target Estimate' : self.target}, index=['TTM'])
        volume_comma = self.overview_df.Volume.map('{:,.0f}'.format)
        self.overview_df.Volume = volume_comma
        self.overview_df = object_to_string(self.overview_df)
        self.overview_df = self.overview_df.transpose()

    #income statement
    def get_income_statement(self):
        self.income_statement_df = pd.DataFrame({'Total Revenue' : self.revenue , ' - Cost of Revenue' : self.cost, 'Gross Profit' : self.gross_profit,
                                            ' - Operating Expense' : self.operating_expense, 'EBIT' : self.ebit, ' - Interest Expense' : self.interest_expense,
                                            'EBT' : self.ebt, ' - Tax Expense' : self.tax_expense, 'Net Income' : self.net_income})
        self.income_statement_df = formatter(self.income_statement_df)

    #cash flows
    def get_cash_flow_statement(self):
        self.cash_flow_statement_df = pd.DataFrame({'CFO' : self.cfo, 'CFI' : self.cfi, 'CFF' : self.cff, 'Change in Inventory' : self.change_in_inventory})
        self.cash_flow_statement_df = formatter(self.cash_flow_statement_df)
        
    #balance sheet
    def get_balance_sheet(self):
        self.balance_sheet_df = pd.DataFrame({'Total Current Assets' : self.total_current_asset, 'Total Assets' : self.total_asset, 'Total Current Liabilities' : self.total_current_liabilities,
                                              'Total Liabilities' : self.total_liabilities, "Total Shareholder's Equity" : self.total_shareholder_equity})
        self.balance_sheet_df = formatter(self.balance_sheet_df)

    # financial ratios     
    def get_financial_ratios(self):
        self.gross_margin = self.gross_profit/self.revenue
        self.operating_margin = self.ebit/self.revenue
        self.net_margin = self.net_income/self.revenue
        
        self.financial_ratio_df = pd.DataFrame({'Gross Margin' : self.gross_margin, 'Operating Margin' : self.operating_margin, 'Net Margin' : self.net_margin})
        self.financial_ratio_df = round_decimal(self.financial_ratio_df)

    def create_chart(self, df, height):
        date = list(company.cash_and_cash_equivalents.index.year)
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
            height = height
        )
        return fig
        
#streamlit function
st.set_page_config(layout = 'wide')
st.title('Financial Dashboard')
st.sidebar.subheader('Financial Dashboard')
option = st.sidebar.selectbox(label='Select an option:', options = ('Stock Price Comparison', 'Financial Analysis'))

#stock price comparison
if option == 'Stock Price Comparison':    
    #side bar
    ticker_input = st.sidebar.multiselect(label='Enter Tickers to Compare:', options= si.tickers_sp500(), help='Choose multiple tickers to be compared')
    start_input = st.sidebar.date_input('Start Date:', dt.date(2020, 1, 1))
    end_input = st.sidebar.date_input('End Date:', dt.datetime.today())
    search_button = st.sidebar.button('Search')

    if search_button:
        with st.spinner('Loading Data...'):
            fig = go.Figure()
            for ticker in ticker_input:
                company = App(ticker, start_input, end_input)
                fig.add_trace(go.Scatter(x = company.price_df.index, y = company.price_df['adjclose'], name = company.name))
            
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
            st.subheader('Stock Price Comparison')
            st.plotly_chart(fig, use_container_width=True)

#financial analysis
if option == 'Financial Analysis':
    #sidebar
    ticker_input = st.sidebar.selectbox(label='Enter Ticker for Financial Data:', options= si.tickers_sp500(), help='Choose a single firm to further investigate in')
    search_button = st.sidebar.button('Search')
    
    if search_button:
        with st.spinner('Loading Data...'):
            company = App(ticker_input)
            company.get_overview()        
            company.get_income_statement()
            company.get_cash_flow_statement()
            company.get_balance_sheet()
            company.get_financial_ratios()
            price_df = company.price_df

            # company info
            st.subheader('General Information')
            st.write(company.info)

            #column divisor
            col1, col2 = st.columns([1.5,1])
            
            #column 1 - stock price plot
            with col1:
                st.subheader(f'Stock Price History - {ticker_input}')
                fig = go.Figure()
                
                fig.add_trace(
                    # open high low close
                    # go.Ohlc(x = price_df.index, 
                    #            open = price_df['open'],
                    #            high = price_df['high'],
                    #            low = price_df['low'],
                    #            close = price_df['close']
                    # )
                    go.Scatter(x = price_df.index, y = price_df['adjclose'])
                )

                fig.update_layout(
                    margin = dict(
                        l = 0,
                        r = 0,
                        t = 0,
                    ),
                    xaxis = dict(
                        type = "date",
                        title = 'Select Range',
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
                st.plotly_chart(fig, use_container_width=True)
                print(company.overview_df)
            #column 2 - overview table
            with col2:
                st.subheader('Overview')
                st.write('')
                # st.table(company.overview_df)
                fig = go.Figure()
                fig.add_trace(go.Table(
                    columnorder = [1,2],
                    columnwidth = [80, 120],
                    header = dict(
                        values = ['<b>Overview</b>', '<b>TTM</b>'],
                        line_color = 'darkslategray',
                        fill_color = '#9467BD',
                        align = ['left', 'center'],
                        font = dict(color = 'white', size = 16),
                        height = 40
                    ),
                    cells = dict(
                        values = [
                        list(company.overview_df.index),
                        list((company.overview_df.iloc[:,0]))],
                        line_color='darkslategray',
                        fill=dict(color=['#EEA6FB', 'white']),
                        align = ['left', 'center'],
                        font=dict(color='darkslategray', size = 14),
                        height = 30
                    )))
                fig.update_layout(
                    margin = dict(
                        l = 0,
                        r = 0,
                        t = 0,
                        b = 0
                    ),
                    autosize = True
                )
                st.plotly_chart(fig, use_container_width=True)

            with st.expander(f'Income Statement (since {company.income_statement_df.columns[3]}) - in millions'):
                print(company.income_statement_df)
                fig = company.create_chart(company.income_statement_df, 320)
                st.plotly_chart(fig, use_container_width=True)

            with st.expander(f'Cash Flow Statement (since {company.cash_flow_statement_df.columns[3]}) - in millions'):
                fig = company.create_chart(company.cash_flow_statement_df, 160)
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander(f'Balance Sheet (since {company.balance_sheet_df.columns[3]}) - in millions'):
                fig = company.create_chart(company.balance_sheet_df, 200)
                st.plotly_chart(fig, use_container_width=True)

            with st.expander(f'Financial Ratios (since {company.financial_ratio_df.columns[3]})'):
                fig = company.create_chart(company.financial_ratio_df, 120)
                st.plotly_chart(fig, use_container_width = True)                
                fig2=go.Figure()
                for index, row in company.financial_ratio_df.iterrows():
                    fig2.add_trace(go.Scatter(x=(company.cash_and_cash_equivalents.index.year), y=(company.financial_ratio_df.loc[index]), name = index)
                )
                fig2.update_layout(
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
                st.plotly_chart(fig2, use_container_width=True)
                
            with st.expander(f'Cash Flow and Cash Equivalents (since {company.financial_ratio_df.columns[3]})'):
                fig = go.Figure()
                fig.add_trace(go.Bar(x=company.cash_and_cash_equivalents.index.year, y=company.cash_and_cash_equivalents.iloc[:]))
                fig.update_layout(
                        title='Cash Flow Comparison',
                        xaxis = dict(
                            nticks = 8
                        ),
                        margin = dict(
                        l = 0,
                        r = 0,
                        b = 0
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            
# button option candle stick - takes too much time
# hyperlink wikipedia style


# #stock price comparison
# if option == 'Stock Price Comparison':    
#     #side bar
#     ticker_input = st.sidebar.multiselect(label='Enter Tickers to Compare:', options= si.tickers_sp500(), help='Choose multiple tickers to be compared')
#     start_input = st.sidebar.date_input('Start Date:', dt.date(2020, 1, 1))
#     end_input = st.sidebar.date_input('End Date:', dt.datetime.today())
#     search_button = st.sidebar.button('Search')

#     if search_button:
#         with st.spinner('Loading Data...'):
#             fig = go.Figure()
#             for ticker in ticker_input:
#                 company = Company(ticker, start_input, end_input)
#                 fig.add_trace(go.Scatter(x = company.price_df.index, y = company.price_df['adjclose'], name = company.name))
            
#             fig.update_layout(
#                 margin = dict(
#                     l = 0,
#                     r = 0,
#                     t = 0
#                 ),
#                 legend_title_text = 'Tickers',
#                 xaxis = dict(
#                     title = "Date",
#                     type = "date"
#                 ),
#                 yaxis = dict(
#                     title = "Price"
#                 )
#             )
#             st.subheader('Stock Price Comparison')
#             st.plotly_chart(fig, use_container_width=True)
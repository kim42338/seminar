from utils import formatter, object_to_string, round_decimal
import yahoo_fin.stock_info as si
import streamlit as st
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class Company:
    def __init__(self, ticker, start_date=None, end_date=None):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    @property
    def name(self):
        return self.quote_data['longName']

    @property
    def info(self):
        return self.company_info.loc['longBusinessSummary'].item()

    @property
    @st.cache(ttl=86400, persist=False)
    def quote_data(self):
        return si.get_quote_data(self.ticker)

    @property
    @st.cache(ttl=86400, persist=False)
    def company_info(self):
        return si.get_company_info(self.ticker)

    @property
    @st.cache(ttl=86400, persist=False)
    def quote_table(self):
        return si.get_quote_table(self.ticker)

    @property
    @st.cache(ttl=86400, persist=False)
    def price_data(self):
        return si.get_data(self.ticker, self.start_date, self.end_date)

    @property
    @st.cache(ttl=86400, persist=False)
    def income_statement(self):
        return si.get_income_statement(self.ticker)
    
    @property
    @st.cache(ttl=86400, persist=False)
    def cash_flow(self):
        return si.get_cash_flow(self.ticker)

    @property
    @st.cache(ttl=86400, persist=False)
    def balance_sheet(self):
        return si.get_balance_sheet(self.ticker)

    @staticmethod
    @st.cache(ttl=86400, persist=False)
    def get_sp500_tickers():
        return si.tickers_sp500()

    #overview
    def generate_overview_df(self):
        overview_df = pd.DataFrame(
            {
                'Market Capitalization' : self.quote_table['Market Cap'], 
                'Volume' : self.quote_table['Avg. Volume'], 
                'Earning\'s Date' : self.quote_table['Earnings Date'], 
                'Ex-Dividend Date' : self.quote_table['Ex-Dividend Date'],
                'Dividend Yield' : self.quote_table['Forward Dividend & Yield'],
                'PER' : self.quote_table['PE Ratio (TTM)'], 
                'EPS' : self.quote_table['EPS (TTM)'], 
                'Day Range' : self.quote_table['Day\'s Range'],
                '52 Week Range' : self.quote_table['52 Week Range'], 
                '1y Target Estimate' : self.quote_table['1y Target Est']
            },
            index=['TTM']
        )
        volume_comma = overview_df.Volume.map('{:,.0f}'.format)
        overview_df.Volume = volume_comma
        overview_df = object_to_string(overview_df)
        return overview_df.transpose()

    #income statement
    def generate_income_statement_df(self):
        income_statement_df = pd.DataFrame(
            {
                'Total Revenue' : self.income_statement.loc['totalRevenue'],
                ' - Cost of Revenue' : self.income_statement.loc['costOfRevenue'],
                'Gross Profit' : self.income_statement.loc['grossProfit'],
                ' - Operating Expense' : self.income_statement.loc['totalOperatingExpenses'],
                'EBIT' : self.income_statement.loc['ebit'],
                ' - Interest Expense' : self.income_statement.loc['interestExpense'],
                'EBT' : self.income_statement.loc['incomeBeforeTax'], 
                ' - Tax Expense' : self.income_statement.loc['incomeTaxExpense'],
                'Net Income' : self.income_statement.loc['netIncome'],
            }
        )
        return formatter(income_statement_df)

    #cash flows
    def generate_cash_flow_df(self):
        cash_flow_df = pd.DataFrame(
            {
                'CFO' : self.cash_flow.loc['totalCashFromOperatingActivities'], 
                'CFI' : self.cash_flow.loc['totalCashflowsFromInvestingActivities'], 
                'CFF' : self.cash_flow.loc['totalCashFromFinancingActivities'], 
                # 'Change in Inventory' : self.cash_flow.loc['changeToInventory']
            }
        )
        return formatter(cash_flow_df)

    def generate_balance_sheet_df(self):
        balance_sheet_df = pd.DataFrame(
            {
                'Total Current Assets' : self.balance_sheet.loc['totalCurrentAssets'],
                'Total Assets' : self.balance_sheet.loc['totalAssets'],
                'Total Current Liabilities' : self.balance_sheet.loc['totalCurrentLiabilities'],
                'Total Liabilities' : self.balance_sheet.loc['totalLiab'], 
                'Total Shareholder\'s Equity' : self.balance_sheet.loc['totalStockholderEquity']
            }
        )
        return formatter(balance_sheet_df)

    # financial ratios     
    def generate_financial_ratio_df(self):
        self.gross_margin = self.income_statement.loc['grossProfit']/self.income_statement.loc['totalRevenue']
        self.operating_margin = self.income_statement.loc['ebit']/self.income_statement.loc['totalRevenue']
        self.net_profit_margin = self.income_statement.loc['netIncome']/self.income_statement.loc['totalRevenue']
        financial_ratio_df = pd.DataFrame(
            {
                'Gross Margin' : self.gross_margin, 
                'Operating Margin' : self.operating_margin, 
                'Net Profit Margin' : self.net_profit_margin
            }
        )
        financial_ratio_df = round_decimal(financial_ratio_df)
        return financial_ratio_df
    
    def generate_cash_and_cash_equivalents_df(self):
        cash_and_cash_equivalents_df = pd.DataFrame(
            {
                'Cash and Cash Equivalents' : self.balance_sheet.loc['cash']
            }
        )
        return cash_and_cash_equivalents_df
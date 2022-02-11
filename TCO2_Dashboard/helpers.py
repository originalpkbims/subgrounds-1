import pandas as pd
import datetime as dt

def pct_change(first, second):
  diff = second - first
  change = 0
  try:
    if diff > 0:
        change = (diff / first) * 100
    elif diff < 0:
        diff = first - second
        change = -((diff / first) * 100)
  except ZeroDivisionError:
    return float('inf')
  return change

# Used to make Plotly layouts with pre-built visualizations
def add_px_figure(pxfig, layout, row, col):
  for trace in pxfig["data"]:
    layout.append_trace(trace, row=row, col=col)


def drop_duplicates(df):
  df = df.drop_duplicates(subset=['Token Address'],keep='first')
  df = df.reset_index(drop=True)
  return df

def date_manipulations(df):
    df["Bridging Date"] =pd.to_datetime(df["Bridging Date"],unit='s').dt.tz_localize(None).dt.floor('D').dt.date
    df["Vintage"] =pd.to_datetime(df["Vintage"],unit='s').dt.tz_localize(None).dt.year
    return df

def black_list_manipulations(df):
    #Dropping rows where Region = "", these tokenized carbon credits are black-listed
    #Black listed because their methodology = "AM0001" 
    df = df[df["Region"] != ""].reset_index()
    return df

def region_manipulations(df):
    df['Region'] = df['Region'].replace('South Korea', 'Korea, Republic of')
    #Belize country credits are categorized under Latin America. Confirmed this with Verra Registry 
    df['Region'] = df['Region'].replace('Latin America', 'Belize')
    df['Region'] = df['Region'].replace('Oceania', 'Indonesia')
    df['Region'] = df['Region'].replace('Asia', 'Cambodia')
    return df

def subsets(df):

    #7-day, last 7-day, 30-day and last 30 day time
    current_time = dt.datetime.combine(dt.date.today(), dt.datetime.min.time())
    seven_day_start = current_time - dt.timedelta(days=7)
    last_seven_day_start = seven_day_start - dt.timedelta(days=7)
    thirty_day_start = current_time - dt.timedelta(days=30)
    last_thirty_day_start = thirty_day_start - dt.timedelta(days=30)

    # Seven day pool subsets    
    sd_pool =df[(df["Bridging Date"] < current_time.date()) &(df["Bridging Date"] >= seven_day_start.date())]
    last_sd_pool =df[(df["Bridging Date"] < seven_day_start.date()) &(df["Bridging Date"] >= last_seven_day_start.date())]
    # # Thirty day pool subsets
    td_pool =df[(df["Bridging Date"] < current_time.date()) &(df["Bridging Date"] >= thirty_day_start.date())]
    last_td_pool =df[(df["Bridging Date"] < thirty_day_start.date()) &(df["Bridging Date"] >= last_thirty_day_start.date())]

    return sd_pool, last_sd_pool, td_pool, last_td_pool

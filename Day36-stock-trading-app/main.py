import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime as dt


STOCK = "fsr"
COMPANY_NAME = "fisker"

# load secrets
load_dotenv("/Users/nikhil.shrivastava/PycharmProjects/ENVIRONMENT.env")

# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
ALTPHA_VANTAGE_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHA_VANTAGE_API_KEY
}

stock_api_response = requests.get(ALPHA_VANTAGE_URL, params=ALTPHA_VANTAGE_PARAMS)
stock_api_response.raise_for_status()
stock_data = stock_api_response.json()["Time Series (Daily)"]


# convert dictionary values into a list
stock_data_list = list(stock_data.values())

# using list comprehension and slicing getting each values into a list
stock_daily_data = [item for item in stock_data_list[:2]]
# get today and yesterday closing price
yesterday_closing_price = float(stock_data_list[0]['4. close'])
day_before_yesterday_closing_price = float(stock_data_list[1]['4. close'])

difference = yesterday_closing_price - day_before_yesterday_closing_price

if difference > 0:
    up = "🔺"
else:
    up = "🔻"

# using abs() to get rid of -ve values
percent_change = abs(round((difference / day_before_yesterday_closing_price) * 100, 2))

if percent_change >= 2:

    ## STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    NEWS_API_URL= "https://newsapi.org/v2/everything"
    NEWS_API_KEY= os.getenv("NEWS_API_KEY")
    current_dt = dt.now().date()
    NEWS_API_PARAMS = {
        "q": COMPANY_NAME,
        "from": current_dt,
        "to": current_dt,
        "sortBy": "popularity",
        "apikey": NEWS_API_KEY
    }
    # GET https://newsapi.org/v2/everything?q=apple&from=2021-09-16&to=2021-09-16&sortBy=popularity&apiKey=d26c93bc802046a98ff25ba8b126cc8a
    NEWS_API_RESPONSE = requests.get(url=NEWS_API_URL, params=NEWS_API_PARAMS )
    news_articles = NEWS_API_RESPONSE.json()['articles']
    top_headlines = [(article['title'], article['description']) for article in news_articles[:3]]

    ## STEP 3: Use https://www.twilio.com
    # Send a separate message with the percentage change and each article's title and description to your phone number.
    # Twilio api setup
    ACCOUNT_SID = os.getenv("ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")

    # setup Twilio client
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for index, news in enumerate(top_headlines):
        headline = news[0]
        description = news[1]
        message_body = f"{COMPANY_NAME.title()}: {up}{percent_change}%\nHeadline:{headline}\nBrief:{description}"
        message = client.messages.create(
            body=message_body,
            from_="+19147126984",
            to="+19726934134"
        )
        print(message.status)
else:
    print("No significant change in stock")
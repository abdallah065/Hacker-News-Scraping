import bs4
import requests
import re
import datetime
import pandas as pd
import numpy as np
import sqlite3
df = pd.DataFrame(columns=['id', 'title', 'link', 'date', 'score', 'rank'])
x = 0
while True:
    print(f"Page {x}")
    page = requests.get('https://news.ycombinator.com/?p=' + str(x))
    page = bs4.BeautifulSoup(page.text, 'html.parser')
    headlines = page.find_all('tr', class_='athing')
    if not headlines:
        print("No more headlines found")
        break
    ids = [int(headline.attrs['id']) for headline in headlines]

    titles = [headline.find('span', class_='titleline').a.text for headline in headlines]

    links = [headline.find('span', class_='titleline').a.attrs['href'] for headline in headlines]

    ranks = page.find_all('span', class_='rank')
    ranks = [int(rank.text[:-1]) for rank in ranks]
    
    scores = []
    for id in ids:
        score = page.find('span', class_='score',id="score_"+str(id))
        if score:
            score = int(re.search(r'\d+', score.text).group())
        else:
            score = np.nan
        scores.append(score)
        
    dates = page.find_all('span', class_='age')
    dates = [date.attrs["title"] for date in dates]
    # convert dates to datetime objects from 2024-04-09T06:24:15 format to 2024-04-09 06:24:15
    dates = [datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') for date in dates]
    # convert dates to strings in the format 2024-04-09 06:24:15
    dates = [date.strftime('%Y-%m-%d %H:%M:%S') for date in dates]
    print("Adding to database....")

    # add to  dataframe
    df = pd.concat([df, pd.DataFrame({'id': ids, 'title': titles, 'link': links, 'date': dates, 'score': scores, 'rank': ranks})], ignore_index=True)
    x += 1
df.to_csv('hacker_news.csv', index=False)
df.to_sql('hacker_news', sqlite3.connect('hacker_news.db'), if_exists='replace', index=False)
print("Done")

from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from datetime import datetime as dt
import pyodbc


def load_into_table(review_df):
    # Database connection details
    conn = pyodbc.connect(r'Driver={SQL Server};Server=LAPTOP-VUL4TP1T;DATABASE=trip_advicer;Trusted_Connection=yes;')
    cursor = conn.cursor()
    for index,row in review_df.iterrows():
        # Extract each row from the dataframe and insert into the database
        cursor.execute("insert into hotel_ratings(name,dt,location,rating,sub,review) values (?,?,?,?,?,?)",row['name'], row['date'], row['location'], row['rating'], row['subject'],row['review'])
        # commit the insert statement
        conn.commit()
    conn.close()
    return True



def get_data(date_filter,url,main_url):
    review_df = pd.DataFrame(columns=['name', 'date', 'location', 'rating', 'subject', 'review'])
    next_page = 'NotNone'
    while(next_page != None):
        r = requests.get(url)
        soup = BeautifulSoup(r.content,'html.parser')
        content_list = soup.find_all('div',{'class':'review basic_review inlineReviewUpdate provider0'})
        for content in content_list:
            user_name = content.find('div',{'class':'username mo'}).text
            if(content.find('div',{'class':'location'}) != None):
                location = content.find('div',{'class':'location'}).text
            else:
                location = None
            subject = content.find('span',{'class':'noQuotes'}).text
            review_text = content.find('div', {'class': 'entry'}).text
            reviewslist = content.find('div',{'class':'rating reviewItemInline'})
            rating = reviewslist.find('span').get("class")[1][-2:-1]
            date = reviewslist.find('span',{'class':'ratingDate relativeDate'}).get('title')
            current_date = dt.strptime(date_filter,"%d %B %Y")
            content_date = dt.strptime(date,"%d %B %Y")
            print(current_date,content_date)
            # Check if the current date and the extracted content date is equal, if so extract data
            if (current_date == content_date):
                dict = {'name':user_name,'date':date,'location':location,'rating':rating,'subject':subject,'review':review_text}
                review_df.loc[len(review_df)]=dict
            else:
                #if not exit the loop and stop checking the next pages
                next_page = None
                break
        nxt_rltv_pg_url = soup.find('a', {'class': 'nav next rndBtn ui_button primary taLnk'})
        if (nxt_rltv_pg_url != None):
            url = main_url + nxt_rltv_pg_url.get('href')
        else:
            next_page = None
        time.sleep(40)
    #Load the extracted data into a table
    load_in_table = load_into_table(review_df)
    if(load_in_table):
        print("Load into database is sucessful")
    else:
        print("Load into database is unsucessful")



from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

# URL of the Crown plaza hotel that needs to be scrapped
url = 'https://www.tripadvisor.com.sg/Hotel_Review-g294265-d1086295-Reviews-Crowne_Plaza_Changi_Airport-Singapore.html#REVIEWS'
# URL of the trip advisor website
main_url = 'https://www.tripadvisor.com.sg'
# Export the extracted data to csv
file_path = "E:\\Hobby projects\\TripAdvicer\\TripAdvicer\\output\\hotel_rating1.csv"


# Iterates till the last page and stops if there are no more pages
next_page = 'NotNone'
while(next_page != None):
    review_df = pd.DataFrame(columns=['name','date','location','rating','subject','review'])
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'html.parser')
    # Extracts the 10 Rating per page
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
        print(date)
        dict = {'name':user_name,'date':date,'location':location,'rating':rating,'subject':subject,'review':review_text}
        print(dict)
        review_df.loc[len(review_df)]=dict

    # Gets the relative path of the next page
    nxt_rltv_pg_url = soup.find('a',{'class':'nav next rndBtn ui_button primary taLnk'})
    if(nxt_rltv_pg_url != None):
        #if it has a next page it would append it with the next main page
        url = main_url+nxt_rltv_pg_url.get('href')
        #print(url)
    else:
        #if not return none which would break the while loop
        next_page = None
    #Save the rating of each page in a csv file in an append mode
    review_df.to_csv(file_path,mode='a',index=False,header=None)
    #After scrapping each page the program would wait for 40 seconds . This is make sure that trip advicer does not identify a robot is scrapping its page.
    time.sleep(40)
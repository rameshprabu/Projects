from apscheduler.schedulers.blocking import BlockingScheduler
import  web_scrapper_to_table as webscrap
import time

sched = BlockingScheduler()

#schedules the "start_scheduler" method at an interval of every day
@sched.scheduled_job('interval',days=1)
def start_scheduler():
    # URL of page and main_url
    url = 'https://www.tripadvisor.com.sg/Hotel_Review-g294265-d1086295-Reviews-Crowne_Plaza_Changi_Airport-Singapore.html#REVIEWS'
    main_url = 'https://www.tripadvisor.com.sg'
    # get the current system date so that the programs scraps that particular days data alone
    current_date = time.strftime('%d %B %Y')
    webscrap.get_data(current_date,url,main_url)
sched.start()


#!/usr/local/bin/python3



import schedule
import json
import time
from plyer import notification
import os
from Scrape import scrape
import logging



logging.basicConfig(filename='script_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BackgroundNotification:
    def notify(self):
        schedule.every(1).to(2).hours.do(self.create_notification)
        while True:
            schedule.run_pending()
            logging.info(f'...')
            time.sleep(120)

    def load_json_file(self, file_name):
        try:
            with open(self.get_file(file_name), 'r') as read_json:
                return json.loads(read_json.read()) 
        except:
            return {}

    def get_file(self, file_name):
        return os.path.join(os.getcwd(), file_name)

    def create_notification(self):
        credentials = self.load_json_file('credentials.json')
        if credentials:
            scrape(credentials)
            scrapped_data = self.load_json_file('Sakai.json')
            if scrapped_data['status'] == 'new':
                scrapped_data["message-info-list"].reverse()
                for alert in scrapped_data["message-info-list"]:
                    notification.notify(
                        title=alert['type'], 
                        message=alert['body'], 
                        app_icon=self.get_file('icon.png')
                    )
                logging.info(f'Notification Created Successfully. Number of alerts: {len(scrapped_data["message-info-list"])}')
            else:
                logging.error(f'Sorry There Seems to have been an error (Probably No Internet Connection or Invalid Login details.PLease verify details in credentials.json file)')
        else:
            logging.error(f'Invalid Login details.PLease update details in credentials.json file)')




if __name__ == "__main__":
    BackgroundNotification().notify()



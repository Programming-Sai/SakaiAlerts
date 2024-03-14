


# Importing necessary modules and classes
import os
import json
import time
import logging
import schedule
from Scrape import scrape
from plyer import notification


# Configuring logging to write logs to a file named 'script_log.log'
logging.basicConfig(filename='script_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BackgroundNotification:
    """
        Class to handle background notifications.

        Attributes:
            None

        Methods:
            notify(self): Starts the notification loop.
            load_json_file(self, file_name): Loads data from a JSON file.
            get_file(self, file_name): Returns the absolute path to a file.
            create_notification(self): Creates desktop notifications based on scraped data.
    """

    def notify(self):
        """
            Starts the notification loop using the schedule module.
        """

        # Schedules notification creation every 1-2 hours
        schedule.every(1).to(2).hours.do(self.create_notification)
        
        while True:
            schedule.run_pending()  # Runs pending scheduled jobs
            logging.info(f'...')  # Logs a message indicating that the loop is running
            time.sleep(120)  # Pauses execution for 2 minutes

    def load_json_file(self, file_name):
        """
            Loads data from a JSON file.

            Parameters:
                file_name (str): The name of the JSON file.

            Returns:
                dict: Dictionary containing data loaded from the JSON file.
        """
        try:
            with open(self.get_file(file_name), 'r') as read_json:
                return json.loads(read_json.read()) 
        except:
            return {}

    def get_file(self, file_name):
        """
            Returns the absolute path to a file.

            Parameters:
                file_name (str): The name of the file.

            Returns:
                str: The absolute path to the file.
        """
        return os.path.join(os.getcwd(), file_name)

    def create_notification(self):
        """
            Creates desktop notifications based on scraped data.
        """

        # Loads login credentials from JSON file
        credentials = self.load_json_file('credentials.json')


        if credentials:

            # Scrapes data using provided credentials
            scrape(credentials)

            # Loads scraped data from JSON file
            scrapped_data = self.load_json_file('Sakai.json')

            if scrapped_data['status'] == 'new':

                # Reverses the list of alerts/messages
                scrapped_data["message-info-list"].reverse()

                # Iterates over the list of alerts and creates desktop notifications
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
    # Instantiates the BackgroundNotification class and starts the notification process
    BackgroundNotification().notify()



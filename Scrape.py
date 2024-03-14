# Importing necessary modules and classes


import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

 



def scrape_site(credentials, url, alert_body, alert_link):
    """
        Scrapes a specific page of the website to retrieve additional details about a particular alert.

        Parameters:
        - credentials (dict): Dictionary containing login credentials (studentID and password).
        - url (str): The URL of the page to scrape.
        - alert_body (str): The body of the alert message.
        - alert_link (str): The link associated with the alert message.

        Returns:
        - str: The link to the alert, potentially modified after scraping the site.
    """
    options = Options()


     # Runs the Chrome browser in headless mode (without GUI)
    options.add_argument("--headless")  
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    
    # Locating and entering login credentials
    name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'eid')))
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pw')))
    name.send_keys(credentials['studentID']) 
    password.send_keys(credentials['password']) 
    password.send_keys(Keys.ENTER)


    # Switching to iframe containing the announcements
    iframe = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#col2of2 .Mrphs-sakai-announcements .Mrphs-toolBody--sakai-announcements iframe')))
    driver.switch_to.frame(iframe)
    table_css_selector = "html body .container-fluid form .table-responsive table tbody tr th strong a"

    try:


        # Extracting information from the table
        table = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_css_selector)))
        main_announcement = [(item.text, item.get_attribute("href")) for item in table]
        for announcement_name, announcement_link in main_announcement:
            if announcement_name in alert_body:
                 return announcement_link
            
    except TimeoutException:
        print(f"Timed out waiting for the table with Selector: {table_css_selector}")
        return alert_link


    # Switching back to default content and quitting the driver
    driver.switch_to.default_content()
    driver.quit()




def get_file(file_name):
    """
        Returns the absolute path to a file.

        Parameters:
        - file_name(str): The name of the file.

        Returns:
        Returns:
        - (str): The absolute path to the file.

    """
    return os.path.join(os.getcwd(), file_name)


def get_announcement_link(link_to_dissect):
    """
        Constructs the full URL for a Sakai announcement link.

        Parameters:
        - link_to_dissect(str): The partial URL extracted from the Sakai website.

        Returns:
        - (str): The complete URL to the announcement.
    """
    return "https://sakai.ug.edu.gh/portal/site" + link_to_dissect[(link_to_dissect.index('/msg') + 4):(link_to_dissect.index('/main'))]




def date_manipulation(date):
    """
        Converts the date format from one format to another.

        Parameters:
        - date(str): The input date string.

        Returns:
        - (str): The formatted date string.
    """
    return datetime.strptime(date, "%m/%d/%Y %I:%M %p").strftime("%dth %B %Y - %I:%M %p")



def scrape(credentials):
        """
            Main function responsible for scraping the Sakai website.

            Parameters:
            - credentials(dict): Dictionary containing login credentials (studentID and password).

            Returns:
            - (str): String message indicating the status of the scraping process.
        """
        url = "https://sakai.ug.edu.gh/portal"
        alerts = {}
        alerts_messages = []
        alerts_count = 0
        alert_status = 'error'

        try:

            options = Options()
            options.add_argument("--headless") 


            # Initializing the Chrome WebDriver
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            

           
            # Entering login credentials
            name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'eid')))
            password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pw')))
            name.send_keys(credentials['studentID']) 
            password.send_keys(credentials['password']) 
            password.send_keys(Keys.ENTER)


             # Clicking on the alerts button to navigate to the alerts section
            alerts_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "portal-bullhorns-buttons")))
            alerts_button.click()


            # Locating the alerts container
            alerts_container = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "qtip-content")))


            # Extracting alert messages
            anns = driver.find_elements(By.CSS_SELECTOR, ".qtip-content .accordion .portal-bullhorn-bunch")
            for ann in anns:
                ann.click()
                
                type_of_alert = WebDriverWait(ann, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-header button .portal-bullhorn-bunch-title"))).text.split(" ")[0]

                m_all = WebDriverWait(ann, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".collapse .card-body .portal-bullhorn-alert")))
                
                for m in m_all:
                    alert_structure = WebDriverWait(m, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".portal-bullhorn-message div a")))
                    alert_time = WebDriverWait(m, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".portal-bullhorn-message .portal-bullhorn-time"))).text
                    alert_body = alert_structure.text
                    alert_link = alert_structure.get_attribute("href")
                
                    alert_link = alert_link if type_of_alert != "Announcements" else scrape_site(credentials, get_announcement_link(alert_link), alert_body, alert_link)
               
                
                    alerts_count += 1
                    alert_time = date_manipulation(alert_time)
                    alerts_messages.append(
                        {
                            "type": type_of_alert,
                            "body": alert_body, 
                            "time": alert_time, 
                            "link": alert_link 
                        }
                    )
            alert_status = 'new'
            alerts["count"] = alerts_count
            alerts["status"] = alert_status
            alerts["message-info-list"] = alerts_messages
            

        except Exception as e:
            return(f"\nSorry An Error Has Occured\nError: \n{e}")

        
        finally:
            driver.quit()
            alerts["count"] = alerts_count
            alerts["status"] = alert_status
            alerts["message-info-list"] = alerts_messages
            # Writing the alert data to a JSON file
            with open(get_file("Sakai.json"), "w") as al:
                    al.write(json.dumps(alerts, indent= 4))   
            return "Scraped Successfully" if alert_status == 'new' else f"\nSorry An Error Has Occured\nError: \n{e}"

    

    
 










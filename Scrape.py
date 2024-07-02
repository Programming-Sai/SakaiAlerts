import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

# Path to chromedriver executable 
chromedriver_path = './chromedriver-mac-x64/chromedriver'






# Function to scrape a specific site
def scrape_site(credentials, url, alert_body, alert_link, driver):
    """
        Scrapes a specific page of the website to retrieve additional details about a particular alert.

        Parameters:
        - credentials (dict): Dictionary containing login credentials (studentID and password).
        - url (str): The URL of the page to scrape.
        - alert_body (str): The body of the alert message.
        - alert_link (str): The link associated with the alert message.
        - driver (WebDriver): Instance of WebDriver used for scraping.

        Returns:
        - str: The link to the alert, potentially modified after scraping the site.
    """
    try:
        driver.get(url)

        name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'eid')))
        password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pw')))
        name.send_keys(credentials['studentID'])
        password.send_keys(credentials['password'])
        password.send_keys(Keys.ENTER)

        iframe = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#col2of2 .Mrphs-sakai-announcements .Mrphs-toolBody--sakai-announcements iframe')))
        driver.switch_to.frame(iframe)
        table_css_selector = "html body .container-fluid form .table-responsive table tbody tr th strong a"

        try:
            # Retry loop to handle StaleElementReferenceException
            for _ in range(3):  # Retry up to 3 times
                try:
                    table = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_css_selector)))
                    main_announcement = [(item.text, item.get_attribute("href")) for item in table]
                    for announcement_name, announcement_link in main_announcement:
                        if announcement_name in alert_body:
                            return announcement_link
                    break  # Exit retry loop if successful
                except StaleElementReferenceException:
                    continue  # Retry if StaleElementReferenceException occurs

        except TimeoutException:
            print(f"Timed out waiting for the table with Selector: {table_css_selector}")
            return alert_link

    except Exception as e:
        print(f"Error in scraping site: {str(e)}")
        return alert_link

    finally:
        driver.switch_to.default_content()








# Main scraping function
def scrape(credentials):
    """
        Main function responsible for scraping the Sakai website.

        Parameters:
        - credentials (dict): Dictionary containing login credentials (studentID and password).

        Returns:
        - str: String message indicating the status of the scraping process.
    """
    url = "https://sakai.ug.edu.gh/portal"
    alerts = {}
    alerts_messages = []
    alerts_count = 0
    alert_status = 'error'
    error = ""
    driver = None  # Initialize driver outside the try block

    try:
        options = Options()
        options.add_argument("--headless")

        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'eid')))
        password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pw')))
        name.send_keys(credentials['studentID'])
        password.send_keys(credentials['password'])
        password.send_keys(Keys.ENTER)

        alerts_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "portal-bullhorns-buttons")))
        alerts_button.click()

        alerts_container = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "qtip-content")))

        anns = driver.find_elements(By.CSS_SELECTOR, ".qtip-content .accordion .portal-bullhorn-bunch")
        for ann in anns:
            ann.click()

            type_of_alert = WebDriverWait(ann, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-header button .portal-bullhorn-bunch-title"))).text.split(" ")[0]

            m_all = WebDriverWait(ann, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".collapse .card-body .portal-bullhorn-alert")))

            for m in m_all:
                try:
                    alert_structure = WebDriverWait(m, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".portal-bullhorn-message div a")))
                    alert_time = WebDriverWait(m, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".portal-bullhorn-message .portal-bullhorn-time"))).text
                    alert_body = alert_structure.text
                    alert_link = alert_structure.get_attribute("href")

                    try:
                        alert_link = alert_link
                    except Exception as e:
                        alert_link = alert_link if type_of_alert != "Announcements" else scrape_site(credentials, get_announcement_link(alert_link), alert_body, alert_link, driver)


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
                except StaleElementReferenceException:
                    continue  # Skip this alert and move to the next

        alert_status = 'new'
        alerts["count"] = alerts_count
        alerts["status"] = alert_status
        alerts["message-info-list"] = alerts_messages

        print(alerts)

    except Exception as e:
        error = e
        return f"\nSorry An Error Has Occurred\nError: {str(e)}"

    finally:
        if driver:
            driver.quit()
        alerts["count"] = alerts_count
        alerts["status"] = alert_status
        alerts["message-info-list"] = alerts_messages
        with open(get_file("Sakai.json"), "w") as al:
            al.write(json.dumps(alerts, indent=4))
        return "Scraped Successfully" if alert_status == 'new' else f"\nSorry An Error Has Occurred\nError: {error}"




# Function to get the file path
def get_file(file_name):
    """
        Returns the absolute path to a file.

        Parameters:
        - file_name(str): The name of the file.

        Returns:
        - (str): The absolute path to the file.
    """
    return os.path.join(os.getcwd(), file_name)





# Function to manipulate date format
def date_manipulation(date):
    """
        Converts the date format from one format to another.

        Parameters:
        - date(str): The input date string.

        Returns:
        - (str): The formatted date string.
    """
    return datetime.strptime(date, "%m/%d/%Y %I:%M %p").strftime("%dth %B %Y - %I:%M %p")




# Function to get announcement link
def get_announcement_link(link_to_dissect):
    """
        Constructs the full URL for a Sakai announcement link.

        Parameters:
        - link_to_dissect(str): The partial URL extracted from the Sakai website.

        Returns:
        - (str): The complete URL to the announcement.
    """
    return "https://sakai.ug.edu.gh/portal/site" + link_to_dissect[(link_to_dissect.index('/msg') + 4):(link_to_dissect.index('/main'))]

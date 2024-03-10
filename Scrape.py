from selenium import webdriver
import json
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

 



def scrape_site(url, alert_body, alert_link):
    options = Options()
    options.add_argument("--headless")  
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'eid')))
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pw')))
    name.send_keys('11222100')
    password.send_keys('27678')
    password.send_keys(Keys.ENTER)

    iframe = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#col2of2 .Mrphs-sakai-announcements .Mrphs-toolBody--sakai-announcements iframe')))
    driver.switch_to.frame(iframe)
    table_css_selector = "html body .container-fluid form .table-responsive table tbody tr th strong a"

    try:
        table = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_css_selector)))
        main_announcement = [(item.text, item.get_attribute("href")) for item in table]
        for announcement_name, announcement_link in main_announcement:
            if announcement_name in alert_body:
                 return announcement_link
            
    except TimeoutException:
        print(f"Timed out waiting for the table with Selector: {table_css_selector}")

    driver.switch_to.default_content()
    driver.quit()
    return alert_link





def get_file(file_name):
    return os.path.join(os.getcwd(), file_name)



def get_announcement_link(link_to_dissect):
    return "https://sakai.ug.edu.gh/portal/site" + link_to_dissect[(link_to_dissect.index('/msg') + 4):(link_to_dissect.index('/main'))]




def date_manipulation(date):
    return datetime.strptime(date, "%m/%d/%Y %I:%M %p").strftime("%dth %B %Y - %I:%M %p")



def scrape(credentials):
        url = "https://sakai.ug.edu.gh/portal"
        alerts = {}
        alerts_messages = []
        alerts_count = 0
        alert_status = 'error'

        try:

            options = Options()
            options.add_argument("--headless")  

            driver = webdriver.Chrome(options=options)
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
                    alert_structure = WebDriverWait(m, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".portal-bullhorn-message div a")))
                    alert_time = WebDriverWait(m, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".portal-bullhorn-message .portal-bullhorn-time"))).text
                    alert_body = alert_structure.text
                    alert_link = alert_structure.get_attribute("href")
                
                    alert_link = alert_link if type_of_alert != "Announcements" else scrape_site(get_announcement_link(alert_link), alert_body, alert_link)
               
                
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
          with open(get_file("Sakai.json"), "w") as al:
                  al.write(json.dumps(alerts, indent= 4))   


    

    
 










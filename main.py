"""
SakaiAlerts Application

This script implements an application for monitoring alerts from a Sakai platform.
It allows users to log in, view alert history, and scrape new alerts from the Sakai platform.

Classes:
    SakaiAlerts: Main application class managing screens and functionality.
    Sakai_Scrapper: Screen class for scraping new alerts.
    Sakai_Log: Screen class for viewing alert history.
    Sakai_Login: Screen class for obtaining user login details and theme preferences.

Functions:
    get_file(file_name): Helper function to get the absolute path of a file in the current directory.
    add(container, *args): Helper function to add multiple widgets to a container.
    screen_change(change_to): Function to transition between screens.
    load_login_details(): Function to load login details from a JSON file.

Attributes:
    LoadingScreen: Widget class representing a loading animation.
"""




# Importing system modules

import os
import sys
import json
import random
import subprocess
import webbrowser
from threading import Thread

# Importing Kivy and KivyMD classes

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.clock import mainthread
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.uix.checkbox import CheckBox
from kivymd.theming import ThemeManager
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, TwoLineListItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import  NumericProperty, ListProperty, BooleanProperty
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton, MDIconButton, MDRoundFlatButton

# Importing other neccesary modules

from Scrape import scrape
from plyer import notification


 

# Define helper functions




def get_file(file_name):
    """
        Gets the absolute path of a file in the current directory.

        Parameters:
        - file_name(str): A string that holds the name of the file to obtain.

        Returns:
        - (str): The string holding the absolute path to th erequired file.
    """
    return os.path.join(os.getcwd(), file_name)

def add(container, *args):
    """
        Add multiple widgets to a container dynamically, making the coding process easier.

        Parameters:
        - container(Obj): An object that holds the widget that should contain other widgets.
        - args(Obj): A placeholder variable for holding objects that are the widgets to br sdded to the  container.

    """
    for arg in args:
        container.add_widget(arg)

def screen_change(change_to):
    """
        Transition between screens.

        Parameters:
        - change_to(str): A string that holds the name of the screen to change to.

    """
    app = MDApp.get_running_app() 
    app.root.transition.direction = 'left'
    app.root.current = change_to

def load_login_details():
    """
        Loads login details and theme preferences from a JSON file.
        
        Returns:
        - (dict): The dictionary holding the login details and theme preferences data from the JSON file.
    """
    try:
        with open(get_file('credentials.json'), 'r') as f:
            cred = f.read()
        return json.loads(cred)
    except:
        return {}
    
def restart_background_process():
    """
        Restarts teh bacground_notify.py file if it stops running in the background.it is intended to be called whenver teh user starts the app.
    """
    try:
        subprocess.check_output(["pgrep", "-f", "background_notify.py"])
        print("Background notification in progress.....")
    except subprocess.CalledProcessError:
        try:
            subprocess.Popen(['nohup', sys.executable, get_file('background_notify.py'), '&'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            print("Background notification RESTARTED successfully.")
        except Exception as e:
            print(f"Error RESTARTING background notification: {e}")














class LoadingScreen(Widget):
     
    """
        LoadingScreen Widget Class

        This widget represents a loading animation.
    """
     
    start = NumericProperty(0)
    duration = NumericProperty(0)
    interval = NumericProperty(random.randint(100, 150))
    overlay_color = ListProperty([96/255, 125/255, 139/255, 0.3])  
    counter = 0
    is_on_top = BooleanProperty(True)
    Builder.load_string(
"""
<LoadingScreen>:
    
    canvas.before:
        Color:
            rgba: self.overlay_color
        Rectangle:
            pos: 0, 0
            size: 100000000000, 1000000000

    canvas.after:
        Color:
            rgba: [96/255, 125/255, 139/255, 0.6]
        Line:
            width: 3
            ellipse: (self.x, self.y, self.width, self.height, 0, 360)
        Color:
            # rgb: [69/255, 90/255, 100/255]
            rgb: [0, 0, 1]
        Line:
            width: 3
            ellipse: (self.x, self.y, self.width, self.height, self.start, (self.start + self.interval))
"""
    )

    def __init__(self, **kwargs):
        """
            Class Initialization.
        """
        super(LoadingScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.animate, 0)

    def animate(self, *args):
        """
            Starts animation.
        """
        Clock.schedule_interval(self.start_move, 1 / 60)

    def start_move(self, *args):
        """
            Updates animation.
        """
        self.counter += random.randint(5, 10)
        self.start = self.counter



         
# Screen Class Definitions



class Sakai_Login(Screen):
    """
        Sakai_Login Screen Class

        This screen allows users to provide their login details to allow for the retrieval of data from the Sakai platform.
    """
    def __init__(self, **kwargs):
        """
            Initializes Sakai_Login Screen.
        """
        super(Sakai_Login, self).__init__(**kwargs)
        self.add_widget(self.show())

    def next_field(self, instance):
        """
            Moves TextField focus to the password field from the StudentId field
        """
        self.password.focus = True

    def on_checkbox_press(self, checkbox, mode):
        """
            Updates `credentials.json` file with the correct mode.

            Parameters:
            - mode(str): Tells the mode which the user prefers.(Dark / Light)
        """
        login_details = load_login_details()
        login_details["mode"] = mode
        with open(get_file('credentials.json'), 'w') as f:
            f.write(json.dumps(login_details, indent=4))
    
    def show(self):
        """
            Defines Widgets and UI for the screen.
        """

        # Setting up Screen
        screen = Screen()      


        # Fetching data from `credentials.json` file
        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())

        
        # Setting up TextFields
        self.studentID = MDTextField(hint_text="StudentID", pos_hint={'center_x':0.5, 'center_y':0.7}, size_hint_x=0.7, font_size=25, icon_right='account')
        self.password = MDTextField(hint_text="Password", pos_hint={'center_x':0.5, 'center_y':0.6}, size_hint_x=0.7, font_size=25, password=True, icon_right='eye', password_mask="•")


        # Setting up TextFields Functionalities
        self.studentID.bind(on_text_validate = lambda instance : self.next_field(instance))
        self.password.bind(on_text_validate = lambda instance : self.confirm())


        # Settinup submit buttin
        submit = MDRoundFlatButton(text="Submit Details", pos_hint={'center_x':0.5, 'center_y':0.2}, font_size=20)
        submit.bind(on_release= lambda instance : self.confirm())


        # Setting up Radio Buttons
        self.dark_mode = CheckBox(group="mode", size_hint=(0.3, 0.3), pos_hint={"center_x":0.15, "center_y":0.4}, color=[136/255, 176/255, 201/255, 1.0], active= True if credents.get("mode") == "Dark" else False)
        self.light_mode = CheckBox(group="mode", size_hint=(0.3, 0.3), pos_hint={"center_x":0.75, "center_y":0.4}, color=[136/255, 176/255, 201/255, 1.0], active= True if credents.get("mode") == "Light" else False)
        
        
        # Setting up Radio Buttons Functionalities
        self.dark_mode.bind(on_press=lambda instance: self.on_checkbox_press(instance, "Dark"))
        self.light_mode.bind(on_press=lambda instance: self.on_checkbox_press(instance, "Light"))


        # Providing a Label for the Radio Button
        dark_label = Label(text="Dark", pos_hint={"center_x":0.25, "center_y":0.4}, color=("black" if credents.get("mode") == "Light" else "white"))
        light_label = Label(text="Light", pos_hint={"center_x":0.82, "center_y":0.4}, color=("black" if credents.get("mode") == "Light" else "white"))
        

        # Providing a password visibility functionality feature
        eye = MDIconButton(icon='', pos_hint={'center_x':0.825, 'center_y':0.61}, theme_icon_color="Hint")
        eye.bind(on_release=lambda instance : self.on_eye())

        
        # Using the helper function to dynamically add the widgets to the screen. This is much easuer than doing `sceen.add_widget(...)` a bunch of times.
        add(screen, self.dark_mode, dark_label, self.light_mode, light_label,  self.studentID, self.password, submit, eye, MDTopAppBar(title="Login Info", pos_hint={'top':1}, right_action_items=[["bell", lambda instance : screen_change("sakai_scrapper")], ["history", lambda instance : screen_change("sakai_log")]]))
       
       
        return screen
    
    def confirm(self):
        """
            A Dialig box for confirming the users choice of saving their entered dara or not
        """
        self.confirmer = MDDialog(
            auto_dismiss=True,
            text="Are You Sure You Are Ready To Submit?",
            buttons=[
                MDFlatButton(text='Yes', on_press=lambda x: self.confirm_options('yes')),
                MDFlatButton(text='No', on_press=lambda x: self.confirm_options('no'))
            ]
        )
        self.confirmer.open()

    def add_shebang_to_file(self):
        """
            Adds shebang line at the top of teh `background_notify.py` file.
        """

        # Define the path to the background_notify.py file

        # Define the shebang line to add
        shebang_line = "#!" + sys.executable + "\n\n"

        should_add_line = False
        
        with open(get_file('background_notify.py'), "r") as file:
            if file.readline != shebang_line:
                should_add_line = True
            content = file.read()

        with open(get_file('background_notify.py'), "w") as file:
            if should_add_line:
                file.write(shebang_line + content)

    def start_background_process(self):
        """
            Initiating Background Process Specified in `background_notify.py` file.
        """
        try:
            subprocess.Popen(['nohup', sys.executable, get_file('background_notify.py'), '&'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            print("Background notification started successfully.")
        except Exception as e:
            print(f"Error starting background notification: {e}")

    def confirm_options(self, option):
        """
            Logic to complete when the user proceeds to input their details and choose their theme preference.

            Parameters:
            option(str): this determins if the user has selected `yes` or `no`.
        """

        # Fetching data from `credentials.json` 

        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())


        # Checking if the user has agreed to place oin their details.
            
        if option == 'yes':
            credentials = {
                "studentID":self.studentID.text,
                "password":self.password.text,
                "mode":"Dark" if self.dark_mode == True else "Light" or "Light" if self.light_mode ==True else "Dark",
                "background-started": credents.get("background-started", False)
            }

            # This Begins the background process once and only once
             
            if not credentials["background-started"]:
                self.add_shebang_to_file()
                self.start_background_process()
                credentials["background-started"] = True
            
            # And finally the details are written to the file and the UI is uodated accordingly.
                
            with open(get_file('credentials.json'), 'w') as cred:
                cred.write(json.dumps(credentials, indent=4))
            screen_change('sakai_scrapper')
            self.studentID.text = ""
            self.password.text = ""
            self.password.icon_right = 'eye'
            self.password.password = True           
        self.confirmer.dismiss()

    def on_eye(self):

        """
            This toggles the password visibility and the icon assiciated with it.
        """
        
        if self.password.icon_right == 'eye':
            self.password.icon_right = 'eye-off'
            self.password.password = False
        else:
            self.password.icon_right = 'eye'
            self.password.password = True

   




class Sakai_Log(Screen):
    """
        Sakai_Login Screen Class

        This screen allows users to provide their login details to allow for the retrieval of data from the Sakai platform.
    """
    def __init__(self, **kwargs):
        """
            Initializes Sakai_Log Screen.
        """
        super(Sakai_Log, self).__init__(**kwargs)
        self.add_widget(self.show())
         
    def open_popup(self, link, alert_type, alert_body):
        """
            Opens a diaog box for the user to select which action to perform on each alert.

            Parameters:
            link(str): This is the link for the alert or announcement.
            alert_type(str): This is the category  of alerts under which the selected alert falls under.
            alert_body(str): This is the content of the alert selected or at least the summarised version of it. 

        """
        self.dialog = MDDialog(
            title=alert_type[:-1],
            auto_dismiss=True,
            text=alert_body,
            buttons=[
                MDFlatButton(text='Open in Browser', on_press=lambda x: webbrowser.open(link)),
                MDFlatButton(text='Close', on_press=lambda x: self.dialog.dismiss())
            ]
        )
        
        self.dialog.open()

    def load_history(self):
        """
            Fetches the history of all alerts ever scraped for trhe user
        """
        with open(get_file('Sakai-Log.json'), 'r') as mjr:
            log_ = mjr.read()
        return json.loads(log_)
    
    def clear(self):
        """
            Clears or deletes the history of alerts.
        """
        default_history = {
             "log-count": 0,
            "message-log-info-list": []
        }
        with open(get_file('Sakai-Log.json'), 'w') as mjw:
             mjw.write(json.dumps(default_history, indent=4)) 

    def refresh(self):
        """
            Updates the UI after the `clear` method has been called. 
        """
        self.scroll_area.clear_widgets()
        self.screen.remove_widget(self.scroll_area)
        self.screen.add_widget(MDLabel(text="History Cleared", pos_hint={'center_x':0.5, 'center_y':0.5}, font_style = 'H3', halign='center', theme_text_color="Hint"))

    def clear_and_refresh(self):
        """
            Provides a simple way to call both functions at once. ie. ,`self.clear()` and `self.refresh()`
        """
        self.clear()
        self.refresh()

    def create_history_list(self):
        """
            This generates the UI for each alert found in the `Sakai-Log.json` file
        """
        self.history["message-log-info-list"].reverse()

        for i, hist in enumerate(self.history["message-log-info-list"] , start=1):
            self.list_item = TwoLineListItem(text = str(i) + "    " + hist['body'], secondary_text = "       " + hist['time'])

            self.list_item.bind(on_release=lambda instance, link=hist['link'], alert_type=hist['type'], alert_body=hist['body']: self.open_popup(link, alert_type, alert_body))

            add(self.history_list, self.list_item)
        
    def show(self):
        """
            Defines Widgets and UI for the screen.
        """

        # Setting up Screen
        self.screen = Screen()


        # Setting up scrollview and MDlist (something like a fancy container for other widgets which should hold the information abou the alerts)
        self.scroll_area = ScrollView(do_scroll_x=True, size_hint=(0.95, 0.9),pos_hint={'center_x':0.5, 'center_y':0.45})
        self.history_list = MDList()

        # Fetching the History data by calling its method.
        self.history = self.load_history()


        # Generating UI for the alerts by calling its method.
        self.create_history_list()


        # Setting up a fallback Label in case the history is yet to be made.
        empty = MDLabel(text="Empty History", pos_hint={'center_x':0.5, 'center_y':0.5}, font_style = 'H3', halign='center', theme_text_color="Hint")


        # Dynamically adding all the widgets to their respective containers.
        add(self.scroll_area, self.history_list if len(self.history["message-log-info-list"]) > 0 else empty)
        add(self.screen, self.scroll_area, MDTopAppBar(title="Alert History", pos_hint={'top':1}, right_action_items=[["bell", lambda instance : screen_change("sakai_scrapper")], ["account", lambda instance : screen_change('sakai_login')], ["delete", lambda instance : self.clear_and_refresh()]]))

        return self.screen






class Sakai_Scrapper(Screen):
    """
        Sakai_Scrapper Screen Class

        This screen allows users to scrape new alerts from the Sakai platform.
    """
    def __init__(self, **kwargs):
        """
            Initialize Sakai_Scrapper.
        """
        super(Sakai_Scrapper, self).__init__(**kwargs)
        self.scrapping = False
        self.alerts, self.log_sakai = self.load_json_files()
        self.add_widget(self.show())

    def show(self):
        """
            Defines Widgets and UI for the screen.
        """

        # Setting up Screen
        self.screen = Screen()


        # Setting up scrollview and MDlist (something like a fancy container for other widgets which should hold the information abou the alerts)
        self.scroll_screen = ScrollView(do_scroll_x=True, size_hint=(0.95, 0.67),pos_hint={'center_x':0.5, 'center_y':0.55})
        self.result_list = MDList()



        # Defining Some Screen Widgets


        # Providong a label that tells the user the number of alerts available.
        self.alert_count =  MDLabel( text=("Alert Count: " + str(self.get_alert_count())), 
                                pos_hint={'center_x': 0.5, 'center_y': 0.15}, 
                                size_hint = (1, 1), 
                                theme_text_color="Hint",
                                font_style = 'H6', 
                                halign='center'
                            )
    

        # Provides the functionality of scraping and refreshing the UI and.
        refresh_btn = MDFillRoundFlatButton(text="Scrape and Refresh",
                                        size_hint = (0.2, 0.05), 
                                        pos_hint= {'center_x':0.5,'center_y':0.07}, 
                                        font_size=25)
        
        refresh_btn.bind(on_release=lambda instance : self.scrape_and_refresh(instance))



        # Setting up Loading Screen
        self.loading_cycle = LoadingScreen(
            size_hint = (None, None),
            size = (50, 50),
            pos_hint = {'center_x': 0.5, 'center_y': 0.5},
            overlay_color = [96/255, 125/255, 139/255, 0.6],
            is_on_top = True
        )

        # Dynamically adding all the widgets to their respective containers.
        add(self.screen, 
                 MDTopAppBar(title="New Alerts", 
                             pos_hint={'top':1},
                             right_action_items = [["history", lambda instance : screen_change('sakai_log')], ["account", lambda instance : screen_change('sakai_login')]]
                             ), 
                 self.alert_count,
                 self.create_result_list(),  
                 refresh_btn
                 )
        
        add(self.screen)

        return self.screen
    
    def create_result_list(self):
            """
                Generates UI for The newly scraped alerts
            """


            # Clearing the ScrollView and MDlist.

            self.scroll_screen.clear_widgets()
            self.result_list.clear_widgets()
            
            # Setting up Label for the case when there are no alerts.
            if len(self.alerts["message-info-list"]) == 0:
                add(self.scroll_screen, MDLabel(text="No Alerts Found", 
                                            pos_hint= {'center_x':0.5,'center_y':0.5}, 
                                            font_style = 'H4',
                                            halign='center', 
                                            theme_text_color="Hint")
                                            )  

            # Providing UI for the case when there are actually new alerts. 
            else:
                for i, alert in enumerate(self.alerts["message-info-list"], start=1):

                    if alert not in self.log_sakai['message-log-info-list']:
                        self.append_log_json(alert)

                    self.list_item = TwoLineListItem(text = str(i) + "    " + alert['body'], secondary_text = "       " + alert['time'])

                    self.list_item.bind(on_release=lambda instance, link=alert['link'], alert_type=alert['type'], alert_body=alert['body']: self.open_popup(link, alert_type, alert_body))

                    add(self.result_list, self.list_item)
                    notification.notify(title=alert['type'], message=alert['body'], app_icon=get_file('icon.png'))
                    
                    
                add(self.scroll_screen, self.result_list)

            return self.scroll_screen

    def load_json_files(self):
        """
            Fetching Data from JSON files.

            Returns:
            (tuple): two dictionaries containing fetched data. 
        """
        with open(get_file('Sakai.json'), 'r') as sakai:
            alerts_attempt = sakai.read()
        alerts = json.loads(alerts_attempt)

        with open(get_file('Sakai-Log.json'), 'r') as mjr:
            log_ = mjr.read()
        log_sakai = json.loads(log_)

        return (alerts, log_sakai)

    def append_log_json(self, new_dict):
        """
            Updating The alert history with newly scraped alerts.

            Parameters:
            new_dict(dict): This is the newly added dictionary to be appenden.
        """
        with open(get_file('Sakai-Log.json'), 'r') as mjr:
            log_ = mjr.read()
        self.log_sakai = json.loads(log_)
        self.log_sakai['message-log-info-list'].append(new_dict)
        self.log_sakai['log-count'] = len(self.log_sakai['message-log-info-list'])
        with open('Sakai-Log.json', 'w') as mjw:
            mjw.write(json.dumps(self.log_sakai, indent=4))

    def open_popup(self, link, alert_type, alert_body):
        """
            Opens a diaog box for the user to select which action to perform on each alert.

            Parameters:
            link(str): This is the link for the alert or announcement.
            alert_type(str): This is the category  of alerts under which the selected alert falls under.
            alert_body(str): This is the content of the alert selected or at least the summarised version of it. 

        """
        print("open_popup function called")
        self.dialog = MDDialog(
            title=alert_type[:-1],
            auto_dismiss=True,
            text=alert_body,
            buttons=[
                MDFlatButton(text='Open in Browser', on_press=lambda x: webbrowser.open(link)),
                MDFlatButton(text='Close', on_press=lambda x: self.dialog.dismiss())
            ]
        )
        
        self.dialog.open()
    
    def error_popup(self):
        """
            Provides a dialog box for the case when the scrape operaion failed.
        """
        self.error = MDDialog(
            auto_dismiss=True,
            text="Sorry An Error Has Occurred",
            buttons=[
                MDFlatButton(text='Close', on_press=lambda x: self.error.dismiss())
            ]
        )
        self.error.open()

    def refresh(self, status):
        """
            Determines the updating of the UI based on teh success/ failure of the scrape opeartion.

            Parameters:
            status(str): This tells whether or not the scrape oprationwas successful or not. ie `error` or `new`.

        """
        if status == 'new':
            self.create_result_list() 
            self.alert_count.text = ("Alert Count: " + str(self.get_alert_count())) 
        else:
            self.error_popup()

    def buttons_toggle(self):
        """
            This provides a way to turn of or disallow some actions during the scrape operation.
        """
        if self.loading_cycle.is_on_top:
            for child in self.screen.children:
                if isinstance(child, MDFillRoundFlatButton): 
                    child.disabled = True
                elif isinstance(child, ScrollView):
                    child.do_scroll_y = False
                    child.do_scroll_x = False
                elif isinstance(child, MDTopAppBar):
                    child.right_action_items = [
                        ["history"], 
                        ["account"]
                    ]
        else:
            for child in self.screen.children:
                for child in self.screen.children:
                    if isinstance(child, MDFillRoundFlatButton):
                        child.disabled = False
                    elif isinstance(child, ScrollView):
                        child.do_scroll_y = True
                        child.do_scroll_x = False
                    elif isinstance(child, MDTopAppBar):
                        child.right_action_items = [
                            ["history", lambda instance : screen_change('sakai_log')], 
                            ["account", lambda instance : screen_change('sakai_login')]
                        ]
                             
    @mainthread
    def remove_loading_cycle(self, status):
        """
            This clears the `LoadingScreen` widget after the scraping operation

            Parameters:
            status(str): This tells whether or not the scrape oprationwas successful or not. ie `error` or `new`.

        """
        self.screen.remove_widget(self.loading_cycle)
        self.loading_cycle.is_on_top = False
        self.buttons_toggle()
        self.refresh(status)

    def scrape_and_refresh(self, instance):
        """
            Provides a simple way to call both functions at once. ie. ,`self.scrape()` and `self.refresh()`
        """
        self.loading_cycle.is_on_top = True
        self.buttons_toggle()
        self.screen.add_widget(self.loading_cycle)
        Thread(target=self.scrape).start()

    def scrape(self, *args):
        """
            Carries out the actual scrape operation. 
        """
        print(scrape(load_login_details()))
        self.alerts, self.log_sakai = self.load_json_files()
        status = self.alerts['status']
        Clock.schedule_once(lambda dt: self.remove_loading_cycle(status), 0)
        return status
  
    def get_alert_count(self):
        """
            This more like a helper method that gets the number of newly scraped alerts.
        """
        return self.alerts['count']

 





class SakaiAlerts(MDApp):
    """
        SakaiAlerts Application Class

        This is the main application class managing screens and functionality.
    """
    def build(self):
        """
            Build the application.
        """


       
        # Fetching data from the `credentials.json` file
        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())


        # Restarts the background opeartion if neccessary. 
        if credents.get("background-started"):
            restart_background_process()
        


        # Set theme settings
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.theme_style = self.get_mode()


        # Create screen manager
        Screens = ScreenManager()

        
        # Add screens based on login status
        if credents:
            Screens.add_widget(Sakai_Scrapper(name='sakai_scrapper'))
            Screens.add_widget(Sakai_Log(name='sakai_log'))
            Screens.add_widget(Sakai_Login(name='sakai_login'))
        else:
            Screens.add_widget(Sakai_Login(name='sakai_login'))
            Screens.add_widget(Sakai_Scrapper(name='sakai_scrapper'))
            Screens.add_widget(Sakai_Log(name='sakai_log'))


        return Screens
    
    def get_mode(self):
        """
            Gets the currently selected mode by the user from the `credentials.json` file
        """
        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())
        return credents.get("mode") or "Dark"
    
    

if __name__ == '__main__':
    SakaiAlerts().run()














import subprocess
import sys
import webbrowser
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton, MDIconButton, MDRoundFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivymd.uix.textfield import MDTextField
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import  NumericProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.clock import mainthread
import random
import os
import json
from Scrape import scrape
from plyer import notification
from background_notify import BackgroundNotification
from threading import Thread


 





def get_file(file_name):
    return os.path.join(os.getcwd(), file_name)

def add(container, *args):
    for arg in args:
        container.add_widget(arg)

def screen_change(change_to):
    app = MDApp.get_running_app() 
    app.root.transition.direction = 'left'
    app.root.current = change_to

def load_login_details():
    try:
        with open(get_file('credentials.json'), 'r') as f:
            cred = f.read()
        return json.loads(cred)
    except:
        return {}
    












class LoadingCycle(Widget):
    start = NumericProperty(0)
    duration = NumericProperty(0)
    interval = NumericProperty(random.randint(100, 150))
    overlay_color = ListProperty([96/255, 125/255, 139/255, 0.3])  
    counter = 0
    is_on_top = BooleanProperty(True)
    Builder.load_string(
"""
<LoadingCycle>:
    
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
        super(LoadingCycle, self).__init__(**kwargs)
        Clock.schedule_once(self.animate, 0)

    def animate(self, *args):
        Clock.schedule_interval(self.start_move, 1 / 60)

    def start_move(self, *args):
        self.counter += random.randint(5, 10)
        self.start = self.counter



         




class Sakai_Login(Screen):
    def __init__(self, **kwargs):
        super(Sakai_Login, self).__init__(**kwargs)
        self.add_widget(self.show())

    def next_field(self, instance):
        self.password.focus = True

    def on_checkbox_press(self, checkbox, mode):
        login_details = load_login_details()
        login_details["mode"] = mode
        with open(get_file('credentials.json'), 'w') as f:
            f.write(json.dumps(login_details, indent=4))
    
    def show(self):
        screen = Screen()        

        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())

        self.studentID = MDTextField(hint_text="StudentID", pos_hint={'center_x':0.5, 'center_y':0.7}, size_hint_x=0.7, font_size=25, icon_right='account')
        self.password = MDTextField(hint_text="Password", pos_hint={'center_x':0.5, 'center_y':0.6}, size_hint_x=0.7, font_size=25, password=True, icon_right='eye', password_mask="•")

        self.studentID.bind(on_text_validate = lambda instance : self.next_field(instance))
        self.password.bind(on_text_validate = lambda instance : self.confirm())

        submit = MDRoundFlatButton(text="Submit Details", pos_hint={'center_x':0.5, 'center_y':0.2}, font_size=20)
        submit.bind(on_release= lambda instance : self.confirm())


        self.dark_mode = CheckBox(group="mode", size_hint=(0.3, 0.3), pos_hint={"center_x":0.15, "center_y":0.4}, color=[136/255, 176/255, 201/255, 1.0], active= True if credents.get("mode") == "Dark" else False)
        self.light_mode = CheckBox(group="mode", size_hint=(0.3, 0.3), pos_hint={"center_x":0.75, "center_y":0.4}, color=[136/255, 176/255, 201/255, 1.0], active= True if credents.get("mode") == "Light" else False)
       
        self.dark_mode.bind(on_press=lambda instance: self.on_checkbox_press(instance, "Dark"))
        self.light_mode.bind(on_press=lambda instance: self.on_checkbox_press(instance, "Light"))


        dark_label = Label(text="Dark", pos_hint={"center_x":0.25, "center_y":0.4}, color=("black" if credents.get("mode") == "Light" else "white"))
        light_label = Label(text="Light", pos_hint={"center_x":0.82, "center_y":0.4}, color=("black" if credents.get("mode") == "Light" else "white"))
        
        eye = MDIconButton(icon='', pos_hint={'center_x':0.825, 'center_y':0.61}, theme_icon_color="Hint")
        eye.bind(on_release=lambda instance : self.on_eye())

        

        add(screen, self.dark_mode, dark_label, self.light_mode, light_label,  self.studentID, self.password, submit, eye, MDTopAppBar(title="Login Info", pos_hint={'top':1}, right_action_items=[["bell", lambda instance : screen_change("sakai_scrapper")], ["history", lambda instance : screen_change("sakai_log")]]))
        return screen
    
    def confirm(self):
        self.confirmer = MDDialog(
            auto_dismiss=True,
            text="Are You Sure You Are Ready To Submit?",
            buttons=[
                MDFlatButton(text='Yes', on_press=lambda x: self.confirm_options('yes')),
                MDFlatButton(text='No', on_press=lambda x: self.confirm_options('no'))
            ]
        )
        self.confirmer.open()
        
    def start_background_process(self):
        try:
            subprocess.Popen(['nohup', sys.executable, get_file('background_notify.py'), '&'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            print("Background notification started successfully.")
        except Exception as e:
            print(f"Error starting background notification: {e}")

    def confirm_options(self, option):
        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())


        if option == 'yes':
            credentials = {
                "studentID":self.studentID.text,
                "password":self.password.text,
                "mode":"Dark" if self.dark_mode == True else "Light" or "Light" if self.light_mode ==True else "Dark",
                "background-started": credents.get("background-started", False)
            }

            if not credentials["background-started"]:
                self.start_background_process()
                credentials["background-started"] = True



            with open(get_file('credentials.json'), 'w') as cred:
                cred.write(json.dumps(credentials, indent=4))
            screen_change('sakai_scrapper')
            self.studentID.text = ""
            self.password.text = ""
            self.password.icon_right = 'eye'
            self.password.password = True           
        self.confirmer.dismiss()

    def on_eye(self):
        
        if self.password.icon_right == 'eye':
            self.password.icon_right = 'eye-off'
            self.password.password = False
        else:
            self.password.icon_right = 'eye'
            self.password.password = True

   




class Sakai_Log(Screen):
    def __init__(self, **kwargs):
        super(Sakai_Log, self).__init__(**kwargs)
        self.add_widget(self.show())
         
    def open_popup(self, link, alert_type, alert_body):
        
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
        with open(get_file('Sakai-Log.json'), 'r') as mjr:
            log_ = mjr.read()
        return json.loads(log_)
    
    def clear(self):
        default_history = {
             "log-count": 0,
            "message-log-info-list": []
        }
        with open(get_file('Sakai-Log.json'), 'w') as mjw:
             mjw.write(json.dumps(default_history, indent=4)) 

    def refresh(self):
        self.scroll_area.clear_widgets()
        self.screen.remove_widget(self.scroll_area)
        self.screen.add_widget(MDLabel(text="History Cleared", pos_hint={'center_x':0.5, 'center_y':0.5}, font_style = 'H3', halign='center', theme_text_color="Hint"))

    def clear_and_refresh(self):
        self.clear()
        self.refresh()

    def create_history_list(self):

        self.history["message-log-info-list"].reverse()

        for i, hist in enumerate(self.history["message-log-info-list"] , start=1):
            self.list_item = TwoLineListItem(text = str(i) + "    " + hist['body'], secondary_text = "       " + hist['time'])

            self.list_item.bind(on_release=lambda instance, link=hist['link'], alert_type=hist['type'], alert_body=hist['body']: self.open_popup(link, alert_type, alert_body))

            add(self.history_list, self.list_item)
        

    def show(self):
        self.screen = Screen()

        self.scroll_area = ScrollView(do_scroll_x=True, size_hint=(0.95, 0.9),pos_hint={'center_x':0.5, 'center_y':0.45})
        self.history_list = MDList()

        self.history = self.load_history()

        self.create_history_list()

        empty = MDLabel(text="Empty History", pos_hint={'center_x':0.5, 'center_y':0.5}, font_style = 'H3', halign='center', theme_text_color="Hint")

        add(self.scroll_area, self.history_list if len(self.history["message-log-info-list"]) > 0 else empty)
        add(self.screen, self.scroll_area, MDTopAppBar(title="Alert History", pos_hint={'top':1}, right_action_items=[["bell", lambda instance : screen_change("sakai_scrapper")], ["account", lambda instance : screen_change('sakai_login')], ["delete", lambda instance : self.clear_and_refresh()]]))

        return self.screen






class Sakai_Scrapper(Screen):
    def __init__(self, **kwargs):
        super(Sakai_Scrapper, self).__init__(**kwargs)
        self.scrapping = False
        self.alerts, self.log_sakai = self.load_json_files()
        self.add_widget(self.show())

    def show(self):
        self.screen = Screen()

        self.scroll_screen = ScrollView(do_scroll_x=True, size_hint=(0.95, 0.67),pos_hint={'center_x':0.5, 'center_y':0.55})
        self.result_list = MDList()

        self.alert_count =  MDLabel( text=("Alert Count: " + str(self.get_alert_count())), 
                                pos_hint={'center_x': 0.5, 'center_y': 0.15}, 
                                size_hint = (1, 1), 
                                theme_text_color="Hint",
                                font_style = 'H6', 
                                halign='center'
                            )
    
        refresh_btn = MDFillRoundFlatButton(text="Scrape and Refresh",
                                        size_hint = (0.2, 0.05), 
                                        pos_hint= {'center_x':0.5,'center_y':0.07}, 
                                        font_size=25)
        
        refresh_btn.bind(on_release=lambda instance : self.scrape_and_refresh(instance))
        add(self.screen, 
                 MDTopAppBar(title="New Alerts", 
                             pos_hint={'top':1},
                             right_action_items = [["history", lambda instance : screen_change('sakai_log')], ["account", lambda instance : screen_change('sakai_login')]]
                             ), 
                 self.alert_count,
                 self.create_result_list(),  
                 refresh_btn
                 )
        
        self.loading_cycle = LoadingCycle(
            size_hint = (None, None),
            size = (50, 50),
            pos_hint = {'center_x': 0.5, 'center_y': 0.5},
            overlay_color = [96/255, 125/255, 139/255, 0.6],
            is_on_top = True
        )

        add(self.screen)

        return self.screen
    
    def create_result_list(self):
            self.scroll_screen.clear_widgets()
            
            self.result_list.clear_widgets()

            if len(self.alerts["message-info-list"]) == 0:
                add(self.scroll_screen, MDLabel(text="No Alerts Found", 
                                            pos_hint= {'center_x':0.5,'center_y':0.5}, 
                                            font_style = 'H4',
                                            halign='center', 
                                            theme_text_color="Hint")
                                            )          
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
        with open(get_file('Sakai.json'), 'r') as sakai:
            alerts_attempt = sakai.read()
        alerts = json.loads(alerts_attempt)

        with open(get_file('Sakai-Log.json'), 'r') as mjr:
            log_ = mjr.read()
        log_sakai = json.loads(log_)

        return (alerts, log_sakai)

    def append_log_json(self, new_dict):
        with open(get_file('Sakai-Log.json'), 'r') as mjr:
            log_ = mjr.read()
        self.log_sakai = json.loads(log_)
        self.log_sakai['message-log-info-list'].append(new_dict)
        self.log_sakai['log-count'] = len(self.log_sakai['message-log-info-list'])
        with open('Sakai-Log.json', 'w') as mjw:
            mjw.write(json.dumps(self.log_sakai, indent=4))

    def open_popup(self, link, alert_type, alert_body):
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
        self.error = MDDialog(
            auto_dismiss=True,
            text="Sorry An Error Has Occurred",
            buttons=[
                MDFlatButton(text='Close', on_press=lambda x: self.error.dismiss())
            ]
        )
        self.error.open()

    def refresh(self, status):
        if status == 'new':
            self.create_result_list() 
            self.alert_count.text = ("Alert Count: " + str(self.get_alert_count())) 
        else:
            self.error_popup()

    def buttons_toggle(self):
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
        self.screen.remove_widget(self.loading_cycle)
        self.loading_cycle.is_on_top = False
        self.buttons_toggle()
        self.refresh(status)

    def scrape_and_refresh(self, instance):
        self.loading_cycle.is_on_top = True
        self.buttons_toggle()
        self.screen.add_widget(self.loading_cycle)
        Thread(target=self.scrape).start()

    def scrape(self, *args):
        print(scrape(load_login_details()))
        self.alerts, self.log_sakai = self.load_json_files()
        status = self.alerts['status']
        Clock.schedule_once(lambda dt: self.remove_loading_cycle(status), 0)
        return status
  
    def get_alert_count(self):
        return self.alerts['count']

 





class SakaiAlerts(MDApp):
    def build(self):
        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())

        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.theme_style = self.get_mode()

        Screens = ScreenManager()

        

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
        with open(get_file('credentials.json'), 'r') as cred:
            credents = json.loads(cred.read())
        return credents.get("mode") or "Dark"
    
    

if __name__ == '__main__':
    SakaiAlerts().run()














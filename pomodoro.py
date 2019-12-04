from __future__ import print_function
import rumps
import pickle
import os.path
import math
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
from datetime import timedelta 


class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("--")
        self.menu = ["Start Session", "End Session"]
        self.status = 'init' # none, sess, break, inter, init
        self.start_cur = datetime.now()
        self.init_goal = ""
        self.sess_len = 25
        self.break_len = 5
        self.menu['End Session'].set_callback(None)
        self.menu['Start Session'].set_callback(self.start_click)

    def start_new_sess(self):
        self.status = "inter"
        test = rumps.Window(message="", title='Start Pomodoro Session', default_text='use mouse clicks to copy paste', ok="Start", cancel="Procrastinate", dimensions=(320,80))
        test.icon = "/Users/clemens/Documents/Misc/pomodoro/invisible.png"
        response = test.run()
        if response.clicked == 1:
            self.init_goal = response.text
            self.start_cur = datetime.now()
            self.status = "sess"
            self.title = self.get_remain(self.sess_len)
            self.menu['End Session'].set_callback(self.end_click)
            self.menu['Start Session'].set_callback(None)
        else:
            self.title = "--:--"
            self.init_goal = ""
            self.status = "none"
            self.menu['End Session'].set_callback(None)
            self.menu['Start Session'].set_callback(self.start_click)
        

    def end_sess(self):
        end_time = datetime.now()
        self.status = "inter"
        self.title = "--:--"
        test = rumps.Window(message="Goal: "+self.init_goal, title='Session Done!', default_text='use mouse clicks to copy paste', ok="Start Break", cancel="Finish", dimensions=(320,80))
        test.icon = "/Users/clemens/Documents/Misc/pomodoro/invisible.png"
        response = test.run()
        # log the session
        self.g_test(self.start_cur, end_time, self.init_goal, response.text)
        if response.clicked == 1:
            self.init_goal = ""
            self.start_cur = datetime.now()
            self.status = "break"
        else:
            self.title = "--:--"
            self.init_goal = ""
            self.status = "none"
        self.menu['End Session'].set_callback(None)
        self.menu['Start Session'].set_callback(self.start_click)


    def get_remain(self, time_l):
        time_passed = (datetime.now() - self.start_cur).seconds
        sec_str = (  str(60 - time_passed%60) if time_passed%60 != 0 else "00" )
        min_str = str(time_l - math.ceil(time_passed/60))
        return (min_str if len(min_str) == 2 else '0' + min_str ) + ":" + (sec_str if len(sec_str) == 2 else '0' + sec_str )
    

    #@rumps.clicked("Start Session")
    def start_click(self, sender):
        if self.status == "none" or self.status == "break":
            self.start_new_sess()

    #@rumps.clicked("End Session")
    def end_click(self, sender):
        if self.status == "break":
            self.title = "--:--"
            self.init_goal = ""
            self.status = "none"
        elif self.status == "sess":
            self.end_sess()
        else:
            pass

    @rumps.timer(1)  # create a new thread that calls the decorated function every 4 seconds
    def update_time(self, _):
        if self.status == "none":
            pass
        elif self.status == "inter":
            pass
        elif self.status == "init":
            self.title = "--:--"
            self.status = "none"
        elif self.status == "sess":
            if (datetime.now() - self.start_cur) < timedelta(minutes=self.sess_len):
                self.title = self.get_remain(self.sess_len)
            else:
               self.end_sess()

        elif self.status == "break":
            if (datetime.now() - self.start_cur) < timedelta(minutes=self.break_len):
                self.title = self.get_remain(self.break_len)
            else:
                self.start_new_sess()


    def g_test(self, start_t, end_t, title, outcome):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/Users/clemens/Documents/Misc/credentials.json', ['https://www.googleapis.com/auth/calendar'])
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

        
        # creat an event
        event = {
          'summary': title,
          'location': 'Notre Dame',
          'description': 'Pomodoro Session\nGoal: '+title+'\nAchieved: '+outcome,
          'start': {
            'dateTime':  start_t.strftime("%Y-%m-%dT%H:%M:%S-05:00"), # 
            'timeZone': 'America/New_York',
          },
          'end': {
            'dateTime':  end_t.strftime("%Y-%m-%dT%H:%M:%S-05:00"), # '2019-12-03T17:00:00-07:00', #
            'timeZone': 'America/New_York',
          },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))





if __name__ == "__main__":
    AwesomeStatusBarApp().run()



from __future__ import print_function
import datetime
import pickle
import os.path
import os
import tabula
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    #sign_in()
    filter_events()


def sign_in():
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    #print(service.calendarList().list().execute())

    # Call the Calendar API
    #create_event(service,"TEST",datetime(2020,3,3,8,20),datetime(2020,3,3,8,30))

def filter_events():
    #tabula.convert_into("plan.pdf", "output.json", output_format="json", pages='all')
    events = []
    with open('output.json') as json_file:
        whole_json = json.load(json_file)
        data = whole_json[0]['data']

    temp = 22
    print(data[temp][0]["text"])
    print(kind_identifier(data[temp][0]["text"]))
    print(len(data))
    print(len(data[0]))

    for x in range(0, len(data[0])):
        for y in range(0, len(data)):
            content = data[y][x]["text"]
            if kind_identifier(content) == "time":
                text, start_day_time, end_day_time = "", datetime(1970,1,1,1,1), datetime(1970,1,1,1,2)
                if kind_identifier(data[y+1][x]["text"]) == "content" and kind_identifier(data[y+2][x]["text"]) == "content": 
                    #Wenn die beiden folgenden Zeilen Vorlesungen sind
                    text = ' '.join([data[y+1][x]["text"], data[y+2][x]["text"]])
                else:
                    text = data[y+1][x]["text"]
                
                if kind_identifier(data[y-1][x]["text"]) == "weekday":
                    time_list = strftime(content)
                    print(time_list)
                    date_list = strfdate(data[y-1][x]["text"])
                    day_time = datetime(date_list[0], date_list[1], date_list[2]) #todo: Attach time

                event = {
                    'start' : start_day_time,
                    'end' : end_day_time,
                    'text': text
                }


def kind_identifier(input):
    weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

    if "Woche" in input or input == "":
        return "skip"
    elif "-" in input:
        return "time"
    elif len(input) > 1:
        for day in weekdays:
            if input.startswith(day):
                return "weekday"
        return "content"
    
def strfdate(input):
    input = input[-10:]
    temp = [input[-4:], input[-7:-5], input[:2]]
    return temp

def strftime(input):
    #result[start hour, start minute, end hour, end minute]
    result = [-1,-1,-1,-1]
    dot = input.find('.')
    result[0] = int(input[:dot])
    result[1] = int(input[dot + 1:dot+3])

    return result
    


    

def create_event(service,Vorlesung, Start, End):
    event = {
        'summary': Vorlesung,
        'location': "Unknown",
        'description': "",
        'start': {
            'dateTime': Start.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': "Europe/Berlin",
        },
        'end': {
            'dateTime': End.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': "Europe/Berlin",
        },
        'attendees': [],
        'reminders': {
            'useDefault': True,
            'overrides': [
            ],
        },
    }
    event = service.events().insert(calendarId='calubl9uctbhmpr428hb1pk878@group.calendar.google.com', body=event).execute()

if __name__ == '__main__':
    main()
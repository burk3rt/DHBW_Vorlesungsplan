'''
    Installation:
    1. Python 3.7 herunterladen
    2. pip install virtualenv
    3. pip -r requirements.txt
    4. source env/bin/activate
'''
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
    #Creates the filtered events
    events = filter_events()
    for event in events:
        create_event(service,event['text'],event['start'],event['end'])
        print(event)
        pass
    print("Probably done")

def filter_events():
    tabula.convert_into("plan.pdf", "output.json", output_format="json", pages='all')
    events = []
    with open('output.json') as json_file:
        whole_json = json.load(json_file)
        data = whole_json[0]['data']

    #Filters events data
    counter = 0
    for x in range(0, len(data[0])):
        for y in range(0, len(data)):
            content = data[y][x]["text"]
            if kind_identifier(content) == "time":
                text, start_day_time, end_day_time = "", datetime(1970,1,1,1,1), datetime(1970,1,1,1,2)
                #Adds content to event
                if kind_identifier(data[y+1][x]["text"]) == "content" and kind_identifier(data[y+2][x]["text"]) == "content": 
                    #Wenn die beiden folgenden Zeilen Vorlesungen sind
                    text = ' '.join([data[y+1][x]["text"], data[y+2][x]["text"]])
                else:
                    text = data[y+1][x]["text"]
                #Adds date and time to event
                if kind_identifier(data[y-1][x]["text"]) == "weekday":
                    time_list = strftime(content)
                    date_list = strfdate(data[y-1][x]["text"])
                    start_day_time = datetime(date_list[0], date_list[1], date_list[2],time_list[0],time_list[1])
                    end_day_time = datetime(date_list[0], date_list[1], date_list[2],time_list[2],time_list[3])
                else: #needed for 2nd event on one day
                    tempY = y-1
                    while not kind_identifier(data[tempY][x]["text"]) == "weekday":
                        tempY -= 1
                    
                    time_list = strftime(content)
                    date_list = strfdate(data[tempY][x]["text"])
                    start_day_time = datetime(date_list[0], date_list[1], date_list[2],time_list[0],time_list[1])
                    end_day_time = datetime(date_list[0], date_list[1], date_list[2],time_list[2],time_list[3])    

                event = {
                    'start' : start_day_time,
                    'end' : end_day_time,
                    'text': text
                }

                if len(event['text']) > 1: 
                    events.append(event)
                    counter +=1
    print(str(counter) + " events found")
    return events

#identifies the kind of the input in weekday, time, content or skippable
def kind_identifier(input):
    weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

    if "Woche" in input or input == "":
        return "skip"
    elif ("-" in input or "–" in input) and "." in input and input[:1].isdigit():
        return "time" # NICHT EINDEUTIG
    elif len(input) > 1:
        for day in weekdays:
            if input.startswith(day):
                return "weekday"
        return "content"
    
# transforms 16.03.2020 to list[2020,3,16]
def strfdate(input):
    input = input[input.find(',') + 2:]
    temp = [int(input[-4:]), int(input[-7:-5]), int(input[:2])]
    return temp

# transforms 09.00 - 12.15 to list[9,0,12,15]
def strftime(input):
    result = [-1,-1,-1,-1]
    dot = input.find('.')
    result[0] = int(input[:dot])
    result[1] = int(input[dot + 1:dot+3])

    input = input[input.find('-') + 1:]
    dot = input.find('.')
    result[2] = int(input[:dot])
    result[3] = int(input[dot + 1:dot+3])

    return result
    
#Create events, change calendar id is necessary 
def create_event(service,Vorlesung, Start, End):
    event = {
        'summary': Vorlesung,
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
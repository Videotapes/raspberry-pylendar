import arrow
import os
import pickle
from typing import Union

from classes.exceptions.CustomExceptions import CredentialsNotFoundException

from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class GoogleCalendar:
    """An individual Google Calendar instance

    Attributes
    ----------
    calendar_id : str
        Calendar ID of the retrieved Google Calendar
    credentials : google.oauth2.credentials.Credentials
        Google auth credentials
    calendar_connection : googleapiclient.discovery.Resource
        Google calendar connection object
    events : list
        List of calendar event dictionaries
    """

    def __init__(self, calendar_id="primary"):
        """Initializes the GoogleCalendar instance.
        
        Parameters
        ----------
        calendar_id : str, optional
            Determines calendar for connection; defaults to primary.
        """ 

        self.calendar_id = calendar_id
        self.credentials = None
        self.calendar_connection = None
        self.events = []
    
    def connect(self):
        """Initiates a connection to the Google Calendar associated with the supplied credentials.

        Raises
        ------
        CredentialsNotFoundException
            Pickled credentials were not found in the top-level directory.
        """
        path = os.path.join(".", "token.pickle")
        if os.path.exists(path):
            with open("token.pickle", "rb") as token:
                self.credentials = pickle.load(token)
        else:
            raise CredentialsNotFoundException("Calendar API credentials not found")

        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())

        self.calendar_connection = build("calendar", "V3", credentials=self.credentials)

    def refresh_credentials(self):
        """Manually refresh Google credentials."""

        if self.credentials:
            self.credentials.refresh(Request())
    
    def get_events(self, total=1):
        """Fetches a set of events ocurring after current system time 
        from the connected calendar and stores them in the events attribute.

        Parameters
        ----------
        total : int, optional
            Number of events to fetch from the calendar; defaults to 1.
        """

        current_time = arrow.utcnow().isoformat()
        current_time = current_time.split("+")[0] + "Z"
        
        self.events = self.calendar_connection.events().list(
            calendarId=self.calendar_id, timeMin=current_time,
            maxResults=total, singleEvents=True, orderBy="startTime").execute()

        # shear off the additional top-level user info we're not interested in
        self.events = self.events.get("items", [])
        # get rid of "outOfOffice" events
        self.events = [event for event in self.events if event["eventType"] == "default"]

        self.__append_arrow_datetimes()
    
    def get_event_starts(self) -> list:
        """Returns a list of event start datetimes from the last fetched event list.
        
        Returns
        -------
        list
            A list of event start Arrow datetimes
        """
        return [event["arrowStart"] for event in self.events]

    def get_event_ends(self) -> list:
        """Returns a list of event end datetimes from the last fetched event list.

        Returns
        -------
        list
            A list of event end Arrow datetimes
        """
        return [event["arrowEnd"] for event in self.events]

    def check_upcoming_events(self) -> bool:
        """Returns a boolean based on whether current stored events are upcoming."""

        event_starts = self.get_event_starts()

        return any(time > arrow.now() for time in event_starts)
    
    def get_next_event(self) -> Union[dict, bool]:
        """Returns the next upcoming event in stored events.
        
        Returns
        -------
        dict
            A dictionary containing the next upcoming event
        bool
            False; returned only if there is no upcoming event
        """
        
        if self.events:
            next_event_time = min(event["arrowStart"] for event in self.events if event["arrowStart"] > arrow.now())
            return [event for event in self.events if event["arrowStart"] == next_event_time][0] 
        else:
            return False

    def __append_arrow_datetimes(self):

        for event in self.events:
            event["arrowStart"] = arrow.get(event["start"]["dateTime"]).replace(tzinfo=event["start"]["timeZone"])
            event["arrowEnd"] = arrow.get(event["end"]["dateTime"]).replace(tzinfo=event["end"]["timeZone"])





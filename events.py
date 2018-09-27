import json

# Map Watson strings to TeamCalendar strings
VACATION_TYPES = {
    'working from home': 'Working from home',
    'sickness': 'Sick day',
    'site visit' : 'Site visit',
    'vacation': 'Vacation'
    }

class VacationEvent():
    def __init__(self, user, type, start_date, end_date):
        self.user = user
        self.type = VACATION_TYPES[type]
        # add time to the events (full day always)
        # TODO: make this time zone agnostic
        self.start = start_date + 'T00:00:00.000Z'
        self.end = end_date + 'T23:59:59.999Z'
        self.resizable = { 'beforeStart': True, 'afterEnd': True }
        self.draggable = True
        self.title = ''
        self.color = {'primary': '', 'secondary': ''}

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


if __name__ == "__main__":
    event = VacationEvent('john', VACATION_TYPES['working from home'], '2019-01-05', '2019-01-06')
    print(event.toJSON())

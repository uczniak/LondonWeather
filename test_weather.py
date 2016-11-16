import requests
from threading import Thread
import weather

REF_DATA = {'description': "clear sky",
            'humidity': "63%",
            'temperature': "17C",
            'kelvin': "290K",
            'pressure': "1024.87"}

ALL_ITEMS = ['description', 'humidity', 'temperature', 'pressure']

# start app in background
def start_app():
    with open('forecast.json','r') as f:
        weather.forecast = {obs['dt_txt']: obs for obs in weather.json.load(f)['list']}
    weather.app.run()

t = Thread(None, start_app)
t.daemon = True
t.start()

def test_good():
    r = requests.get("http://localhost:5000/weather/london/20160705/2100/")
    data = r.json()
    for item in ALL_ITEMS:
        assert data[item] == REF_DATA[item]

def test_single_item():
    for item in ALL_ITEMS:
        r = requests.get("http://localhost:5000/weather/london/20160705/2100/{}".format(item))
        data = r.json()
        assert len(data) == 1
        assert data[item] == REF_DATA[item]

def test_bad_datetime():
    r = requests.get("http://localhost:5000/weather/london/20160705/2101/")
    data = r.json()
    assert data['status'] == "error"
    assert data['message'] == "No data for 2016-07-05 21:01"

def test_bad_item():
    r = requests.get("http://localhost:5000/weather/london/20160705/2100/foo")
    data = r.json()
    assert data['status'] == "error"
    assert data['message'] == "'foo' is not a valid weather parameter name"

def test_kelvin():
    r = requests.get("http://localhost:5000/weather/london/20160705/2100/temperature/?t=k")
    data = r.json()
    assert len(data) == 1
    assert data['temperature'] == REF_DATA['kelvin']
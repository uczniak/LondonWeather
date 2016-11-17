import requests
from threading import Thread
from datetime import datetime, timedelta
import weather

REF_DATA = {'description': "clear sky",
            'humidity': "63%",
            'temperature': "17C",
            'kelvin': "290K",
            'pressure': "1024.87"}

ALL_ITEMS = ['description', 'humidity', 'temperature', 'pressure']

# current global limit per hour - ensure tests don't use more per view
LIMIT = 60

# start app in background
t = Thread(None, weather.app.run)
t.daemon = True
t.start()

def test__validation():
    result_good = weather.convert_datetime('20161116','2029')
    result_bad = weather.convert_datetime('9999foo','b@r4')
    assert result_bad is None
    assert result_good == "2016-11-16 20:29:00"

def test_good():
    r = requests.get("http://localhost:5000/weather/london/20160705/2100/")
    data = r.json()
    for item in ALL_ITEMS:
        assert data[item] == REF_DATA[item]

def test_current():
    day_after_tomorrow = datetime.now() + timedelta(days=2)
    day_after_tomorrow_url = datetime.strftime(day_after_tomorrow,"%Y%m%d/0000/")
    r = requests.get("http://localhost:5000/weather/london/{}".format(day_after_tomorrow_url))
    data = r.json()
    assert len(data) == 4

def test_single_item():
    for item in ALL_ITEMS:
        r = requests.get("http://localhost:5000/weather/london/20160705/2100/{}".format(item))
        data = r.json()
        assert len(data) == 1
        assert data[item] == REF_DATA[item]

def test_bad_datetime_format():
    r = requests.get("http://localhost:5000/weather/london/9999foo/b@r4/")
    data = r.json()
    assert data['status'] == "error"
    assert data['message'] == "Invalid date or time entered"

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

def test_rate_limit():
    # this has to be the last test
    for _ in range(LIMIT+1):
        r = requests.get("http://localhost:5000/weather/london/20160705/2100/")
    assert "Too Many Requests" in r.text

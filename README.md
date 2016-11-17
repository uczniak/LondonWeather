# LondonWeather
Simple REST API for retrieving London weather forecast.

## Installation
You need Python (tested on 3.5.1+ and 2.7.12) and:
* Flask (`pip install Flask`),
* requests (`pip install requests`),
* Flask-Limiter (`pip install Flask-Limiter`)

To start the service simply run `weather.py`.

Service will be running on Flask default `http://localhost:5000/`.

## API
Please kindly note that the use of API is limited to 60 requests per hour per view.

There are following endpoints available:

* `/weather/london/<date>/<time>/` where `<date>` is in YYYYMMDD format and `<time>` is in HHMM format.
Entries are available for 00:00, 03:00 etc. every 3 hours. This gives you the summary in JSON format:
```json
{
  "description": "broken clouds", 
  "humidity": "83%", 
  "pressure": "1022.38", 
  "temperature": "17C"
}
```

* `/weather/london/<date>/<time>/<item>/` where `<item>` is in `['description', 'humidity', 'pressure', 'temperature']`.
This gives you a single item from the above summary:
```json
{
  "temperature": "17C"
}
```

* You can specify `?t=k` in the query string to have temperature given in Kelvin.

In case of invalid input or missing data, a JSON object with error message will be generated looking like this:
```json
{
  "message": "No data for 2016-07-08 21:01", 
  "status": "error"
}
```

## Tests
To run tests you need pytest (`pip install -U pytest`).

While in project directory, simply type `pytest` to run the whole suite.
Please note that the tests can take a while as the last test checks if limits are applied correctly
and has to exhaust them first.

To check test coverage, make sure you have pytest-cov (`pip install pytest-cov`) and run
`pytest --cov=weather` from project folder.

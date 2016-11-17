from flask import Flask, json, jsonify, request, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from math import ceil
from datetime import datetime, MINYEAR, timedelta

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["60 per hour"],
)

with open('forecast.json', 'r') as f:
    forecast = {obs['dt_txt']: obs for obs in json.load(f)['list']}

forecast['last_update'] = datetime(MINYEAR,1,1)

def check_for_update():
    if datetime.now() - forecast['last_update'] > timedelta(days=1):
        update_forecast()

def update_forecast():
    r = requests.get("http://api.openweathermap.org/data/2.5/forecast?q=London,uk&APPID={appkey}"
                     .format(appkey="164795a1df804b59afcc6bbf8e19bcfe"))
    update_from_web = {obs['dt_txt']: obs for obs in r.json()['list']}
    forecast.update(update_from_web)
    forecast.update(last_update = datetime.now())

def convert_datetime(date, time):
    try:
        requested_datetime = datetime.strptime(date+'/'+time, "%Y%m%d/%H%M")
    except ValueError:
        return None
    return datetime.strftime(requested_datetime, "%Y-%m-%d %H:%M:%S")

def get_summary(snapshot):
    return dict(
        description="; ".join([item['description'] for item in snapshot['weather']]),
        temperature=("{}K".format(int(ceil(snapshot['main']['temp']))) if request.args.get('t','')=='k'
                                  else "{}C".format(int(ceil(snapshot['main']['temp'] - 273.15)))),
        pressure="{:.2f}".format(snapshot['main']['pressure']),
        humidity="{}%".format(snapshot['main']['humidity'])
    )

@app.route('/')
def show_docs():
    return redirect("https://github.com/uczniak/LondonWeather/blob/master/README.md#api")

@app.route('/weather/london/<date>/<time>/')
def show_summary(date,time):
    check_for_update()
    datetime_as_string = convert_datetime(date,time)
    if datetime_as_string is None:
        return jsonify(
            status="error",
            message="Invalid date or time entered"
        )
    if datetime_as_string in forecast:
        snapshot = forecast[datetime_as_string]
        return jsonify(get_summary(snapshot))
    # if date + time not found, return error object
    return jsonify(
        status = "error",
        message = "No data for {}".format(datetime_as_string[:-3])
    )

@app.route('/weather/london/<date>/<time>/<item>/')
def show_item(date,time,item):
    check_for_update()
    if item in ['description', 'humidity', 'pressure', 'temperature']:
        datetime_as_string = convert_datetime(date,time)
        if datetime_as_string is None:
            return jsonify(
                status="error",
                message="Invalid date or time entered"
            )
        if datetime_as_string in forecast:
            snapshot = forecast[datetime_as_string]
            summary = get_summary(snapshot)
            return jsonify({item: summary[item]})
        # if date + time not found, return error object
        return jsonify(
            status = "error",
            message = "No data for {}".format(datetime_as_string[:-3])
        )
    return jsonify(
        status="error",
        message="'{}' is not a valid weather parameter name".format(item)
    )

if __name__ in ["__main__"]:
    app.run()
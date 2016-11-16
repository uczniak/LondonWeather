from flask import Flask, json, jsonify, request
from math import ceil
from datetime import datetime

app = Flask(__name__)

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

@app.route('/weather/london/<date>/<time>/')
def show_summary(date,time):
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
    with open('forecast.json','r') as f:
        forecast = {obs['dt_txt']: obs for obs in json.load(f)['list']}
    app.run()
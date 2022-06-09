
import json
from turtle import st
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def prec():

    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_dt = dt.datetime.strptime(latest, '%Y-%m-%d')

    #Using the maximum value at each date
    msr_data = session.query(Measurement.date,func.max(Measurement.prcp)).\
        filter(Measurement.date <= latest_dt).\
        filter(Measurement.date > (latest_dt - dt.timedelta(days = 365))).\
        group_by(Measurement.date).\
        order_by(Measurement.date.desc()).\
        all()  

    prec_dict = {}

    for row in msr_data:
        prec_dict[row[0]] = row[1]

    session.close()
    return jsonify(prec_dict)
@app.route("/api/v1.0/stations")
def stations():

    act_stations = session.query(Station.station).all()
    stat_list = []
    for row in act_stations:
        stat_list.append(row[0])

    session.close()
    return jsonify(stat_list)

@app.route("/api/v1.0/tobs")
def temp():

    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_dt = dt.datetime.strptime(latest, '%Y-%m-%d')

    act_count = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    top_act = act_count[0][0]

    act_meas = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == top_act).\
        filter(Measurement.date <= latest_dt).\
        filter(Measurement.date > (latest_dt - dt.timedelta(days = 365))).\
        all()

    tob_dict = {}

    for row in act_meas:
        tob_dict[row[0]] = row[1]

    session.close()
    return jsonify(tob_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    sta_stats = session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        all()
    
    stats_dict = {}

    stats_dict[f"{start} onwards"] = {"Max":sta_stats[0][0], "Min": sta_stats[0][1], "Average": sta_stats[0][2]}

    session.close()
    return jsonify(stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def end_date(start, end):

    sta_stats = session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        all()
    
    stats_dict = {}

    stats_dict[f"{start} - {end}"] = {"Max":sta_stats[0][0], "Min": sta_stats[0][1], "Average": sta_stats[0][2]}

    session.close()
    return jsonify(stats_dict)

if __name__ == "__main__":
    app.run(debug=True)

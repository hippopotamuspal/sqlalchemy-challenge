
from flask import Flask, jsonify
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, text

# Declare a Base using `automap_base()`
Base=automap_base()

#Connecting to DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement and station classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)




#################################################
# Flask Routes
#################################################

#Create "/" Route
@app.route("/")

def yo():
    """Check out these sick routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>br/>")

#Create the precipitation route
@app.route("/api/v1.0/precipitation")

def itsrainin():
    """rain rain go away"""
    #find recent date
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    lastdate = datetime.strptime(lastdate, '%Y-%m-%d')
    firstdate = lastdate - timedelta(days=365)

    #doin the query for precip data in the last year
    precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= firstdate).all()

    #converting to a dictionary via iteration
    precip_dict = {date: prcp for date, prcp in precip}

    # Return the JSON representation of the dictionary
    return jsonify(precip_dict)


#create stations route

@app.route("/api/v1.0/stations")
def stations():
    """You are listening to station whatever"""
    
    #Query all stations
    stationdata = session.query(Station.station).all()

    #convert into a normal list
    stationslist = [station[0] for station in stationdata]

    #return JSON
    return jsonify(stationslist)

#4create station route

@app.route("/api/v1.0/tobs")
def tobs():
    """It's (maybe) hot out there folks!"""
    
    #find the most active station
    poppinstation = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    #most recent date for that station specifically
    poppinlastdate = session.query(Measurement.date).filter(Measurement.station == poppinstation).order_by(Measurement.date.desc()).first()[0]
    poppinlastdate = datetime.strptime(poppinlastdate, '%Y-%m-%d')
    poppinfirstdate = poppinlastdate - timedelta(days=365)

    #doin one of those queryt things for observations from the most active station in last year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station ==poppinstation).\
        filter(Measurement.date >= poppinfirstdate).all()

    #convert into a normal list
    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in tobs_data]

    #return JSON
    return jsonify(tobs_list)

#create start date route

@app.route("/api/v1.0/<start>")

def temp_stats_start(start):
    
    """Get that beginning date data!"""
    #doin the query for min, avr, and max temps
    tempstats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    #convert to a dictionary
    tempdict = {"Minimum Temperature": tempstats[0][0], "Average Temperature": tempstats[0][1], "Maximum Temperature": tempstats[0][2]}

    #return JSON
    return jsonify(tempdict)

#start & end date route

@app.route("/api/v1.0/<start>/<end>")

def tempstatsstartend(start, end):
    """Get that beginning and end date data!"""
    #doin the query for min, avr, and max temps
    tempstats2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    #convert into a dictionary
    tempdict2 = {"Minimum Temperature": tempstats2[0][0], "Average Temperature": tempstats2[0][1], "Maximum Temperature": tempstats2[0][2]}

    #return JSON
    return jsonify(tempdict2)

#run Flask app
if __name__ == '__main__':
    app.run(debug=True)  
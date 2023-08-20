# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    last_date = session.query(func.max(measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    year_ago = last_date - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()

    # Close the session
    session.close()
    
    # Convert list of tuples into normal list
    precipitation = {}
    for d, p in results:
        precipitation [d] = p

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # List all the stations
    station_results = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(desc(func.count(measurement.station))).all()

    # Close the session
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return the dates and temparature observations of the most-active station for the previous year of data"""
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station 
    last_date = session.query(func.max(measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = last_date - dt.timedelta(days=365)
    tobs_results = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= year_ago).all()
    
    # Close the session
    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_results))

    return jsonify(tobs_list)

@app.route("/api/v1.0/start")
def start():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return the minimum temp, the average temp, and the maximum temp for all dates greater than or equal to 6APR2016"""
    # Find all of the dates great than or equal to `2016-04-06` and return min avg and max temp
    start_results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= '2016-04-06').\
        group_by(measurement.date).all()
    
    # Close the session
    session.close()

     # Create a dictionary from the row data and append to a list of all_temps
    all_temps = []
    for date, min_temp, avg_temp, max_temp in start_results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["min_temp"] = min_temp
        temp_dict["avg_temp"] = avg_temp
        temp_dict["max_temp"] = max_temp
        all_temps.append(temp_dict)

    # Return a JSON list of temperature observations for the previous year
    return jsonify(all_temps)

@app.route("/api/v1.0/start/end")
def end():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return the minimum temp, the average temp, and the maximum temp for all dates between 6APR2016 and 9APR2016"""
    # Find all of the dates betwee `2016-04-06 and 2016-04-09` and return min avg and max temp
    start_results_end = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= '2016-04-06').\
        filter(measurement.date <= '2016-04-09').\
            group_by(measurement.date).all()
    
    # Close the session
    session.close()

     # Create a dictionary from the row data and append to a list of all_temps
    all_temps_end = []
    for date, min_temp, avg_temp, max_temp in start_results_end:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["min_temp"] = min_temp
        temp_dict["avg_temp"] = avg_temp
        temp_dict["max_temp"] = max_temp
        all_temps_end.append(temp_dict)

    # Return a JSON list of temperature observations for the previous year
    return jsonify(all_temps_end)

if __name__ == '__main__':
    app.run()
# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func, text, inspect

import flask
from flask import Flask , jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """set prior_year variable before session declaration to define prior_year filter"""
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   
    with Session(bind=engine) as session:
        """Retrieve 1 year percipitation data starting from prior year's date"""
        data = session.query(Measurement.prcp, Measurement.date).\
                filter(Measurement.date >= prior_year).\
                order_by(Measurement.date).all()
                
    """Convert list of tuples into normal list"""
    one_year = list(np.ravel(data))
    return jsonify(one_year)

"""**********************************************************************"""

@app.route("/api/v1.0/stations")
def stations():
    
    with Session(bind=engine) as session:
        """query all stations found in station column of station table"""
        station_list = session.query(Station.station).all()
   
    """Convert list of tuples into normal list & return json"""
    all_stations = list(np.ravel(station_list))
    return jsonify(all_stations)

"""**********************************************************************"""

@app.route("/api/v1.0/tobs")
def tobs():
   
    with Session(bind=engine) as session:
        """Return a list of most active station's temperature prior year"""
        station_temp = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= '2016-08-18').all()

    """Convert list of tuples into normal list & return json"""
    active_staion_temp = list(np.ravel(station_temp))
    return jsonify(active_staion_temp)

"""**********************************************************************"""

@app.route("/api/v1.0/temp/<start>")
def temp1(start): 
     """set start variable to parse specified date via datetime format"""
     start = dt.datetime.strptime(start,"%Y%m%d")
     
     with Session(bind=engine) as session:
        """Query min, max, avg temperature calculations for specified start date"""
        start_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    
     """Convert list of tuples into normal list & return json"""
     specified_temp = list(np.ravel(start_temp))
     return jsonify(specified_temp)

"""**********************************************************************"""

@app.route("/api/v1.0/temp/<start>/<end>")
def temp2(start=None, end=None):
     
     """set start and end variable to parse specified date via datetime format"""
     start = dt.datetime.strptime(start,"%Y%m%d")
     end = dt.datetime.strptime(end, "%Y%m%d")
     
     with Session(bind=engine) as session:
      """Query min, max, avg temperature calculations for start and end date"""
     start_end_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
     
     """Convert list of tuples into normal list & return json"""
     specified_temp2 = list(np.ravel(start_end_temp))
     return jsonify(specified_temp2)


if __name__ == '__main__':
    app.run(debug=True)

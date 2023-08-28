# Import the dependencies.

# 1. import Flask
from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement

station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Home Route lists all routes available
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
            f"Welcome to my 'Home' page!<br/>"
            f"<br/>"
            f"Here are all of the available routes:<br/>"
            f"<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>"
    )



# Precipitation route shows all precipitation data for the last year of the data's life
@app.route("/api/v1.0/precipitation")
def precipitaiton():
    print("Server received request for 'precipitation' page...")

    # Starting from the most recent data point in the database. 
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    year_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= query_date).all()

    # Close Session
    session.close()

    # Place all data into a dictionary
    all_data = []
    for date, prcp in year_data:
        data_dict = {}
        data_dict["date"] = date
        data_dict["prcp"] = prcp
        all_data.append(data_dict)

    # Jsonify the dictionary
    return jsonify(all_data)





@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")

    # Collect station data
    stations = session.query(station.name, station.id).all()
    
    # Close session
    session.close()


    # Place all data into a dictionary
    all_data = []
    for name, id in stations:
        data_dict = {}
        data_dict["station_name"] = name
        data_dict["station_id"] = id
        all_data.append(data_dict)

    # Jsonify the dictionary
    return jsonify(all_data)




@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")

    # Collect and aggregate the temperature obersvation data
    station_active_status = session.query(measurement.station, func.count(measurement.prcp)).group_by(measurement.station).order_by(func.count(measurement.prcp).desc()).first()
    
    # Find the most activ station
    most_active_station = station_active_status[0]

    # Get the starting date for the past year of data 
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Get the temperature data for the year's worth of entries for the most active station
    year_data_USC00519281 = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).filter(measurement.date >= query_date).all()

    # Close session
    session.close()

    # Place all data into a dictionary
    all_data = []
    for date, tobs in year_data_USC00519281:
        data_dict = {}
        data_dict["date"] = date
        data_dict["tobs"] = tobs
        all_data.append(data_dict)
 
    # Jsonify the dictionary
    return jsonify(all_data)




@app.route("/api/v1.0/<start>")
def start(start):
    print(f"Server received request for the date starting at {start} and ending at 2017-08-23...")

    # Take user-input as the start date
    query_start_date = start

    # Create static end date
    query_end_date = dt.date(2017, 8, 23)

    # Get the aggregates of the tempurature data
    all_temp = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= query_start_date).filter(measurement.date <= query_end_date).all()

    # Close session
    session.close()

    # Place all data into a dictionary
    all_data = []
    for min, avg, max in all_temp:
        data_dict = {}
        data_dict["tmin"] = min
        data_dict["tavg"] = avg
        data_dict["tmax"] = max

        all_data.append(data_dict)
 
    # Jsonify the dictionary
    return jsonify(all_data)




@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    print(f"Server received request for the date starting at {start} and ending at {end}...")

    # Take user-input as the start date
    query_start_date = start

    # Take user-input as the end date
    query_end_date = end

    all_temp = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= query_start_date).filter(measurement.date <= query_end_date).all()

    # Close session
    session.close()

    # Place all data into a dictionary
    all_data = []
    for min, avg, max in all_temp:
        data_dict = {}
        data_dict["tmin"] = min
        data_dict["tavg"] = avg
        data_dict["tmax"] = max

        all_data.append(data_dict)
 
    # Jsonify the dictionary
    return jsonify(all_data)


if __name__ == "__main__":
    app.run(debug=True)


# Import the dependencies.
from flask import Flask, jsonify

import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the climate app<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"

    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    print("Query Date: ", query_date)

    # Perform a query to retrieve the data and precipitation scores
    precip_data = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= query_date).all()
    

    all_precip = []
    for date, prcp in precip_data:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        
        all_precip.append(precip_dict)
    session.close()
    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    station_names = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_names))

    return jsonify(all_stations)

   


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    most_active_stations = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    most_active_station = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == most_active_stations[0].station).\
    filter(measurement.date >= query_date).all()

    
    all_tobs = []
    for date, prcp in most_active_station:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["temp"] = prcp
        
        all_tobs.append(precip_dict)
    session.close()
    return jsonify(all_tobs)

    all_tobs = list(np.ravel(most_active_station))

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%d-%m-%Y")


    most_active_stat = session.query(func.min(measurement.tobs),\
            func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start_date).all()

    session.close()
    all_start = list(np.ravel(most_active_stat))

    return jsonify(all_start)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%d-%m-%Y")
    end_date = dt.datetime.strptime(end, "%d-%m-%Y")


    most_active_stat = session.query(func.min(measurement.tobs),\
            func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()
    all_start_end = list(np.ravel(most_active_stat))

    return jsonify(all_start_end)


    
if __name__ == "__main__":
    app.run(debug=True)

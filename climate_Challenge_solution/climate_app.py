# 1. import dependencies
from flask import Flask, jsonify, request
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create an app, being sure to pass __name__
app = Flask(__name__)

#  List all the available routes.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (f"Welcome"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)

# Calculate the date one year from the last date in data set.
    precipitation_query = dt.date(2017, 8, 23) - dt.timedelta(days=366)
    print(precipitation_query)

# Perform a query to retrieve the data and precipitation scores
    prior_year_data_query = (session.query(Measurement.date, Measurement.prcp).
                             filter(Measurement.date >= precipitation_query).all())

# Close Session
    session.close()

    # Create a dictionary
    precipitation_data = []
    for date, prcp in prior_year_data_query:
        prior_year_dict = [f"{date}", f"{prcp} inches"]
        precipitation_data.append(prior_year_dict)

    return jsonify(dict(precipitation_data))


# create stations list

@app.route("/api/v1.0/stations")
def stations():

    # Create session from Python to the DB
    session = Session(engine)

    # Retrieve data for all stations
    stations = session.query(Station.name, Station.station).all()

    # Close Session
    session.close()
    # Convert list of tuples to ordinary list
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

# dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def temps():

    # Create session from Python to the DB
    session = Session(engine)
    # Dates and temperature observations of the most-active station for the previous year of data.
   
    precipitation_query = dt.date(2017, 8, 23) - dt.timedelta(days=366)
    most_active_prior_year = (session.query(Measurement.date, Measurement.tobs)
                              .filter(Measurement.date >= precipitation_query)
                              .filter(Measurement.station == 'USC00519281')
                              .all())
   
   # Close Session
    session.close()

    #Convert list of tuples into normal list
    most_active_prior_year_list = list(np.ravel(most_active_prior_year))
     #Return a JSON list
    return jsonify(most_active_prior_year_list)

#5 - Return the temperature summary for a specified start or start-end range.
#5a
@app.route("/api/v1.0/<start>")

def start(start):
    
    # Create session from Python to the DB
    session = Session(engine)

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close()

    # Create list
    tobsall = []
    # Create dictonary
    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)
    # Jasonify list    
    return jsonify(tobsall)


#5b
#minimum temperature, the average temperature, and 
# the maximum temperature for a specified start or start-end range
@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    
    session = Session(engine)

    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                func.max(Measurement.tobs)).filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)


    return jsonify(tobsall)



if __name__ == '__main__':
    app.run(debug=True)

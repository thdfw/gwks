from typing import Optional, Dict
from sqlalchemy import create_engine, Column, BigInteger, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os

from datetime import datetime
import pytz

# Get current time with zone
tz = pytz.timezone('America/New_York')
current_time = datetime.now()
current_time_with_tz = tz.localize(current_time)


def add_experiment(exp_dict):
    """
    Adds an experiment (provided as a dict) as a new row in the 'flow_sessions' table
    """

    # Get the dictionnary as a sqlalchemy object
    session_sqlalchemy = GWMessageSQLAlchemy(
        session_name = exp_dict['session_name'],
        zone_config = exp_dict['zone_config'],
        flow_rate_gpm = exp_dict['flow_rate_gpm'],
        start_time = exp_dict['start_time'],
        end_time = exp_dict['end_time'],
    )

    # Open session, add new row and commit changes
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(session_sqlalchemy)
    session.commit()
    session.close()


# Defining the sqlalchemy table format
Base = declarative_base()

class GWMessageSQLAlchemy(Base):
    __tablename__ = 'flow_sessions'
    session_name = Column(String)
    zone_config = Column(String)
    flow_rate_gpm = Column(Float)
    start_time = Column(DateTime(timezone=True), primary_key=True)
    end_time = Column(DateTime(timezone=True))

# Create the table in the desired database
engine = create_engine('postgresql://localhost/thomas')
Base.metadata.drop_all(engine) # remove existing table
Base.metadata.create_all(engine) # add new table

first_try = {
    'session_name': 'Session3',
    'zone_config': 'downstairs_zone',
    'flow_rate_gpm': 20.0,
    'start_time': current_time_with_tz,
    'end_time': current_time_with_tz,
}
add_experiment(first_try)

'''
# Add all experiments in the given directory to the table
print("\nAdded the following files as new rows in the messages table:")
json_files_dir = 'sample_messages'
for _, __, files in os.walk(json_files_dir):
    for file in files:
        if file.endswith(".json"):
            print(file)
            add_experiment(json_files_dir+'/'+file)
print("")
'''
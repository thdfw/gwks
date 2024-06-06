from pydantic import BaseModel
from pydantic import Extra
from pydantic import validator
from typing import Optional, Dict
from sqlalchemy import create_engine, Column, BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os

# Defining the pydantic class for messages
class GwMessagePydantic(BaseModel):
    from_alias: str
    type_name: str
    message_persisted_ms: int
    payload: Dict
    message_id: Optional[str] = None

    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True

    @validator("message_id")
    def _check_message_id(cls, v: str) -> str:
        if v!='':
            try:
                check_is_uuid_canonical_textual(v)
            except ValueError as e:
                raise ValueError(
                    f"MessageId failed UuidCanonicalTextual format validation: {e}"
                )
        return v


def check_is_uuid_canonical_textual(v: str) -> None:
    """Checks UuidCanonicalTextual format

    UuidCanonicalTextual format:  A string of hex words separated by hyphens
    of length 8-4-4-4-12.

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not UuidCanonicalTextual format
    """
    try:
        x = v.split("-")
    except AttributeError as e:
        raise ValueError(f"Failed to split on -: {e}")
    if len(x) != 5:
        raise ValueError(f"{v} split by '-' did not have 5 words")
    for hex_word in x:
        try:
            int(hex_word, 16)
        except ValueError:
            raise ValueError(f"Words of {v} are not all hex")
    if len(x[0]) != 8:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[1]) != 4:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[2]) != 4:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[3]) != 4:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[4]) != 12:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")


def add_message(path):
    """
    Adds a message file (provided through the path to a .json file)
    as a new row in the table in the messages database
    """

    # The first three attributes can be read from the file name
    from_alias, type_name, message_persisted_ms = path.split('/')[-1].split('-')[:-1]
    message_persisted_ms = int(message_persisted_ms)

    # The fourth and fifth can be read from the file content
    with open(path, 'r') as file:
        data = json.load(file)
        payload = data['Payload']
        message_id = data['Header']['MessageId']
        
    # Get the message as a pydantic object
    message_pydantic = GwMessagePydantic(
        from_alias = from_alias,
        type_name = type_name,
        message_persisted_ms = message_persisted_ms,
        payload = payload,
        message_id = message_id
    )

    # Get the pydantic object as a sqlalchemy object
    message_sqlalchemy = GWMessageSQLAlchemy(
        from_alias = message_pydantic.from_alias,
        type_name = message_pydantic.type_name,
        message_persisted_ms = message_pydantic.message_persisted_ms,
        payload = message_pydantic.payload,
        message_id = message_pydantic.message_id
    )

    # Open session, add new row and commit changes
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(message_sqlalchemy)
    session.commit()
    session.close()


# Defining the sqlalchemy table format
Base = declarative_base()

class GWMessageSQLAlchemy(Base):
    __tablename__ = 'messages'
    from_alias = Column(String)
    type_name = Column(String)
    message_persisted_ms = Column(BigInteger)
    payload = Column(JSONB)
    message_id = Column(String, primary_key=True)

# Create the table in the desired database
engine = create_engine('postgresql://localhost/gw_messages')
Base.metadata.drop_all(engine) # remove existing table
Base.metadata.create_all(engine) # add new table

# Add all json files in the given directory to the table
print("\nAdded the following json files as new rows in the messages table:")
json_files_dir = '/Users/thomasdefauw/Downloads'
for _, __, files in os.walk(json_files_dir):
    for file in files:
        if file.endswith(".json"):
            print(file)
            add_message(json_files_dir+'/'+file)
print("")
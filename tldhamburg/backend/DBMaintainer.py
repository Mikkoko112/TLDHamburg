import sqlite3, os
import pandas as pd
import logging


class DBMaintainer:
    allowed_columns = [
        "primary_signal",
        "secondary_signal",
        "auxiliary_signal",
        "acoustic_signal",
        "detector_car",
        "detector_cyclists",
        "detector_pedestrian",
        "detector_acoustic_traffic_request",
        "bus_pre_request_point",
        "bus_request_point",
        "bus_checkout",
        "signal_program",
        "cycle_second",
    ]

    tables = ["Things", "Datastreams"]

    logging.basicConfig(
        level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    def create_tables():
        create_things_table = """
        CREATE TABLE IF NOT EXISTS Things (
            thingID INTEGER PRIMARY KEY,
            connectionID INTEGER NOT NULL,
            trafficLightsID INTEGER NOT NULL
        );
        """

        create_datastreams_table = """
        CREATE TABLE IF NOT EXISTS Datastreams (
            thingID INTEGER PRIMARY KEY,
            primary_signal INTEGER DEFAULT 0,
            secondary_signal INTEGER DEFAULT 0,
            auxiliary_signal INTEGER DEFAULT 0,
            acoustic_signal INTEGER DEFAULT 0,
            detector_car INTEGER DEFAULT 0,
            detector_cyclists INTEGER DEFAULT 0,
            detector_pedestrian INTEGER DEFAULT 0,
            detector_acoustic_traffic_request INTEGER DEFAULT 0,
            bus_pre_request_point INTEGER DEFAULT 0,
            bus_request_point INTEGER DEFAULT 0,
            bus_checkout INTEGER DEFAULT 0,
            signal_program INTEGER DEFAULT 0,
            cycle_second INTEGER DEFAULT 0,
            FOREIGN KEY (thingID) REFERENCES Things(thingID) ON DELETE CASCADE
        );
        """

        with sqlite3.connect("TLDHamburg.db") as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(create_things_table)
            cursor.execute(create_datastreams_table)
            connection.commit()
            logging.info("Tables created or verified successfully.")

    def delete_thing(thingID):
        """
        Deletes a thing entity from the Things table based on the provided thing_id.

        Args:
            thing_id (int): The unique identifier of the thing to be deleted.
        """
        try:
            with sqlite3.connect("TLDHamburg.db") as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("DELETE FROM Things WHERE thing_id = ?;", (thingID,))
                connection.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted thing with ID {thingID}.")
                else:
                    logging.info(f"No Thing found with ID {thingID}.")
        except sqlite3.Error as error:
            logging.info(f"An error occurred: {error}")

    def insert_things(things_data):
        insert_query = """
        INSERT INTO Things (thingID, connectionID, trafficLightsID)
        VALUES (?, ?, ?);
        """
        try:
            with sqlite3.connect("TLDHamburg.db") as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.executemany(insert_query, things_data)
                connection.commit()
                print(f"Inserted {cursor.rowcount} record(s) into Things.")
        except sqlite3.IntegrityError as error:
            logging.error(f"Integrity Error: {error}")
        except sqlite3.Error as error:
            logging.error(f"Database Error: {error}")

    def insert_datastreams(datastreams):
        """
        Inserts multiple datastream records into the Datastreams table.

        Args:
            datastreams (list of dict): Each dictionary should contain 'thingID' and any optional datastream attributes.

        Example:
        datastreams = [
            {'thingID': 4, 'primary_signal': 12, 'detector_pedestrian': 1},
            {'thingID': 5, 'secondary_signal': 7},
            {'thingID': 6}  # Uses default values for all optional columns
        ]
        """

        try:
            with sqlite3.connect("TLDHamburg.db") as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                for datastream in datastreams:
                    thingID = datastream.get("thingID")
                    if thingID is None:
                        print("Skipping entry without 'thingID'.")
                        continue
                    columns = ["thingID"]
                    values = [thingID]
                    for key, value in datastream.items():
                        if key in DBMaintainer.allowed_columns:
                            columns.append(key)
                            values.append(value)
                        elif key != "thingID":
                            print(f"Ignoring invalid column: {key}")
                    columns_str = ", ".join(columns)
                    placeholders = ", ".join(["?"] * len(columns))
                    insert_query = f"INSERT INTO Datastreams ({columns_str}) VALUES ({placeholders});"
                    cursor.execute(insert_query, values)
                connection.commit()
                print(f"Inserted datastream id(s) of {len(datastreams)} Thing(s).")
        except sqlite3.IntegrityError as error:
            print(f"Integrity Error: {error}")
        except sqlite3.Error as error:
            print(f"Database Error: {error}")

    def print_table(table="Things"):
        """
        Prints all records from the specified table in the TLDHamburg database.

        Args:
            table (str, optional): The name of the table to retrieve data from.
                Defaults to "Things".
        """
        if table not in DBMaintainer.tables:
            raise ValueError(f"Table '{table}' was not found in the database.")

        db_path = DBMaintainer.get_db_path()
        try:
            with sqlite3.connect(db_path) as connection:
                df = pd.read_sql_query(f"SELECT * FROM {table};", connection)
                print(df)
        except sqlite3.DatabaseError as error:
            logging.error(f"Database Error: {error}")

    def get_db_path():
        """
        Constructs and returns the absolute path to the TLDHamburg.db database file. It is assumed
        that the database is in the same directory as the class DBMaintainer.

        Returns:
            str: The absolute path to the TLDHamburg.db database file.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "TLDHamburg.db")
        return db_path

    def read_datastreams_db(ids: list, attribute: str):
        """
        Reads a specific attribute from the Datastreams table for given thingIDs.

        Args:
            ids (list of int): List of thingID values to filter the records.
            attribute (str): The specific column/attribute to retrieve.

        Returns:
            list: A list of values corresponding to the specified attribute for each thingID.
                If a thingID does not have the attribute set, None is returned for that entry.
        """

        if attribute not in DBMaintainer.allowed_columns:
            logging.error(
                f"Invalid attribute: '{attribute}'. Allowed attributes are: {DBMaintainer.allowed_columns}"
            )
            return {}

        if not ids:
            logging.error(
                "The 'ids' list is empty. Please provide at least one thingID."
            )
            return {}

        placeholders = ", ".join(["?"] * len(ids))
        query = f"SELECT thingID, {attribute} FROM Datastreams WHERE thingID IN ({placeholders});"

        try:
            with sqlite3.connect(DBMaintainer.get_db_path()) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute(query, ids)
                rows = cursor.fetchall()
                # Mapping thingId to the corresponding Datastream ID.
                id_to_value = {row[0]: row[1] for row in rows}
                logging.info(
                    f"Retrieved attribute '{attribute}' for {len(ids)} Thing(s)."
                )
                return id_to_value
        except sqlite3.Error as error:
            logging.error(f"Database Error: {error}")

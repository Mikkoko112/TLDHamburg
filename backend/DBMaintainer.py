import sqlite3
import pandas as pd


class DBMaintainer:
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
            print("Tables created or verified successfully.")

    def delete_thing(thingID):
        """
        Deletes a thing entity from the Things table based on the provided thing_id.

        Parameters:
        - thing_id (int): The unique identifier of the thing to be deleted.
        """
        try:
            with sqlite3.connect("TLDHamburg.db") as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("DELETE FROM Things WHERE thing_id = ?;", (thingID,))
                connection.commit()
                if cursor.rowcount > 0:
                    print(f"Deleted thing with ID {thingID}.")
                else:
                    print(f"No Thing found with ID {thingID}.")
        except sqlite3.Error as error:
            print(f"An error occurred: {error}")

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
            print(f"Integrity Error: {error}")
        except sqlite3.Error as error:
            print(f"Database Error: {error}")

    def insert_datastreams(datastreams):
        """
        Inserts multiple datastream records into the Datastreams table.

        Parameters:
        - datastreams (list of dict): Each dictionary should contain 'thingID' and any optional datastream attributes.

        Example:
        datastreams = [
            {'thingID': 4, 'primary_signal': 12, 'detector_pedestrian': 1},
            {'thingID': 5, 'secondary_signal': 7},
            {'thingID': 6}  # Uses default values for all optional columns
        ]
        """
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
                        if key in allowed_columns:
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
        connection = sqlite3.connect("TLDHamburg.db")
        df = pd.read_sql_query(f"SELECT * FROM {table};", connection)
        print(df)
        connection.close()

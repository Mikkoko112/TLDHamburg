import sqlite3
import pandas as pd


class DBMaintainer:
    def create_tables():
        create_things_table = """
        CREATE TABLE IF NOT EXISTS Things (
            thing_id INTEGER PRIMARY KEY,
            connectionID INTEGER NOT NULL,
            trafficLightsID INTEGER NOT NULL
        );
        """

        create_datastreams_table = """
        CREATE TABLE IF NOT EXISTS Datastreams (
            thing_id INTEGER PRIMARY KEY,
            primary_signal INTEGER DEFAULT 0,
            secondary_signal INTEGER DEFAULT 0,
            auxiliary_signal INTEGER DEFAULT 0,
            acoustic_signal INTEGER DEFAULT 0,
            car_request INTEGER DEFAULT 0,
            cyclist_request INTEGER DEFAULT 0,
            pedestrian_request INTEGER DEFAULT 0,
            FOREIGN KEY (thing_id) REFERENCES Things(thing_id) ON DELETE CASCADE
        );
        """

        with sqlite3.connect("TLDHamburg.db") as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(create_things_table)
            cursor.execute(create_datastreams_table)
            connection.commit()
            print("Tables created or verified successfully.")

    def insert_things(things_data):
        insert_query = """
        INSERT INTO Things (thing_id, connectionID, trafficLightsID)
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

    def print_things_table():
        connection = sqlite3.connect("TLDHamburg.db")
        df = pd.read_sql_query("SELECT * FROM Things;", connection)
        print(df)
        connection.close()

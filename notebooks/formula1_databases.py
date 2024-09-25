from typing import Any, cast
import sqlite3
import pandas as pd
from datetime import datetime
from fastf1.core import Session
import fastf1


class FastF1ToSQL:
    def __init__(self, db_path: str) -> None:
        """
        Initialize the FastF1ToSQL class.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        """Create all necessary tables and indexes if they don't exist."""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS Drivers (
                driver_id INTEGER PRIMARY KEY,
                driver_name TEXT NOT NULL,
                team TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Tracks (
                track_id INTEGER PRIMARY KEY,
                track_name TEXT NOT NULL,
                country TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Event (
                event_id INTEGER PRIMARY KEY,
                round_number INTEGER,
                country TEXT,
                location TEXT,
                event_date DATE,
                event_name TEXT,
                session_1_date_utc DATETIME,
                session_1_name TEXT CHECK(session_1_name IN ('practice', 'qualify', 'race')),
                session_2_date_utc DATETIME,
                session_2_name TEXT CHECK(session_2_name IN ('practice', 'qualify', 'race')),
                session_3_date_utc DATETIME,
                session_3_name TEXT CHECK(session_3_name IN ('practice', 'qualify', 'race')),
                session_4_date_utc DATETIME,
                session_4_name TEXT CHECK(session_4_name IN ('practice', 'qualify', 'race')),
                session_5_date_utc DATETIME,
                session_5_name TEXT CHECK(session_5_name IN ('practice', 'qualify', 'race'))
            );

            CREATE TABLE IF NOT EXISTS Sessions (
                session_id INTEGER PRIMARY KEY,
                event_id INTEGER,
                track_id INTEGER,
                session_type TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES Event(event_id),
                FOREIGN KEY (track_id) REFERENCES Tracks(track_id)
            );

            CREATE TABLE IF NOT EXISTS Weather (
                weather_id INTEGER PRIMARY KEY,
                session_id INTEGER,
                datetime DATETIME,
                air_temperature_in_celsius REAL,
                relative_air_humidity_in_percentage REAL,
                air_pressure_in_mbar REAL,
                is_raining BOOLEAN,
                track_temperature_in_celsius REAL,
                wind_direction_in_grads REAL,
                wind_speed_in_meters_per_seconds REAL,
                FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
            );

            CREATE TABLE IF NOT EXISTS Laps (
                lap_id INTEGER PRIMARY KEY,
                session_id INTEGER,
                driver_name TEXT NOT NULL,
                lap_number INTEGER NOT NULL,
                stint INTEGER,
                sector_1_speed_trap_in_km REAL,
                sector_2_speed_trap_in_km REAL,
                finish_line_speed_trap_in_km REAL,
                longest_strait_speed_trap_in_km REAL,
                is_personal_best BOOLEAN,
                tyre_compound TEXT,
                tyre_life_in_laps INTEGER,
                is_fresh_tyre BOOLEAN,
                position INTEGER,
                lap_time_in_seconds REAL,
                sector_1_time_in_seconds REAL,
                sector_2_time_in_seconds REAL,
                sector_3_time_in_seconds REAL,
                lap_start_time_in_datetime DATETIME,
                pin_in_time_in_datetime DATETIME,
                pin_out_time_in_datetime DATETIME,
                FOREIGN KEY (session_id) REFERENCES Sessions(session_id),
                UNIQUE (session_id, driver_name, lap_number)
            );

            CREATE TABLE IF NOT EXISTS Telemetry (
                telemetry_id INTEGER PRIMARY KEY,
                lap_id INTEGER,
                speed_in_km REAL,
                RPM INTEGER,
                gear_number INTEGER,
                throttle_input REAL CHECK (throttle_input BETWEEN 0 AND 100),
                is_brake_pressed BOOLEAN,
                is_DRS_open BOOLEAN,
                x_position REAL,
                y_position REAL,
                z_position REAL,
                is_off_track BOOLEAN,
                datetime DATETIME,
                FOREIGN KEY (lap_id) REFERENCES Laps(lap_id)
            );

            CREATE INDEX IF NOT EXISTS idx_laps_driver_name ON Laps(driver_name);
            CREATE INDEX IF NOT EXISTS idx_laps_session_id ON Laps(session_id);
            CREATE INDEX IF NOT EXISTS idx_telemetry_lap_id ON Telemetry(lap_id);
            CREATE INDEX IF NOT EXISTS idx_telemetry_datetime ON Telemetry(datetime);
            CREATE INDEX IF NOT EXISTS idx_weather_session_id ON Weather(session_id);
            CREATE INDEX IF NOT EXISTS idx_weather_datetime ON Weather(datetime);
            CREATE INDEX IF NOT EXISTS idx_event_date ON Event(event_date);
        ''')
        self.conn.commit()

    def process_session(self, session: Session) -> None:
        """
        Process a session and insert the data into the database.

        Args:
            session (Session): The session to process.
        """
        # Load session data
        session.load()

        # Insert data into tables
        self.insert_event(session)
        self.insert_session(session)
        self.insert_drivers(session)
        self.insert_laps(session)
        self.insert_telemetry(session)
        self.insert_weather(session)

        # Commit changes and close connection
        self.conn.commit()
        self.conn.close()

    def insert_event(self, session: Session) -> None:
        """
        Insert the event data into the database.

        Args:
            session (Session): The FastF1 session object.
        """
        event_data: dict[str, Any] = {
            'round_number': session.event.RoundNumber,
            'country': session.event.Country,
            'location': session.event.Location,
            'event_date': session.event.EventDate.date(),
            'event_name': session.event.EventName,
            'session_1_date_utc': session.event.Session1DateUtc,
            'session_1_name': session.event.Session1.lower(),
            'session_2_date_utc': session.event.Session2DateUtc,
            'session_2_name': session.event.Session2.lower(),
            'session_3_date_utc': session.event.Session3DateUtc,
            'session_3_name': session.event.Session3.lower(),
            'session_4_date_utc': session.event.Session4DateUtc,
            'session_4_name': session.event.Session4.lower(),
            'session_5_date_utc': session.event.Session5DateUtc,
            'session_5_name': session.event.Session5.lower(),
        }

        columns = ', '.join(event_data.keys())
        placeholders = ', '.join(['?' for _ in event_data])
        query = f"INSERT OR REPLACE INTO Event ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, list(event_data.values()))

    def insert_session(self, session: Session) -> None:
        """
        Insert the session data into the database.

        Args:
            session (Session): The FastF1 session object.
        """
        session_data: dict[str, Any] = {
            # Assuming this is called right after insert_event
            'event_id': self.cursor.lastrowid,
            'track_id': self.get_or_create_track(session.event.Location, session.event.Country),
            'session_type': session.name,
            'date': session.date,
        }
        columns = ', '.join(session_data.keys())
        placeholders = ':' + ', :'.join(session_data.keys())
        query = f"INSERT INTO Sessions ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, session_data)

    def insert_drivers(self, session: Session) -> None:
        """
        Insert the drivers data into the database.

        Args:
            session (Session): The FastF1 session object.
        """
        for driver in session.drivers:
            driver_info = session.get_driver(driver)
            driver_data = {
                'driver_name': driver_info['FullName'],
                'team': driver_info['TeamName']
            }
            columns = ', '.join(driver_data.keys())
            placeholders = ':' + ', :'.join(driver_data.keys())
            query = f"INSERT OR IGNORE INTO Drivers ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, driver_data)

    def insert_laps(self, session: Session) -> None:
        """
        Insert the laps data into the database.

        Args:
            session (Session): The FastF1 session object.
        """
        laps_df = session.laps.copy()
        # Assuming this is called right after insert_session
        laps_df['session_id'] = self.cursor.lastrowid
        laps_df['lap_start_time_in_datetime'] = pd.to_datetime(
            laps_df['LapStartDate'])
        laps_df['pin_in_time_in_datetime'] = pd.to_datetime(
            laps_df['PitInTime'], unit='ns')
        laps_df['pin_out_time_in_datetime'] = pd.to_datetime(
            laps_df['PitOutTime'], unit='ns')

        for _, lap in laps_df.iterrows():
            lap_data: dict[str, Any] = {
                'session_id': lap['session_id'],
                'driver_name': lap['Driver'],
                'lap_number': lap['LapNumber'],
                'sector_1_time_in_seconds': lap['Sector1Time'].total_seconds() if pd.notnull(lap['Sector1Time']) else None,
                'sector_2_time_in_seconds': lap['Sector2Time'].total_seconds() if pd.notnull(lap['Sector2Time']) else None,
                'sector_3_time_in_seconds': lap['Sector3Time'].total_seconds() if pd.notnull(lap['Sector3Time']) else None,
                'lap_time_in_seconds': lap['LapTime'].total_seconds() if pd.notnull(lap['LapTime']) else None,
                'finish_line_speed_trap_in_km': lap['SpeedFL'],
                'longest_strait_speed_trap_in_km': lap['SpeedST'],
                'is_personal_best': lap['IsPersonalBest'],
                'tyre_compound': lap['Compound'],
                'tyre_life_in_laps': lap['TyreLife'],
                'is_fresh_tyre': lap['FreshTyre'],
                'position': lap['Position'],
                'lap_start_time_in_datetime': lap['lap_start_time_in_datetime'],
                'pin_in_time_in_datetime': lap['pin_in_time_in_datetime'],
                'pin_out_time_in_datetime': lap['pin_out_time_in_datetime'],
            }
            columns = ', '.join(lap_data.keys())
            placeholders = ':' + ', :'.join(lap_data.keys())
            query = f"INSERT INTO Laps ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, lap_data)

    def insert_telemetry(self, session: Session) -> None:
        """
        Insert the telemetry data into the database.

        Args:
            session (Session): The FastF1 session object.
        """
        for driver in session.drivers:
            car_data = session.car_data[driver].copy()
            pos_data = session.pos_data[driver].copy()

            telemetry = car_data.merge(
                pos_data, left_index=True, right_index=True, suffixes=('', '_pos'))
            telemetry['lap_id'] = self.get_lap_id(
                session, driver, telemetry.index)

            for _, sample in telemetry.iterrows():
                telemetry_data: dict[str, Any] = {
                    'lap_id': sample['lap_id'],
                    'speed_in_km': sample['Speed'],
                    'RPM': sample['RPM'],
                    'gear_number': sample['nGear'],
                    'throttle_input': sample['Throttle'],
                    'is_brake_pressed': sample['Brake'],
                    'is_DRS_open': sample['DRS'],
                    'x_position': sample['X'],
                    'y_position': sample['Y'],
                    'z_position': sample['Z'],
                    'is_off_track': sample['Status'] == 'OffTrack',
                    'datetime': sample.name,
                }
                columns = ', '.join(telemetry_data.keys())
                placeholders = ':' + ', :'.join(telemetry_data.keys())
                query = f"INSERT INTO Telemetry ({columns}) VALUES ({placeholders})"
                self.cursor.execute(query, telemetry_data)

    def insert_weather(self, session: Session) -> None:
        """
        Insert weather data into the Weather table.

        Args:
            session (Session): The FastF1 session containing weather data.
        """
        weather_data = cast(pd.DataFrame, session.weather_data)
        # Assuming this is called right after insert_session
        weather_data['session_id'] = self.cursor.lastrowid

        for _, sample in weather_data.iterrows():
            weather_sample: dict[str, Any] = {
                'session_id': sample['session_id'],
                'air_temperature_in_celsius': sample['AirTemp'],
                'track_temperature_in_celsius': sample['TrackTemp'],
                'wind_speed_in_meters_per_seconds': sample['WindSpeed'],
                'wind_direction_in_grads': sample['WindDirection'],
                'relative_air_humidity_in_percentage': sample['Humidity'],
                'air_pressure_in_mbar': sample['Pressure'],
                'is_raining': sample['Rainfall'],
                'datetime': sample.name,
            }
            columns = ', '.join(weather_sample.keys())
            placeholders = ':' + ', :'.join(weather_sample.keys())
            query = f"INSERT INTO Weather ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, weather_sample)

    def get_or_create_track(self, track_name: str, country: str) -> int:
        """
        Get the track_id for a given track, or create a new track if it doesn't exist.

        Args:
            track_name (str): The name of the track.
            country (str): The country where the track is located.

        Returns:
            int: The track_id of the existing or newly created track.
        """
        self.cursor.execute(
            "SELECT track_id FROM Tracks WHERE track_name = ? AND country = ?", (track_name, country))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            self.cursor.execute(
                "INSERT INTO Tracks (track_name, country) VALUES (?, ?)", (track_name, country))
            return self.cursor.lastrowid or 0

    def get_lap_id(self, session: Session, driver: str, time: datetime) -> int:
        """
        Get the lap_id for a given driver and time.

        Args:
            session (fastf1.core.Session): The FastF1 session.
            driver (str): The driver's name or abbreviation.
            time (pd.Timestamp): The timestamp to find the corresponding lap.

        Returns:
            int: The lap_id of the found lap.
        """
        laps = session.laps.pick_driver(driver)
        lap = laps.loc[laps['LapStartTime'] <= time].iloc[-1]

        if self.cursor.lastrowid is None:
            raise ValueError("No ID was generated")

        self.cursor.execute("SELECT lap_id FROM Laps WHERE session_id = ? AND driver_name = ? AND lap_number = ?",
                            (self.cursor.lastrowid, driver, lap['LapNumber']))
        return self.cursor.fetchone()[0]


# Usage example:
session = fastf1.get_session(2023, 'Bahrain', 'Q')
converter = FastF1ToSQL('f1_data.db')
converter.process_session(session)

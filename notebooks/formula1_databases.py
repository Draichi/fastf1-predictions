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
        self.conn = sqlite3.connect(db_path, timeout=20)
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
                session_1_name TEXT,
                session_2_date_utc DATETIME,
                session_2_name TEXT,
                session_3_date_utc DATETIME,
                session_3_name TEXT,
                session_4_date_utc DATETIME,
                session_4_name TEXT,
                session_5_date_utc DATETIME,
                session_5_name TEXT
            );

            CREATE TABLE IF NOT EXISTS Sessions (
                session_id INTEGER PRIMARY KEY,
                event_id INTEGER,
                track_id INTEGER,
                session_type TEXT NOT NULL,
                date DATETIME NOT NULL,
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
                throttle_input REAL,
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

        # Save session start date
        self._session_start_date = session.t0_date

        # Insert data into tables
        self.insert_event(session)
        self.insert_session(session)
        self.insert_drivers(session)
        self.insert_laps(session)
        self.insert_telemetry(session)
        self.insert_weather(session)

        # Create data analysis views
        self.create_data_analysis_views()

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
            'round_number': int(session.event.RoundNumber),
            'country': session.event.Country,
            'location': session.event.Location,
            'event_date': str(session.event.EventDate.date()),
            'event_name': session.event.EventName,
            'session_1_date_utc': str(session.event.Session1DateUtc),
            'session_1_name': session.event.Session1.lower(),
            'session_2_date_utc': str(session.event.Session2DateUtc),
            'session_2_name': session.event.Session2.lower(),
            'session_3_date_utc': str(session.event.Session3DateUtc),
            'session_3_name': session.event.Session3.lower(),
            'session_4_date_utc': str(session.event.Session4DateUtc),
            'session_4_name': session.event.Session4.lower(),
            'session_5_date_utc': str(session.event.Session5DateUtc),
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
            'date': str(session.date),
        }
        columns = ', '.join(session_data.keys())
        placeholders = ':' + ', :'.join(session_data.keys())
        query = f"INSERT INTO Sessions ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, session_data)
        self._session_id = self.cursor.lastrowid

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
        laps_df['session_id'] = self._session_id
        laps_df['lap_start_time_in_datetime'] = pd.to_datetime(
            laps_df['LapStartDate'])
        laps_df['pin_in_time_in_datetime'] = self._session_start_date + \
            laps_df['PitInTime']
        laps_df['pin_out_time_in_datetime'] = self._session_start_date + \
            laps_df['PitOutTime']

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
                'lap_start_time_in_datetime': str(lap['lap_start_time_in_datetime']),
                'pin_in_time_in_datetime': str(lap['pin_in_time_in_datetime']),
                'pin_out_time_in_datetime': str(lap['pin_out_time_in_datetime']),
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
        print('> Inserting telemetry data...')
        telemetry_data_list = []

        for driver in session.drivers:
            laps_per_driver = session.laps.pick_driver(driver)

            for _, lap in laps_per_driver.iterrows():
                lap_number = lap['LapNumber']
                telemetry = lap.get_telemetry()
                telemetry['datetime'] = self._session_start_date + \
                    telemetry['Time']

                for _, sample in telemetry.iterrows():
                    telemetry_data: dict[str, Any] = {
                        'lap_id': lap_number,
                        'speed_in_km': sample['Speed'],
                        'RPM': sample['RPM'],
                        'gear_number': sample['nGear'],
                        'throttle_input': sample['Throttle'],
                        'is_brake_pressed': sample['Brake'],
                        'is_DRS_open': sample['DRS'],
                        'x_position': round(sample['X'], 2),
                        'y_position': round(sample['Y'], 2),
                        'z_position': round(sample['Z'], 2),
                        'is_off_track': sample['Status'] == 'OffTrack',
                        'datetime': str(sample['datetime']),
                    }
                    telemetry_data_list.append(telemetry_data)

        if telemetry_data_list:
            columns = ', '.join(telemetry_data_list[0].keys())
            placeholders = ':' + ', :'.join(telemetry_data_list[0].keys())
            query = f"INSERT INTO Telemetry ({columns}) VALUES ({placeholders})"
            self.cursor.executemany(query, telemetry_data_list)

    def insert_weather(self, session: Session) -> None:
        """
        Insert weather data into the Weather table.

        Args:
            session (Session): The FastF1 session containing weather data.
        """
        weather_data = cast(pd.DataFrame, session.weather_data)
        weather_data['session_id'] = self._session_id

        weather_data['datetime'] = self._session_start_date + \
            weather_data['Time']

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
                'datetime': str(sample['datetime']),
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

        if self._session_id is None:
            raise ValueError("No ID was generated")

        self.cursor.execute("SELECT lap_id FROM Laps WHERE session_id = ? AND driver_name = ? AND lap_number = ?",
                            (self._session_id, driver, lap['LapNumber']))
        return self.cursor.fetchone()[0]

    def create_data_analysis_views(self) -> None:
        """Create data analysis views in the database."""
        print('> Creating data analysis views...')
        self.cursor.executescript('''
            -- 1. Driver Performance Summary with Weather
            CREATE VIEW IF NOT EXISTS DriverPerformanceSummaryWithWeather AS
            SELECT 
                l.driver_name,
                e.event_name,
                s.session_type,
                t.track_name,
                COUNT(l.lap_id) AS total_laps,
                AVG(l.lap_time_in_seconds) AS avg_lap_time,
                MIN(l.lap_time_in_seconds) AS best_lap_time,
                AVG(l.sector_1_time_in_seconds) AS avg_sector1_time,
                AVG(l.sector_2_time_in_seconds) AS avg_sector2_time,
                AVG(l.sector_3_time_in_seconds) AS avg_sector3_time,
                AVG(l.finish_line_speed_trap_in_km) AS avg_finish_line_speed,
                COUNT(CASE WHEN l.is_personal_best THEN 1 END) AS personal_best_laps,
                AVG(w.air_temperature_in_celsius) AS avg_air_temp,
                AVG(w.track_temperature_in_celsius) AS avg_track_temp,
                SUM(CASE WHEN w.is_raining THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS rain_percentage
            FROM Laps l
            JOIN Sessions s ON l.session_id = s.session_id
            JOIN Tracks t ON s.track_id = t.track_id
            JOIN Event e ON s.event_id = e.event_id
            LEFT JOIN Weather w ON s.session_id = w.session_id 
                AND l.lap_start_time_in_datetime BETWEEN w.datetime AND datetime(w.datetime, '+1 minutes')
            GROUP BY l.driver_name, e.event_id, s.session_id;

            -- 2. Tyre Performance Analysis with Weather
            CREATE VIEW IF NOT EXISTS TyrePerformanceAnalysisWithWeather AS
            SELECT 
                l.driver_name,
                e.event_name,
                s.session_type,
                t.track_name,
                l.tyre_compound,
                AVG(l.tyre_life_in_laps) AS avg_tyre_life,
                AVG(l.lap_time_in_seconds) AS avg_lap_time,
                AVG(l.longest_strait_speed_trap_in_km) AS avg_top_speed,
                COUNT(CASE WHEN l.is_fresh_tyre THEN 1 END) AS fresh_tyre_laps,
                COUNT(CASE WHEN NOT l.is_fresh_tyre THEN 1 END) AS used_tyre_laps,
                AVG(w.track_temperature_in_celsius) AS avg_track_temp,
                AVG(w.air_temperature_in_celsius) AS avg_air_temp
            FROM Laps l
            JOIN Sessions s ON l.session_id = s.session_id
            JOIN Tracks t ON s.track_id = t.track_id
            JOIN Event e ON s.event_id = e.event_id
            LEFT JOIN Weather w ON s.session_id = w.session_id 
                AND l.lap_start_time_in_datetime BETWEEN w.datetime AND datetime(w.datetime, '+1 minutes')
            GROUP BY l.driver_name, e.event_id, s.session_id, l.tyre_compound;

            -- 3. Weather Impact Analysis
            CREATE VIEW IF NOT EXISTS WeatherImpactAnalysis AS
            SELECT 
                e.event_name,
                s.session_type,
                t.track_name,
                AVG(w.air_temperature_in_celsius) AS avg_air_temp,
                AVG(w.track_temperature_in_celsius) AS avg_track_temp,
                AVG(w.relative_air_humidity_in_percentage) AS avg_humidity,
                AVG(w.wind_speed_in_meters_per_seconds) AS avg_wind_speed,
                SUM(CASE WHEN w.is_raining THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS rain_percentage,
                AVG(l.lap_time_in_seconds) AS avg_lap_time,
                MIN(l.lap_time_in_seconds) AS best_lap_time
            FROM Weather w
            JOIN Sessions s ON w.session_id = s.session_id
            JOIN Tracks t ON s.track_id = t.track_id
            JOIN Event e ON s.event_id = e.event_id
            JOIN Laps l ON s.session_id = l.session_id
                AND l.lap_start_time_in_datetime BETWEEN w.datetime AND datetime(w.datetime, '+1 minutes')
            GROUP BY e.event_id, s.session_id;

            -- 4. Event Performance Overview
            CREATE VIEW IF NOT EXISTS EventPerformanceOverview AS
            SELECT 
                e.event_name,
                e.country,
                e.location,
                s.session_type,
                COUNT(DISTINCT l.driver_name) AS driver_count,
                AVG(l.lap_time_in_seconds) AS avg_lap_time,
                MIN(l.lap_time_in_seconds) AS best_lap_time,
                MAX(l.finish_line_speed_trap_in_km) AS max_finish_line_speed,
                AVG(w.air_temperature_in_celsius) AS avg_air_temp,
                AVG(w.track_temperature_in_celsius) AS avg_track_temp,
                SUM(CASE WHEN w.is_raining THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS rain_percentage
            FROM Event e
            JOIN Sessions s ON e.event_id = s.event_id
            JOIN Laps l ON s.session_id = l.session_id
            LEFT JOIN Weather w ON s.session_id = w.session_id 
                AND l.lap_start_time_in_datetime BETWEEN w.datetime AND datetime(w.datetime, '+1 minutes')
            GROUP BY e.event_id, s.session_id;

            -- 5. Telemetry Analysis with Weather
            CREATE VIEW IF NOT EXISTS TelemetryAnalysisWithWeather AS
            SELECT 
                l.lap_id,
                l.driver_name,
                e.event_name,
                s.session_type,
                t.track_name,
                l.lap_number,
                l.lap_time_in_seconds,
                AVG(tel.speed_in_km) AS avg_speed,
                MAX(tel.speed_in_km) AS max_speed,
                AVG(tel.RPM) AS avg_RPM,
                MAX(tel.RPM) AS max_RPM,
                AVG(tel.throttle_input) AS avg_throttle,
                SUM(CASE WHEN tel.is_brake_pressed THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS brake_percentage,
                SUM(CASE WHEN tel.is_DRS_open THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS drs_usage_percentage,
                SUM(CASE WHEN tel.is_off_track THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS off_track_percentage,
                AVG(w.air_temperature_in_celsius) AS avg_air_temp,
                AVG(w.track_temperature_in_celsius) AS avg_track_temp,
                AVG(w.wind_speed_in_meters_per_seconds) AS avg_wind_speed
            FROM Laps l
            JOIN Sessions s ON l.session_id = s.session_id
            JOIN Tracks t ON s.track_id = t.track_id
            JOIN Event e ON s.event_id = e.event_id
            JOIN Telemetry tel ON l.lap_id = tel.lap_id
            LEFT JOIN Weather w ON s.session_id = w.session_id 
                AND tel.datetime BETWEEN w.datetime AND datetime(w.datetime, '+1 minutes')
            GROUP BY l.lap_id;
        ''')
        self.conn.commit()


# Usage example:
session = fastf1.get_session(2023, 'Bahrain', 'Q')
converter = FastF1ToSQL('Bahrain_2023_Q.db')
converter.process_session(session)

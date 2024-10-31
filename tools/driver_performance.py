from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from db.connection import db


class GetDriverPerformanceOutput(BaseModel):
    """Output for the get_driver_performance tool"""
    driver_name: str = Field(description="Name of the driver")
    event_name: str = Field(description="Name of the event")
    session_type: str = Field(
        description="Type of session (Practice, Qualifying, Race)")
    track_name: str = Field(description="Name of the track")
    total_laps: int = Field(description="Total number of laps completed")
    avg_lap_time: float | None = Field(
        description="Average lap time in seconds")
    best_lap_time: float | None = Field(description="Best lap time in seconds")
    avg_sector1_time: float | None = Field(
        description="Average sector 1 time in seconds")
    avg_sector2_time: float | None = Field(
        description="Average sector 2 time in seconds")
    avg_sector3_time: float | None = Field(
        description="Average sector 3 time in seconds")
    avg_finish_line_speed: float | None = Field(
        description="Average finish line speed in km/h")
    personal_best_laps: int = Field(description="Number of personal best laps")
    avg_air_temp: float | None = Field(
        description="Average air temperature in celsius")
    avg_track_temp: float | None = Field(
        description="Average track temperature in celsius")
    rain_percentage: float = Field(
        description="Percentage of time it rained during the session")


class GetDriverPerformance(BaseTool):
    name: str = "get_driver_performance"
    description: str = "useful for when you need to analyze driver performance statistics across different sessions and events"

    def _run(self) -> list[GetDriverPerformanceOutput]:
        """Use the tool."""
        sql_file = open("tools/sql/driver_performance.query.sql", "r")
        sql_query = sql_file.read()
        sql_file.close()

        response = db.run(sql_query)

        if not isinstance(response, str):
            response = str(response)

        # Remove the outer brackets and split by rows
        rows = response.strip('[]').split('), (')

        results = []
        for row in rows:
            # Clean up the row string and split by columns
            clean_row = row.strip('()').split(',')

            # Convert to appropriate types and create output object
            driver_data = GetDriverPerformanceOutput(
                driver_name=clean_row[0].strip("'"),
                event_name=clean_row[1].strip("'"),
                session_type=clean_row[2].strip("'"),
                track_name=clean_row[3].strip("'"),
                total_laps=int(float(clean_row[4])),
                avg_lap_time=float(
                    clean_row[5]) if clean_row[5].strip() != 'None' else None,
                best_lap_time=float(
                    clean_row[6]) if clean_row[6].strip() != 'None' else None,
                avg_sector1_time=float(
                    clean_row[7]) if clean_row[7].strip() != 'None' else None,
                avg_sector2_time=float(
                    clean_row[8]) if clean_row[8].strip() != 'None' else None,
                avg_sector3_time=float(
                    clean_row[9]) if clean_row[9].strip() != 'None' else None,
                avg_finish_line_speed=float(
                    clean_row[10]) if clean_row[10].strip() != 'None' else None,
                personal_best_laps=int(
                    float(clean_row[11])) if clean_row[11].strip() != 'None' else 0,
                avg_air_temp=float(
                    clean_row[12]) if clean_row[12].strip() != 'None' else None,
                avg_track_temp=float(
                    clean_row[13]) if clean_row[13].strip() != 'None' else None,
                rain_percentage=float(
                    clean_row[14]) if clean_row[14].strip() != 'None' else 0.0
            )
            results.append(driver_data)

        return results

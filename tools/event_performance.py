from pydantic import BaseModel, Field
from typing import Type
from langchain_core.tools import BaseTool
from db.connection import db
from . import console


class GetEventPerformanceOutput(BaseModel):
    """Output for the get_event_performance tool"""
    event_name: str = Field(description="Name of the event")
    country: str = Field(description="Country where the event took place")
    location: str = Field(description="Specific location of the event")
    session_type: str = Field(
        description="Type of session (Practice, Qualifying, Race)")
    driver_count: int = Field(
        description="Number of drivers that participated")
    avg_lap_time: float = Field(description="Average lap time in seconds")
    best_lap_time: float = Field(description="Best lap time in seconds")
    max_finish_line_speed: float = Field(
        description="Maximum speed at finish line in km/h")
    avg_air_temp: float | None = Field(
        description="Average air temperature in celsius")
    avg_track_temp: float | None = Field(
        description="Average track temperature in celsius")
    rain_percentage: float = Field(
        description="Percentage of time it rained during the session")


class GetEventPerformance(BaseTool):
    name: str = "get_event_performance"
    description: str = "useful for when you need to get performance statistics for Formula 1 events"

    def _run(self) -> list[GetEventPerformanceOutput]:
        """Use the tool."""
        sql_file = open("tools/sql/event_performance.query.sql", "r")
        sql_query = sql_file.read()
        sql_file.close()

        console.print("getting event performance data")
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
            event_data = GetEventPerformanceOutput(
                event_name=clean_row[0].strip("'"),
                country=clean_row[1].strip("'"),
                location=clean_row[2].strip("'"),
                session_type=clean_row[3].strip("'"),
                driver_count=int(float(clean_row[4])),
                avg_lap_time=float(
                    clean_row[5]) if clean_row[5].strip() != 'None' else 0.0,
                best_lap_time=float(
                    clean_row[6]) if clean_row[6].strip() != 'None' else 0.0,
                max_finish_line_speed=float(
                    clean_row[7]) if clean_row[7].strip() != 'None' else 0.0,
                avg_air_temp=float(
                    clean_row[8]) if clean_row[8].strip() != 'None' else None,
                avg_track_temp=float(
                    clean_row[9]) if clean_row[9].strip() != 'None' else None,
                rain_percentage=float(
                    clean_row[10]) if clean_row[10].strip() != 'None' else 0.0
            )
            results.append(event_data)

        return results

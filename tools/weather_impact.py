from pydantic import BaseModel, Field
from typing import Type
from langchain_core.tools import BaseTool
from rich.console import Console
from . import db

console = Console(style="chartreuse1 on grey7")


class GetWeatherImpactInput(BaseModel):
    """Input for the get_weather_impact tool"""
    # Note: This tool doesn't require input parameters as it returns weather impact data
    pass


class GetWeatherImpactOutput(BaseModel):
    """Output for the get_weather_impact tool"""
    event_name: str = Field(description="Name of the event")
    session_type: str = Field(
        description="Type of session (Practice, Qualifying, Race)")
    track_name: str = Field(description="Name of the track")
    avg_air_temp: float | None = Field(
        description="Average air temperature in celsius")
    avg_track_temp: float | None = Field(
        description="Average track temperature in celsius")
    avg_humidity: float | None = Field(
        description="Average relative humidity percentage")
    avg_wind_speed: float | None = Field(
        description="Average wind speed in meters per second")
    rain_percentage: float = Field(
        description="Percentage of time it rained during the session")
    avg_lap_time: float | None = Field(
        description="Average lap time in seconds")
    best_lap_time: float | None = Field(description="Best lap time in seconds")


class GetWeatherImpact(BaseTool):
    name: str = "get_weather_impact"
    description: str = "useful for when you need to analyze how weather conditions impact Formula 1 session performance"
    args_schema: Type[BaseModel] = GetWeatherImpactInput

    def _run(self) -> GetWeatherImpactOutput:
        """Use the tool."""
        sql_file = open("tools/sql/weather_impact.query.sql", "r")
        sql_query = sql_file.read()
        sql_file.close()

        console.print("getting weather impact data")
        response = db.run(sql_query)

        if not isinstance(response, str):
            response = str(response)

        # Clean up the single row response
        clean_row = response.strip('[]()').split(',')

        # Convert to appropriate types and create output object
        return GetWeatherImpactOutput(
            event_name=clean_row[0].strip("'"),
            session_type=clean_row[1].strip("'"),
            track_name=clean_row[2].strip("'"),
            avg_air_temp=float(
                clean_row[3]) if clean_row[3].strip() != 'None' else None,
            avg_track_temp=float(
                clean_row[4]) if clean_row[4].strip() != 'None' else None,
            avg_humidity=float(
                clean_row[5]) if clean_row[5].strip() != 'None' else None,
            avg_wind_speed=float(
                clean_row[6]) if clean_row[6].strip() != 'None' else None,
            rain_percentage=float(
                clean_row[7]) if clean_row[7].strip() != 'None' else 0.0,
            avg_lap_time=float(
                clean_row[8]) if clean_row[8].strip() != 'None' else None,
            best_lap_time=float(
                clean_row[9]) if clean_row[9].strip() != 'None' else None
        )

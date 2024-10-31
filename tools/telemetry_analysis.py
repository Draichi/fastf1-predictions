from pydantic import BaseModel, Field
from typing import Type
from langchain_core.tools import BaseTool
from . import db, console


class GetTelemetryAndWeatherInput(BaseModel):
    """Input for the get_telemetry_and_weather tool"""
    driver_name: str = Field(
        description="Name of the driver to analyze (e.g., 'VER', 'HAM', 'LEC', etc.)")
    lap_number: int = Field(description="Lap number to analyze")


class GetTelemetryAndWeatherOutput(BaseModel):
    """Output for the get_telemetry_and_weather tool"""
    lap_id: int = Field(description="Lap ID")
    lap_number: int = Field(description="Lap number")
    lap_time_in_seconds: float | None = Field(
        description="Lap time in seconds")
    avg_speed: float = Field(description="Average speed in km/h")
    max_speed: float = Field(description="Maximum speed in km/h")
    avg_RPM: float = Field(description="Average RPM")
    max_RPM: float = Field(description="Maximum RPM")
    avg_throttle: float = Field(description="Average throttle")
    brake_percentage: float = Field(description="Brake percentage")
    drs_usage_percentage: float = Field(description="Drs usage percentage")
    off_track_percentage: float = Field(description="Off track percentage")
    avg_air_temp: float | None = Field(
        description="Average air temperature in celsius")
    avg_track_temp: float | None = Field(
        description="Average track temperature in celsius")
    avg_wind_speed: float | None = Field(
        description="Average wind speed in meters per second")


class GetTelemetry(BaseTool):
    name: str = "get_telemetry"
    description: str = "useful for when you need to answer questions about telemetry for a given driver and lap"
    args_schema: Type[BaseModel] = GetTelemetryAndWeatherInput

    def _run(
        self, driver_name: str, lap_number: int
    ) -> GetTelemetryAndWeatherOutput:
        # """Use the tool."""
        sql_file = open("tools/sql/telemetry_analysis.query.sql", "r")
        sql_query = sql_file.read()
        sql_file.close()
        console.print("getting telemetry")
        response = db.run(sql_query, parameters={
            "driver_name": driver_name,
            "lap_number": lap_number})

        if not isinstance(response, str):
            response = str(response)

        clean_response = response.strip('[]()').split(',')
        # Convert to appropriate types and create dictionary
        return GetTelemetryAndWeatherOutput(
            lap_id=int(float(clean_response[0])),
            lap_number=int(float(clean_response[1])),
            lap_time_in_seconds=float(
                clean_response[2]) if clean_response[2].strip() != 'None' else None,
            avg_speed=float(clean_response[3]),
            max_speed=float(clean_response[4]),
            avg_RPM=float(clean_response[5]),
            max_RPM=float(clean_response[6]),
            avg_throttle=float(clean_response[7]),
            brake_percentage=float(clean_response[8]),
            drs_usage_percentage=float(clean_response[9]),
            off_track_percentage=float(clean_response[10]),
            avg_air_temp=float(
                clean_response[11]) if clean_response[11].strip() != 'None' else None,
            avg_track_temp=float(
                clean_response[12]) if clean_response[12].strip() != 'None' else None,
            avg_wind_speed=float(
                clean_response[13]) if clean_response[13].strip() != 'None' else None
        )

from pydantic import BaseModel, Field
from typing import Type
from langchain_core.tools import BaseTool
from db.connection import db
from . import console


class GetTyrePerformanceInput(BaseModel):
    """Input for the get_tyre_performance tool"""
    driver_name: str = Field(description="Name of the driver to analyze")


class GetTyrePerformanceOutput(BaseModel):
    """Output for the get_tyre_performance tool"""
    driver_name: str = Field(description="Name of the driver")
    lap_number: int = Field(description="Lap number")
    tyre_compound: str = Field(description="Type of tyre compound used")
    avg_tyre_life: float | None = Field(
        description="Average tyre life in laps")
    avg_lap_time: float | None = Field(
        description="Average lap time in seconds")
    avg_top_speed: float | None = Field(
        description="Average top speed in longest straight in km/h")
    fresh_tyre_laps: int = Field(
        description="Number of laps done with fresh tyres")
    used_tyre_laps: int = Field(
        description="Number of laps done with used tyres")
    avg_track_temp: float | None = Field(
        description="Average track temperature in celsius")
    avg_air_temp: float | None = Field(
        description="Average air temperature in celsius")


class GetTyrePerformance(BaseTool):
    name: str = "get_tyre_performance"
    description: str = "useful for when you need to analyze tyre performance and degradation for a specific driver across all their laps"
    args_schema: Type[BaseModel] = GetTyrePerformanceInput

    def _run(self, driver_name: str) -> list[GetTyrePerformanceOutput]:
        """Use the tool."""
        sql_file = open("tools/sql/tyre_performance.query.sql", "r")
        sql_query = sql_file.read()
        sql_file.close()

        console.print("getting tyre performance data")
        response = db.run(sql_query, parameters={
            "driver_name": driver_name
        })

        if not isinstance(response, str):
            response = str(response)

        # Remove the outer brackets and split by rows
        rows = response.strip('[]').split('), (')

        results = []
        for row in rows:
            # Clean up the row string and split by columns
            clean_row = row.strip('()').split(',')

            # Convert to appropriate types and create output object
            tyre_data = GetTyrePerformanceOutput(
                driver_name=clean_row[0].strip("'"),
                lap_number=int(float(clean_row[1])),
                tyre_compound=clean_row[2].strip("'"),
                avg_tyre_life=float(
                    clean_row[3]) if clean_row[3].strip() != 'None' else None,
                avg_lap_time=float(
                    clean_row[4]) if clean_row[4].strip() != 'None' else None,
                avg_top_speed=float(
                    clean_row[5]) if clean_row[5].strip() != 'None' else None,
                fresh_tyre_laps=int(
                    float(clean_row[6])) if clean_row[6].strip() != 'None' else 0,
                used_tyre_laps=int(
                    float(clean_row[7])) if clean_row[7].strip() != 'None' else 0,
                avg_track_temp=float(
                    clean_row[8]) if clean_row[8].strip() != 'None' else None,
                avg_air_temp=float(
                    clean_row[9]) if clean_row[9].strip() != 'None' else None
            )
            results.append(tyre_data)

        return results

from rich.console import Console
from .driver_performance import GetDriverPerformance
from .event_performance import GetEventPerformance
from .telemetry_analysis import GetTelemetry
from .tyre_performance import GetTyrePerformance
from .weather_impact import GetWeatherImpact

console = Console(style="chartreuse1 on grey7")

__all__ = [
    "GetDriverPerformance",
    "GetEventPerformance",
    "GetTelemetry",
    "GetTyrePerformance",
    "GetWeatherImpact",
    "console",
    "db"
]

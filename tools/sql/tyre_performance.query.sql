SELECT 
    l.driver_name,
    l.lap_number,
    l.tyre_compound,
    AVG(l.tyre_life_in_laps) AS avg_tyre_life,
    AVG(l.lap_time_in_seconds) AS avg_lap_time,
    AVG(l.longest_strait_speed_trap_in_km) AS avg_top_speed,
    COUNT(CASE WHEN l.is_fresh_tyre THEN 1 END) AS fresh_tyre_laps,
    COUNT(CASE WHEN NOT l.is_fresh_tyre THEN 1 END) AS used_tyre_laps,
    AVG(w.track_temperature_in_celsius) AS avg_track_temp,
    AVG(w.air_temperature_in_celsius) AS avg_air_temp
FROM Laps l
INNER JOIN Weather w ON l.session_id = w.session_id 
    AND l.lap_start_time_in_datetime BETWEEN w.datetime AND datetime(w.datetime, '+5 minutes')
WHERE l.driver_name = :driver_name
GROUP BY l.driver_name, l.lap_number, l.tyre_compound;
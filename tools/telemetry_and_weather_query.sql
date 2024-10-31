SELECT 
    l.lap_id,
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
WHERE l.driver_name = :driver_name
    AND l.lap_number = :lap_number
GROUP BY l.lap_id;
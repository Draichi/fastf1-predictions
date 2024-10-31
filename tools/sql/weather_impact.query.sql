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
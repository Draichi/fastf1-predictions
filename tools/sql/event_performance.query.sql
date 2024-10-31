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
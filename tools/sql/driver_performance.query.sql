SELECT 
    l.driver_name,
    e.event_name,
    s.session_type,
    t.track_name,
    COUNT(l.lap_id) AS total_laps,
    AVG(l.lap_time_in_seconds) AS avg_lap_time,
    MIN(l.lap_time_in_seconds) AS best_lap_time,
    AVG(l.sector_1_time_in_seconds) AS avg_sector1_time,
    AVG(l.sector_2_time_in_seconds) AS avg_sector2_time,
    AVG(l.sector_3_time_in_seconds) AS avg_sector3_time,
    AVG(l.finish_line_speed_trap_in_km) AS avg_finish_line_speed,
    COUNT(CASE WHEN l.is_personal_best THEN 1 END) AS personal_best_laps,
    AVG(w.air_temperature_in_celsius) AS avg_air_temp,
    AVG(w.track_temperature_in_celsius) AS avg_track_temp,
    SUM(CASE WHEN w.is_raining THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS rain_percentage
FROM Laps l
JOIN Sessions s ON l.session_id = s.session_id
JOIN Tracks t ON s.track_id = t.track_id
JOIN Event e ON s.event_id = e.event_id
LEFT JOIN Weather w ON s.session_id = w.session_id 
    AND l.lap_start_time_in_datetime BETWEEN w.datetime AND datetime(w.datetime, '+1 minutes')
GROUP BY l.driver_name, e.event_id, s.session_id;
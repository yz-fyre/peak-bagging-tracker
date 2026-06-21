SELECT COUNT(*) FROM wainwrights;

SELECT COUNT(*) FROM wainwrights WHERE Completed = 1;

SELECT Area, COUNT(*) AS total, SUM(CAST(Completed AS INT)) AS completed
FROM wainwrights
GROUP BY Area;
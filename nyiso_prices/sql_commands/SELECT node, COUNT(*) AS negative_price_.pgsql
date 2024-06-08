SELECT node, COUNT(*) AS negative_price_occurences
FROM energy_prices
WHERE price < 0
GROUP BY node
ORDER BY COUNT(*) DESC
LIMIT 10;

#SELECT node, SUM(price) AS negative_price_occurences
#FROM energy_prices
#WHERE price < 0
#GROUP BY node
#ORDER BY COUNT(*) DESC
#LIMIT 10;

#SELECT node, STDDEV_POP(price) AS price_volatility
#FROM energy_prices
#GROUP BY node
#ORDER BY price_volatility DESC
#LIMIT 10;
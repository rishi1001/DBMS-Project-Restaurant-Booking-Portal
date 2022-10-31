SELECT name FROM (SELECT * FROM liked WHERE restaurantid = 1) as temp, likedref where temp.likedid=likedref.likedid;

SELECT phone FROM phones WHERE restaurantid = 1;

SELECT name FROM (SELECT * FROM cuisines WHERE restaurantid = 1) as temp, cuisinesref where temp.cuisineid=cuisinesref.cuisineid;

SELECT * FROM restaurants WHERE restaurantid = 1 limit 1;

SELECT * FROM user_login WHERE username ='rishi';

SELECT * FROM restaurant_login WHERE username = 'rishi';

SELECT username FROM user_login WHERE userid = 1;

SELECT listedid FROM listedref WHERE name = 'Buffet';

SELECT restaurants.name,url,restaurants.restaurantid,address,listedref.name,locationref.name,costfortwo FROM restaurants,cuisines,listedref,locationref WHERE restaurants.listedid = 1 and costfortwo<999999 and costfortwo>=0 and restaurants.name like 'Jal%' and rating < 5 and rating>=0 and restaurants.locationid=1 and restaurants.restaurantid = cuisines.restaurantid and cuisines.cuisineid = 1 and restaurants.listedid = listedref.listedid and restaurants.locationid=locationref.locationid order by votes desc limit 100;

SELECT name FROM cuisinesref ORDER BY name;

UPDATE bookings SET status = 'ACCEPTED' WHERE bookingid = 1;

SELECT bookingid,restaurants.name,person,date,time,status,restaurants.restaurantid FROM bookings,restaurants where userid =1 and restaurants.restaurantid = bookings.restaurantid  order by date asc, time asc;

SELECT reviewid, rating FROM reviews WHERE restaurantid = 1 and userid = 1 limit 1;

INSERT INTO user_login VALUES (1000000,'notme123','pass123');

SELECT locationid FROM locationref ORDER BY locationid DESC limit 1;
-- drop database if exists col362project;
-- create database col362project;
-- \c col362project

drop table if exists restaurants cascade;
drop table if exists cuisinesref cascade;
drop table if exists cuisines cascade;
drop table if exists likedref cascade;
drop table if exists liked cascade;
drop table if exists listedref cascade;
drop table if exists locationref cascade;
drop table if exists phones cascade;
drop table if exists typesref cascade;
drop table if exists types cascade;
drop table if exists reviews cascade;
drop table if exists user_login cascade;
drop table if exists restaurant_login cascade;
drop table if exists bookings cascade;
drop index if exists index1;
drop index if exists index2;
drop index if exists index3;
drop materialized view if exists popular;
drop PROCEDURE if exists refresh_popular;
drop trigger if exists trigger_popular on restaurants;

CREATE table IF NOT EXISTS cuisinesref(
    cuisineid bigint,
    name text,
    CONSTRAINT cuisine_key PRIMARY KEY (cuisineid),
    CONSTRAINT unique9 unique(name)
);
CREATE table IF NOT EXISTS listedref(
    listedid bigint,
    name text,
    CONSTRAINT listed_key PRIMARY KEY (listedid),
    CONSTRAINT unique10 unique(name)
);

CREATE table IF NOT EXISTS locationref(
    locationid bigint,
    name text,
    CONSTRAINT locationid PRIMARY KEY (locationid),
    CONSTRAINT unique11 unique(name)
);
CREATE table IF NOT EXISTS restaurants(
    restaurantid bigint,
    locationid bigint,
    listedid bigint,
    onlineorder text,
    rating float,
    votes bigint,
    costfortwo bigint,
    name text,
    url text,
    address text,
    CONSTRAINT restaurant_key PRIMARY KEY (restaurantid),
    CONSTRAINT listed_foreign_key FOREIGN KEY (listedid) REFERENCES listedref(listedid),
    CONSTRAINT unique1 unique(name, address)

);
CREATE table IF NOT EXISTS cuisines(
    restaurantid bigint,
    cuisineid bigint,
    CONSTRAINT cuisine_foreign_key FOREIGN KEY (cuisineid) REFERENCES cuisinesref(cuisineid),
    CONSTRAINT cuisine_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid),
    CONSTRAINT unique2 unique(restaurantid, cuisineid)
);

CREATE table IF NOT EXISTS likedref(
    likedid bigint,
    name text,
    CONSTRAINT liked_key PRIMARY KEY (likedid)
);

CREATE table IF NOT EXISTS liked(
    restaurantid bigint,
    likedid bigint,
    CONSTRAINT liked_foreign_key FOREIGN KEY (likedid) REFERENCES likedref(likedid),
    CONSTRAINT liked_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid),
    CONSTRAINT unique3 unique(restaurantid, likedid)
);


CREATE table IF NOT EXISTS phones(
    restaurantid bigint,
    phone text,
    CONSTRAINT phone_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid),
    CONSTRAINT unique4 unique(restaurantid, phone)
);

CREATE table IF NOT EXISTS typesref(
    typeid bigint,
    name text,
    CONSTRAINT types_key PRIMARY KEY (typeid)
);

CREATE table IF NOT EXISTS types(
    restaurantid bigint,
    typeid bigint,
    CONSTRAINT types_foreign_key FOREIGN KEY (typeid) REFERENCES typesref(typeid),
    CONSTRAINT types_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid),
    CONSTRAINT unique5 unique(restaurantid, typeid)
);

CREATE table IF NOT EXISTS reviews(
    restaurantid bigint,
    reviewid bigint,
    userid bigint,
    rating float,
    review text,
    CONSTRAINT review_key PRIMARY KEY (reviewid),
    CONSTRAINT rest_foreign_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid)
);

CREATE table if NOT EXISTS user_login(
    userid bigint,
    username text,
    password text,
    CONSTRAINT user_login_key PRIMARY KEY (userid),
    CONSTRAINT unique7 unique(username)
);

CREATE table if not EXISTS restaurant_login(
    restaurantid bigint,
    username text,
    password text,
    CONSTRAINT restaurant_login_key PRIMARY KEY (restaurantid),
    CONSTRAINT unique8 unique(username)
);

CREATE table if NOT EXISTS bookings(
    bookingid bigint,
    userid bigint,
    restaurantid bigint,
    person bigint,
    date date,
    time time,
    status text,
    CONSTRAINT bookings_key PRIMARY KEY (bookingid),
    CONSTRAINT booking_foreign_key1 FOREIGN KEY (userid) REFERENCES user_login(userid),
    CONSTRAINT booking_foreign_key2 FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid)
);

\copy cuisinesref from '/Users/rishi_1001/Documents/DBMS-Project/Data/cuisinesref.csv' delimiter ',' csv header encoding 'win1250';

\copy listedref from '/Users/rishi_1001/Documents/DBMS-Project/Data/listedref.csv' delimiter ',' csv header encoding 'win1250';

\copy locationref from '/Users/rishi_1001/Documents/DBMS-Project/Data/locationref.csv' delimiter ',' csv header encoding 'win1250';

\copy restaurants from '/Users/rishi_1001/Documents/DBMS-Project/Data/restaurants.csv' delimiter ',' csv header encoding 'win1250';

Update restaurants set locationid = NULL where locationid < 0;
Update restaurants set costfortwo = NULL where costfortwo < 0;
Update restaurants set rating = NULL where rating < 0;


alter table restaurants add CONSTRAINT location_foreign_key FOREIGN KEY (locationid) REFERENCES locationref(locationid);


\copy cuisines from '/Users/rishi_1001/Documents/DBMS-Project/Data/cuisines.csv' delimiter ',' csv header encoding 'win1250';

\copy likedref from '/Users/rishi_1001/Documents/DBMS-Project/Data/likedref.csv' delimiter ',' csv header encoding 'win1250';

\copy liked from '/Users/rishi_1001/Documents/DBMS-Project/Data/liked.csv' delimiter ',' csv header encoding 'win1250';

\copy phones from '/Users/rishi_1001/Documents/DBMS-Project/Data/phones.csv' delimiter ',' csv header encoding 'win1250';

\copy typesref from '/Users/rishi_1001/Documents/DBMS-Project/Data/typesref.csv' delimiter ',' csv header encoding 'win1250';

\copy types from '/Users/rishi_1001/Documents/DBMS-Project/Data/types.csv' delimiter ',' csv header encoding 'win1250';

\copy reviews from '/Users/rishi_1001/Documents/DBMS-Project/Data/reviews.csv' delimiter ',' csv header encoding 'win1250';

Update reviews set userid = NULL where userid < 0;
alter table reviews add CONSTRAINT unique6 unique(restaurantid, userid);

alter table reviews add CONSTRAINT user_foreign_key FOREIGN KEY (userid) REFERENCES user_login(userid);

\copy restaurant_login from '/Users/rishi_1001/Documents/DBMS-Project/Data/restaurant_login.csv' delimiter ',' csv header encoding 'win1250';

alter table restaurants add CONSTRAINT restaurant_foreign_key FOREIGN KEY (restaurantid) REFERENCES restaurant_login(restaurantid);

create index index1 on reviews(restaurantid);
create index index2 on restaurants(locationid);
create index index3 on restaurants(name);

create materialized view popular as select restaurantid,locationid,listedid,onlineorder,costfortwo,restaurants.name,url,address from restaurants, (select name, max(votes) from restaurants group by name order by max desc) as temp where restaurants.name=temp.name and restaurants.votes=max order by max desc limit 100;

CREATE OR REPLACE FUNCTION refresh_popular() RETURNS trigger LANGUAGE plpgsql AS
$$
BEGIN
-- REFRESH MATERIALIZED VIEW popular;
NOTIFY refresh_, '60 REFRESH MATERIALIZED VIEW popular';
RETURN NULL;
END;
$$;

CREATE TRIGGER trigger_popular AFTER INSERT ON restaurants EXECUTE PROCEDURE refresh_popular();
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
drop table if exists login_info cascade;
CREATE table IF NOT EXISTS cuisinesref(
    cuisineid bigint,
    name text,
    CONSTRAINT cuisine_key PRIMARY KEY (cuisineid)
);
CREATE table IF NOT EXISTS listedref(
    listedid bigint,
    name text,
    CONSTRAINT listed_key PRIMARY KEY (listedid)
);

CREATE table IF NOT EXISTS locationref(
    locationid bigint,
    name text,
    CONSTRAINT locationid PRIMARY KEY (locationid)
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
    CONSTRAINT listed_foreign_key FOREIGN KEY (listedid) REFERENCES listedref(listedid)

);
CREATE table IF NOT EXISTS cuisines(
    restaurantid bigint,
    cuisineid bigint,
    CONSTRAINT cuisine_foreign_key FOREIGN KEY (cuisineid) REFERENCES cuisinesref(cuisineid),
    CONSTRAINT cuisine_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid)
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
    CONSTRAINT liked_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid)
);


CREATE table IF NOT EXISTS phones(
    restaurantid bigint,
    phone text,
    CONSTRAINT phone_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid)
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
    CONSTRAINT types_restaurant_key FOREIGN KEY (restaurantid) REFERENCES restaurants(restaurantid)
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

CREATE table if NOT EXISTS login_info(
    userid bigint,
    username text,
    password text,
    CONSTRAINT login_key PRIMARY KEY (userid)
);

\copy cuisinesref from '/Users/ishaansingh/Desktop/DBMS-Project/Data/cuisinesref.csv' delimiter ',' csv header encoding 'win1250';

\copy listedref from '/Users/ishaansingh/Desktop/DBMS-Project/Data/listedref.csv' delimiter ',' csv header encoding 'win1250';

\copy locationref from '/Users/ishaansingh/Desktop/DBMS-Project/Data/locationref.csv' delimiter ',' csv header encoding 'win1250';

\copy restaurants from '/Users/ishaansingh/Desktop/DBMS-Project/Data/restaurants.csv' delimiter ',' csv header encoding 'win1250';

Update restaurants set locationid = NULL where locationid = -1;

alter table restaurants add CONSTRAINT location_foreign_key FOREIGN KEY (locationid) REFERENCES locationref(locationid);


\copy cuisines from '/Users/ishaansingh/Desktop/DBMS-Project/Data/cuisines.csv' delimiter ',' csv header encoding 'win1250';

\copy likedref from '/Users/ishaansingh/Desktop/DBMS-Project/Data/likedref.csv' delimiter ',' csv header encoding 'win1250';

\copy liked from '/Users/ishaansingh/Desktop/DBMS-Project/Data/liked.csv' delimiter ',' csv header encoding 'win1250';

\copy phones from '/Users/ishaansingh/Desktop/DBMS-Project/Data/phones.csv' delimiter ',' csv header encoding 'win1250';

\copy typesref from '/Users/ishaansingh/Desktop/DBMS-Project/Data/typesref.csv' delimiter ',' csv header encoding 'win1250';

\copy types from '/Users/ishaansingh/Desktop/DBMS-Project/Data/types.csv' delimiter ',' csv header encoding 'win1250';

\copy reviews from '/Users/ishaansingh/Desktop/DBMS-Project/Data/reviews.csv' delimiter ',' csv header encoding 'win1250';

Update reviews set userid = NULL where userid = -1;

alter table reviews add CONSTRAINT user_foreign_key FOREIGN KEY (userid) REFERENCES login_info(userid);

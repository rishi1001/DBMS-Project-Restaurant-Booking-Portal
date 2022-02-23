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
    CONSTRAINT restaurant_key PRIMARY KEY (restaurantid)
);

CREATE table IF NOT EXISTS cuisinesref(
    cuisineid bigint,
    name text,
    CONSTRAINT cuisine_key PRIMARY KEY (cuisineid)
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
    CONSTRAINT review_key PRIMARY KEY (reviewid)
);


copy restaurants from '/Users/rishi_1001/Documents/DBMS-Project/Data/restaurants.csv' delimiter ',' csv header encoding 'win1250';

copy cuisinesref from '/Users/rishi_1001/Documents/DBMS-Project/Data/cuisinesref.csv' delimiter ',' csv header encoding 'win1250';

copy cuisines from '/Users/rishi_1001/Documents/DBMS-Project/Data/cuisines.csv' delimiter ',' csv header encoding 'win1250';

copy likedref from '/Users/rishi_1001/Documents/DBMS-Project/Data/likedref.csv' delimiter ',' csv header encoding 'win1250';

copy liked from '/Users/rishi_1001/Documents/DBMS-Project/Data/liked.csv' delimiter ',' csv header encoding 'win1250';

copy listedref from '/Users/rishi_1001/Documents/DBMS-Project/Data/listedref.csv' delimiter ',' csv header encoding 'win1250';

copy locationref from '/Users/rishi_1001/Documents/DBMS-Project/Data/locationref.csv' delimiter ',' csv header encoding 'win1250';

copy phones from '/Users/rishi_1001/Documents/DBMS-Project/Data/phones.csv' delimiter ',' csv header encoding 'win1250';

copy typesref from '/Users/rishi_1001/Documents/DBMS-Project/Data/typesref.csv' delimiter ',' csv header encoding 'win1250';

copy types from '/Users/rishi_1001/Documents/DBMS-Project/Data/types.csv' delimiter ',' csv header encoding 'win1250';

copy reviews from '/Users/rishi_1001/Documents/DBMS-Project/Data/reviews.csv' delimiter ',' csv header encoding 'win1250';

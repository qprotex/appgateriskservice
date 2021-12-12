CREATE TABLE Users (id INTEGER PRIMARY KEY, username text);
INSERT INTO Users VALUES (1, 'UserA');

CREATE TABLE UserComputers (id INTEGER PRIMARY KEY, userId INTEGER, fingerPrint text);
INSERT INTO UserComputers VALUES (1, 1, 'PostmanRuntime/7.28.4');
INSERT INTO UserComputers VALUES (2, 1, 'Custom User Agent');


CREATE TABLE UserStats (id INTEGER PRIMARY KEY AUTOINCREMENT, userId INTEGER, lastsuccessfullogindate INTEGER);
INSERT INTO UserStats VALUES (1, 1, strftime('%s','2021-12-1'));

CREATE TABLE CompanyNetwork (id INTEGER PRIMARY KEY, range text);
INSERT INTO CompanyNetwork VALUES (1, '10.97.2.0/24');

CREATE TABLE LogData (id INTEGER PRIMARY KEY AUTOINCREMENT, source text, username text, ip text, fingerPrint text, createdDate INTEGER, loginStatus INTEGER);
INSERT INTO LogData VALUES (1, 'website', 'UserA', '10.97.2.10', 'PostmanRuntime/7.28.4', strftime('%s','2021-12-10'), true);
INSERT INTO LogData VALUES (2, 'mobile', 'UserA', '10.97.2.10', 'PostmanRuntime/7.28.4', strftime('%s','now'), true);
INSERT INTO LogData VALUES (3, 'mobile', 'UserA', '10.97.2.10', 'PostmanRuntime/7.28.4', strftime('%s','now'), true);
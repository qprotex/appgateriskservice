CREATE TABLE Users (id int, username text);
INSERT INTO Users VALUES (1, 'UserA');

CREATE TABLE UserComputers (id int, userId int, fingerPrint text);
INSERT INTO UserComputers VALUES (1, 1, 'PostmanRuntime/7.28.4');
INSERT INTO UserComputers VALUES (2, 1, 'Custom User Agent');

CREATE TABLE CompanyNetwork (id int, range text);
INSERT INTO CompanyNetwork VALUES (1, '10.97.2.0/24');

CREATE TABLE LogData (id int, username text, ip text, fingerPrint text, createdDate int, loginStatus int);
INSERT INTO LogData VALUES (1, 'UserA', '10.97.2.10', 'PostmanRuntime/7.28.4', strftime('%s','now'), true);
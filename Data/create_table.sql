create database innovation;
use innovation;
show tables;

create table account
(
id varchar(50),
institution varchar(50),
created_date timestamp,
card_name varchar(50),
account_type varchar(50),
balance float,
total_limit float
);


create table transaction
(
id varchar(50),
customer_id varchar(50),
account_id varchar(50),
posted_date timestamp,
amount float,
category_name varchar(50),
merchant varchar(50)
);

insert into account values ('1111','Chase','2014-08-01','Freedom','200',3250,6500),('1112','Chase','2015-10-28','Sapphire','200',2821,9000),('1113','BOA','2013-09-25','CashReward','200',1450,8500),('1114','Discover','2014-04-20','Discover','200',450,4000),('1115','Chase','2013-06-22','Checking','100',4500,0),('1116','Chase','2013-06-22','Saving','101',18000,0),('1117','BOA','2013-08-18','Saving','101',18000,0);

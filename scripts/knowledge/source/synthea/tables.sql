
-- https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary 

create database if not exists synthea;

use synthea;

select 'Loading patients.' as '';

drop table if exists patients;
create table patients (
    id char(36),
    birthdate date,
    deathdate date,
    ssn char(11),
    drivers varchar(255),
    passport varchar(255),
    prefix varchar(255),
    `first` varchar(255),
    `last` varchar(255),
    suffix varchar(255),
    maiden varchar(255),
    martial tinyint unsigned,
    race varchar(255),
    ethnicity varchar(255),
    gender tinyint unsigned
);

load data local infile '/home/benjamin/shared/data/import/synthea/patients.csv' into table patients
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @id, @birthdate, @deathdate, @ssn, @drivers, @passport,
        @prefix, @first, @last, @suffix, @maiden, @martial,
        @race, @ethnicity, @gender, @birthplace, @address,
        @city, @country, @state, @zip, @lat, @lon,
        @healthcare_expenses, @healthcare_coverage  )
set
    id = @id,
    birthdate = @birthdate,
    deathdate = (case @deathdate when "" then null else @deathdate end),
    ssn = (case @ssn when "" then null else @ssn end),
    drivers = (case @drivers when "" then null else @drivers end),
    passport = (case @passport when "" then null else @passport end),
    prefix = (case @prefix when "" then null else @prefix end),
    `first` = @first,
    `last` = @last,
    suffix = (case @suffix when "" then null else @suffix end),
    maiden = (case @maiden when "" then null else @maiden end),
    martial = (@martial = "M"),
    race = @race,
    ethnicity = @ethnicity,
    gender = (@gender = "M");

select 'Loading encounters.' as '';

drop table if exists encounters;
create table encounters (
    id char(36),
    `start` timestamp null default null,
    `end` timestamp null default null,
    patient char(36),
    `type` varchar(255),
    code varchar(255),
    `description` varchar(255),
    reason_code varchar(255),
    reason_description varchar(255)
);

load data local infile '/home/benjamin/shared/data/import/synthea/encounters.csv' into table encounters
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @id, @start, @end, @patient, @provider, @payer, @type, @code, 
        @description, @base_cost, @total_cost, @payer_coverage, 
        @reason_code, @reason_description )
set
    id = @id,
    `start` = @start,
    `end` = (case @end when "" then null else @end end),
    patient = @patient,
    `type` = @type,
    code = @code,
    `description` = @description,
    reason_code = (case @reason_code when "" then null else @reason_code end),
    reason_description = (case @reason_description when "" then null else @reason_description end);

select 'Loading observations.' as '';

drop table if exists observations;
create table observations (
    `date` date,
    patient char(36),
    encounter char(36),
    code varchar(255),
    `description` varchar(255),
    `value` varchar(255),
    unit varchar(255),
    `type` varchar(255)
);

load data local infile '/home/benjamin/shared/data/import/synthea/observations.csv' into table observations
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @date, @patient, @encounter, @code,
        @description, @value, @unit, @type  )
set
    `date` = @date,
    patient = @patient,
    encounter = @encounter,
    code = @code,
    `description` = @description,
    `value` = (case @value when "" then null else @value end),
    unit = (case @unit when "" then null else @unit end),
    `type`= (case @type when "" then null else @type end);

select 'Loading conditions.' as '';

drop table if exists conditions;
create table conditions (
    `start` date,
    `end` date,
    patient char(36),
    encounter char(36),
    code varchar(255),
    `description` varchar(80)
);

load data local infile '/home/benjamin/shared/data/import/synthea/conditions.csv' into table conditions
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @start, @end, @patient,
        @encounter, @code, @description )
set
    `start` = @start,
    `end` = (case @end when "" then null else @end end),
    patient = @patient,
    encounter = @encounter,
    code = @code,
    `description` = @description;

select 'Loading medications.' as '';

drop table if exists medications;
create table medications (
    `start` date,
    `end` date,
    patient char(36),
    encounter char(36),
    code varchar(255),
    `description` varchar(255),
    reason_code varchar(255),
    reason_description varchar(255)
);

load data local infile '/home/benjamin/shared/data/import/synthea/medications.csv' into table medications
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @start, @end, @patient, @payer, @encounter, @code, @description, 
        @base_cost, @payer_coverage, @dispenses, @total_cost, @reason_code, 
        @reason_description  )
set
    `start` = @start,
    `end` = (case @end when "" then null else @end end),
    patient = @patient,
    encounter = @encounter,
    code = (case @code when "" then null else @code end),
    `description` = (case @description when "" then null else @description end),
    reason_code = (case @reason_code when "" then null else @reason_code end),
    reason_description = (case @reason_description when "" then null else @reason_description end);

select 'Loading procedures.' as '';

drop table if exists procedures;
create table procedures (
    `date` date,
    patient char(36),
    encounter char(36),
    code varchar(255),
    `description` varchar(255),
    cost float,
    reason_code varchar(255),
    reason_description varchar(255)
);

load data local infile '/home/benjamin/shared/data/import/synthea/procedures.csv' into table procedures
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @date, @patient, @encounter, @code, @description,
        @cost, @reason_code, @reason_description    )
set
    `date` = @date,
    patient = @patient,
    encounter = @encounter,
    code = @code,
    `description` = @description,
    cost = @cost,
    reason_code = (case @reason_code when "" then null else @reason_code end),
    reason_description = (case @reason_description when "" then null else @reason_description end);

select 'Loading immunizations.' as '';

drop table if exists immunizations;
create table immunizations (
    `date` date,
    patient char(36),
    encounter char(36),
    code varchar(255),
    `description` varchar(255),
    cost float
);

load data local infile '/home/benjamin/shared/data/import/synthea/immunizations.csv' into table immunizations
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @date, @patient, @encounter, @code, @description, @cost )
set
    `date` = @date,
    patient = @patient,
    encounter = @encounter,
    code = @code,
    `description` = @description,
    cost = @cost;

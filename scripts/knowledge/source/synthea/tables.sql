
-- https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary 

create database if not exists synthea;

use synthea;

drop table if exists patients;
create table patients (
    id char(36),
    birthdate date,
    deathdate date,
    ssn char(11),
    drivers varchar(9),
    passport varchar(10),
    prefix varchar(10),
    `first` varchar(16),
    `last` varchar(16),
    suffix varchar(4),
    maiden varchar(16),
    martial tinyint unsigned,
    race varchar(8),
    ethnicity varchar(16),
    gender tinyint unsigned
);

load data local infile '/home/benjamin/Documents/HII-C/data/source/synthea_1m_fhir_3_0_May_24/output_01/csv/patients.csv' into table patients
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 3 lines
    (   @id, @birthdate, @deathdate, @ssn, @drivers, @passport,
        @prefix, @first, @last, @suffix, @maiden, @martial,
        @race, @ethnicity, @gender, @birthplace, @address,
        @city, @country, @state, @zip, @lat, @lon,
        @healthcare_expenses, @healthcare_coverage  )
set
    id = @id,
    birthdate = @birthdate,
    deathdate = (case @deathdate when "" then null else @deathdate),
    ssn = (case @ssn when "" then null else @ssn),
    drivers = (case @drivers when "" then null else @drivers),
    passport = (case @passport when "" then null else @passport),
    prefix = (case @prefix when "" then null else @prefix),
    `first` = @first,
    `last` = @last,
    suffix = (case @suffix when "" then null else @suffix),
    maiden = (case @maiden when "" then null else @maiden),
    martial = (@martial = "M"),
    race = @race,
    ethnicity = @ethnicity,
    gender = (@gender = "M");

drop table if exists encounters;
create table encounters (
    id char(36),
    `date` date,
    patient char(36),
    code int unsigned,
    `description` varchar(58),
    reason_code varchar(15),
    reason_description varchar(69)
);

load data local infile '/home/benjamin/Documents/HII-C/data/source/synthea_1m_fhir_3_0_May_24/output_01/csv/encounters.csv' into table encounters
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @id, @date, @patient, @code, @description, 
        @reason_code, @reason_description  )
set
    id = @id,
    `date` = @date,
    patient = @patient,
    code = (case @code when "" then null else @code end),
    `description` = (case @description when "" then null else @description end),
    reason_code = (case @reason_code when "" then null else @reason_code end),
    reason_description = (case @reason_description when "" then null else @reason_description end);

drop table if exists observations;
create table observations (
    `date` date,
    patient char(36),
    encounter char(36),
    code varchar(9),
    `description` varchar(82),
    `value` varchar(21),
    unit varchar(16)
);

load data local infile '/home/benjamin/Documents/HII-C/data/source/synthea_1m_fhir_3_0_May_24/output_01/csv/observations.csv' into table observations
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @date, @patient, @encounter, @code,
        @description, @value, @unit )
set
    `date` = @date,
    patient = @patient,
    encounter = @encounter,
    code = @code,
    `description` = @description,
    `value` = (case @value when "" then null else @value end),
    unit = (case @unit when "" then null else @unit end);

drop table if exists conditions;
create table conditions (
    `start` date,
    `stop` date,
    patient char(36),
    encounter char(36),
    code bigint unsigned,
    `description` varchar(80)
);

load data local infile '/home/benjamin/Documents/HII-C/data/source/synthea_1m_fhir_3_0_May_24/output_01/csv/conditions.csv' into table conditions
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @start, @stop, @patient,
        @encounter, @code, @description )
set
    `start` = @start,
    `stop` = (case @stop when "" then null else @stop end),
    patient = @patient,
    encounter = @encounter,
    code = @code,
    `description` = @description;

drop table if exists medications;
create table medications (
    `start` date,
    `stop` date,
    patient char(36),
    encounter char(36),
    code mediumint unsigned,
    `description` varchar(100),
    reason_code varchar(14),
    reason_description varchar(69)
);

load data local infile '/home/benjamin/Documents/HII-C/data/source/synthea_1m_fhir_3_0_May_24/output_01/csv/medications.csv' into table medications
    fields terminated by ',' escaped by '\\' optionally enclosed by '"'
    lines terminated by '\n'
    ignore 1 lines
    (   @start, @stop, @patient, @encounter, @code, @description, 
        @reason_code, @reason_description  )
set
    `start` = @start,
    `stop` = (case @stop when "" then null else @stop end),
    patient = @patient,
    encounter = @encounter,
    code = (case @code when "" then null else @code end),
    `description` = (case @description when "" then null else @description end),
    reason_code = (case @reason_code when "" then null else @reason_code end),
    reason_description = (case @reason_description when "" then null else @reason_description end);
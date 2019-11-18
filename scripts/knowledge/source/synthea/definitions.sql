create database if not exists synthea;

use synthea;

drop table if exists patients;
create table patients (
    id char(36),
    birthdate date,
    deathdate date,
    ssn char(11),
    drivers varchar()
)
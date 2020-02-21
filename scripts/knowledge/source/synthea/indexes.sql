
-- https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary 

use synthea;

select 'Creating patient id indexes.' as '';

create index patient using hash on patients(id);
create index patient using hash on encounters(patient);
create index patient using hash on observations(patient);
create index patient using hash on conditions(patient);
create index patient using hash on medications(patient);
create index patient using hash on immunizations(patient);

select 'Creating encounter id indexes.' as '';

create index encounter using hash on encounters(id);
create index encounter using hash on observations(encounter);
create index encounter using hash on conditions(encounter);
create index encounter using hash on medications(encounter);
create index encounter using hash on immunizations(encounter);

select 'Creating temooral indexes.' as '';

create index birthdate on patients(birthdate);
create index deathdate on patients(deathdate);
create index `start` on encounters(`start`);
create index `end` on encounters(`end`);
create index `date` on observations(`date`);
create index `start` on conditions(`start`);
create index `end` on conditions(`end`);
create index `start` on medications(`start`);
create index `end` on medications(`end`);
create index `date` on immunizations(`date`);

select 'Creating concept code indexes.' as '';

create index code using hash on encounters(code);
create index code using hash on observations(code);
create index code using hash on conditions(code);
create index code using hash on medications(code);
create index code using hash on immunizations(code);
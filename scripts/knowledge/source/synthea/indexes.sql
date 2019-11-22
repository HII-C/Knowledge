
-- https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary 

use synthea;

create index patient using hash on patients(id);
create index patient using hash on encounters(patient);
create index patient using hash on observations(patient);
create index patient using hash on conditions(patient);
create index patient using hash on medications(patient);

create index encounter using hash on encounters(id);
create index encounter using hash on observations(encounter);
create index encounter using hash on conditions(encounter);
create index encounter using hash on medications(encounter);
create table derived_codes.derived_cui as
select
    distinct MRCONSO.CODE as loinc_code, MRCONSO.CUI as cui_code
from umls.MRCONSO as MRCONSO
inner join mimiciiiv14.D_LABITEMS as items
on MRCONSO.CODE = items.LOINC_CODE
where MRCONSO.SAB = 'LNC'


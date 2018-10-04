from db_util import DatabaseHandle

x = DatabaseHandle('hiic', 'greenes2018', 'derived', 'db01.healthcreek.org')
x.cursor.execute('select * from derived.patients_as_index')
x.cursor.fetchall()
print(x.cursor.rowcount)

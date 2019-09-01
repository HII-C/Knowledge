models.output.storage.py
--------------------------
* update_storage:
    * generates table 'knowledge.ModelStorage'
    * if table didn't exist before, a new table is generated and the input is the
    initial values of the table.
    * if table does exist, the input values are 'upserted' in to the table
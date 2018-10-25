from typing import List
from util.db_util import DatabaseHandle


class PredicateData:
    pt_db: DatabaseHandle

    def __init__(self, db_params):
        self.pt_db = DatabaseHandle(**db_params)

    def build_tables(self, preds: List[str]):
        query = f'''
                CREATE TABLE predicate_scores
                AS (
                    SELECT (predicate, (subject as concept1), (object as concept2), (count(score) as occ), (avg(score) as avg_score))
                    FROM language_data
                    WHERE pred IN {tuple(preds)}
                    GROUP BY (predicate, subject, object)
                )'''
        self.pt_db.cursor.execute(query)
        self.pt_db.connection.commit()
        for pred in preds:
            query = f'''
                    CREATE TABLE {pred}_predicate_scores 
                    AS (
                        SELECT (subj, obj, occr, `avg`)
                        FROM predicate_scores 
                        WHERE pred = \"{pred}\"
                        )
                    '''
            self.pt_db.cursor.execute(query)
            self.pt_db.connection.commit()

    # def update_tables(self, preds:List[str]):
    #     query = f'''

    #         '''
    #     self.pt_db.cursor.execute(query)
    #     for pred in preds:
    #         query = f'''

    #             '''
    #         self.pt_db.cursor.execute(query)

    def get_table(self, pred: str, cols: List[str]) -> List[List[str]]:
        query = f'''
                SELECT {'*' if cols is None else tuple(cols)}
                FROM {pred}_predicate_scores;'''
        self.pt_db.cursor.execute(query)
        return self.pt_db.cursor.fetchall()

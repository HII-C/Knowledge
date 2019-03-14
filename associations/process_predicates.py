from typing import List, Tuple
from associations.util.db_util import DatabaseHandle


class PredicateData:
    pred_db: DatabaseHandle

    def __init__(self, db_params):
        self.pred_db = DatabaseHandle(**db_params)

    def create_small_semmed(self, output_table, n=10000, semmed_db='semmed', output_db='derived'):
        exec_str = f'''DROP TABLE IF EXISTS {output_db}.{output_table}'''
        self.pred_db.cursor.execute(exec_str)
        self.pred_db.connection.commit()
        exec_str = f'''
                    CREATE TABLE {output_db}.{output_table}
                    AS SELECT pred.SUBJECT_CUI, pred.OBJECT_CUI, pred.PREDICATE, aux.SUBJECT_SCORE, aux.OBJECT_SCORE
                    FROM {semmed_db}.PREDICATION AS pred
                    LEFT JOIN {semmed_db}.PREDICATION_AUX as aux
                    ON pred.PREDICATION_ID = aux.PREDICATION_ID limit {n}'''
        self.pred_db.cursor.execute(exec_str)
        self.pred_db.connection.commit()

    def build_tables(self, preds: Tuple[str], source_db, source_table, output_postfix='by_pair', output_db='derived'):
        query = f'''
                CREATE TABLE {output_db}.tmp_pred_scores
                AS 
                    SELECT PREDICATE, SUBJECT_CUI as concept1, OBJECT_CUI as concept2, COUNT(SUBJECT_SCORE) as occ, AVG(SUBJECT_SCORE) as avg_c1_score, AVG(OBJECT_SCORE) as avg_c2_score
                    FROM {source_db}.{source_table}
                    WHERE PREDICATE = \'{preds[0]}\'
                    GROUP BY PREDICATE, SUBJECT_CUI, OBJECT_CUI'''

        self.pred_db.cursor.execute(query)
        self.pred_db.connection.commit()
        for pred in preds:
            query = f'''
                    CREATE TABLE {output_db}.{pred}_{output_postfix}
                    AS 
                        SELECT concept1, concept2, occ, avg_c1_score, avg_c2_score
                        FROM {output_db}.tmp_pred_scores
                        WHERE PREDICATE = \'{pred}\''''
            self.pred_db.cursor.execute(query)
            self.pred_db.connection.commit()

    # def get_table(self, pred: str, cols: List[str]) -> List[List[str]]:
    #     query = f'''
    #             SELECT {'*' if cols is None else tuple(cols)}
    #             FROM {pred}_predicate_scores;'''
    #     self.pred_db.cursor.execute(query)
    #     return self.pred_db.cursor.fetchall()

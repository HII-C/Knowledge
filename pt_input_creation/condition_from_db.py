from numpy.random import randint, shuffle, random_integers
from typing import List, Dict, Tuple
from collections import defaultdict
from util.db_util import DatabaseHandle
from util.concept_util import ConceptType
#import pymysql.connections as connections
#import pymysql as sql

#POP_N = 651047 #651047 in the DIAGNOSES_ICD table
POP_N = 20

class ConditionPopulation:
    cond_db: DatabaseHandle = None
    cond_list: List[int]
    #conn: connections.Connection = None

    def __init__(self, db_params):
        self.cond_db = DatabaseHandle(**db_params)

    def gen_rand_subj_ids(self, conc: ConceptType, flag: bool) -> List[int]:
        if(conc.get_int() != 1 and flag == True):
            raise ValueError("Concept is not observation, and yet the flag is True")
        elif(conc.get_int() == 1 and flag == True):
            tbl = conc.get_table()
            exec_str = f'''
                            SELECT COUNT(*) 
                            FROM {tbl}
                            WHERE FLAG = 'Abnormal';
                            '''
            self.cursor.execute(exec_str)
            num_rows = self.cursor.fetachall()
            rows = random_integers(1, num_rows, POP_N)
            subj_id_list = list
            for x in rows:
                exec_str = f'''
                                SELECT SUBJECT_ID 
                                FROM {tbl}
                                LIMIT 1 OFFSET {x};
                                '''
                self.cursor.execute(exec_str)
                subj_id_list.append(self.cursor.fetachall())


            return subj_id_list

        else:
            tbl = conc.get_table()
            exec_str = f'''
                            SELECT COUNT(*) 
                            FROM {tbl};
                            '''
            self.cursor.execute(exec_str)
            num_rows = self.cursor.fetachall()
            rows = random_integers(1,num_rows, POP_N)
            subj_id_list = list
            for x in rows:
                exec_str = f'''
                                            SELECT SUBJECT_ID 
                                            FROM {tbl}
                                            LIMIT 1 OFFSET {x};
                                            '''
                self.cursor.execute(exec_str)
                subj_id_list.append(self.cursor.fetachall())

            return subj_id_list


    def get_rand(self, tbl, n=1000) -> List[List[int]]:
        if n > POP_N:
            raise ValueError(f'Maximum patient count of {POP_N}')
        tmp_ = list(range(POP_N))
        print(tmp_)
        shuffle(tmp_)
        print(tmp_)
        tmp_ = tmp_[0:n]
        exec_str = f'''
                        SELECT SUBJECT_ID 
                        FROM {tbl}
                        WHERE rand_id IN {tuple(tmp_)}
                        LIMIT {n}'''
        # try:
        #     self.cursor.execute(exec_str)
        # except sql.Error as e:
        #     print("Error %d: %s" % (e.args[0], e.args[1]))

        self.cond_list = [row[0] for row in self.cursor.fetchall()]
        print(self.cond_list)

        return self.cond_list


    def get_result(self, conc: ConceptType, target_concept: Tuple[str], n=1000) -> Dict[int, bool]:
        ret_dict = dict()
        neg_count = 0
        pos_count = 0

        for subj_id in self.cond_list:
            print(subj_id)
            neg_count += 1
            exec_str = f'''
                            SELECT {conc.get_field()}
                            FROM {conc.get_table()}
                            WHERE subj_id = {subj_id}
                            AND {conc.get_field()} in {target_concept}'''
            #self.cond_list.cursor.execute(exec_str)
            self.cursor.execute(exec_str)
            #cons = self.cond_db.cursor.fetchall()
            cons = self.cursor.fetchall()

            print(cons)
            if len(cons) > 0:
                neg_count -= 1
                if pos_count < n/2:
                    pos_count = len(cons)
                    ret_dict[subj_id] = {code: 1 for code in cons}
                    print(ret_dict)
            else:
                ret_dict[subj_id] = {code: 0 for code in cons}
                print(ret_dict)

        return ret_dict


#     def main(self):
#         ConditionPopulation.get_rand(self, "DIAGNOSES_ICD", 10)
#
#         input_tuple: Tuple[str] = ("7100")
#         ConditionPopulation.get_result(self, ConceptType("Condition"), input_tuple, 10)
#
# cp = ConditionPopulation()
# if __name__ == "__main__": cp.main()
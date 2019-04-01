from typing import Dict
from operator import itemgetter

from associations.util.db_util import DatabaseHandle
from associations.util.concept_util import Source, ConceptType


class OutputFormat:
    db_handle: DatabaseHandle = None

    def __init__(self, db_handle):
        self.db_handle = db_handle

    def stringify_scores(self, scores: Dict, src: Source, cutoff=10, fname='scores'):
        conc = ConceptType(src.get_type())
        ret_dict = dict()
        for code in scores:
            if scores[code] > cutoff:
                exec_str = f'''SELECT {conc.get_str()}
                                    FROM D_LABITEMS
                                WHERE 
                                    {conc.get_field()} = {code}'''
                self.db_handle.cursor.execute(exec_str)
                ret_dict[self.db_handle.cursor.fetchall()[0][0]] = scores[code]
        sorted_score = sorted(ret_dict.items(),
                              key=itemgetter(1),
                              reverse=True)
        if len(sorted_score) >= 15:
            length = 15
        else:
            length = len(sorted_score)

        with open(f'{fname}.json', 'w+') as handle:
            json.dump(sorted_score[0:length], handle)
        return ret_dict
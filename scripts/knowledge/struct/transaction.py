
class Transaction:

    def __init__(self):
        self.translations = []
    

    def load_translation(self, filepath, reverse=False):
        '''load a concept code translation for convert codes directly

        Note that translations need to loaded in the order that they
        are intended to be applied to the transaction codes.    '''
        
        pass
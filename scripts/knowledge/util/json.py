
import json

from knowledge.util.print import PrintUtil as pr

class JsonUtil():

    @classmethod
    def merge_default(self, load, default):
        merged = {}
        keys = default.keys()        
        for key in load.keys():
            if key not in keys or type(load[key]) is not type(default[key]):
                valid = False
            elif type(load[key]) is dict:
                pass
        

    @classmethod
    def apply_default(self, loadpath, defaultpath):
        with open(loadpath, 'r') as loadfile, open(defaultpath, 'r') as defaultfile:
            pass

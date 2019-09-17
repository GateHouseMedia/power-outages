import os
from multiprocessing import Pool
import config
from os import makedirs

pythonpath = config.pythonpath
powerscripts = config.powerscripts
jsonpath = config.jsonpath

if config.WantJson:
    makedirs(jsonpath, exist_ok=True)   # Build publishing directory if needed

def run_process(process):
    os.system(pythonpath + ' {}'.format(process))
    
if __name__ ==  '__main__':
    pool = Pool(processes=8)
    pool.map(run_process, tuple(powerscripts))
    pool.close()
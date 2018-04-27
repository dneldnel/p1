import json

filename='x10.config'


    # def __init__(self, id='x10'):
    #     self.id=id

def loadConfig(id):
    filename={
        'x10':'x10.config',
        'gb':'gb.config'
    }.get(id,'x10.config')
    with open(filename) as f:
        #print(f.read())
        setting=json.load(f)
        timeout=setting['timeout']
        print(timeout)
    

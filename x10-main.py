import argparse
import json
import signal
import sys
import time
import os
import config as c
import log as Log
import subprocess
import requests

#result{} is the dict for {key,COIN} while key is like 'dgb_qubit'
results = {}

#revs is the dict for {key,rev} e.g. {'dgb_qubit',2.3}
revs={}

#running is the on-off switch   
running=True

#The haproxy path to config
config_path='/etc/haproxy/'

class Coin():
    x10rev=0
    def __init__(self,name,algo,nethash,blockreward,price, blocktime):
        self.name=name
        self.algo=algo
        self.nethash=nethash
        self.blockreward=blockreward
        self.price=price
        self.blocktime=blocktime


coin_json={
    'dgb_qubit': 'http://www.whattomine.com/coins/115.json',
    'dgb_myrgr':'http://www.whattomine.com/coins/112.json',
    'xvg_myrgr': 'http://www.whattomine.com/coins/218.json',
    'bwk_nist5': 'http://www.whattomine.com/coins/224.json',
    'dgb_skein':'http://www.whattomine.com/coins/114.json'
}

#handling system signal
#signal.SIGINT=Ctrl-C
def signal_handler(signal, frame):

    log.info('exiting...')
    # if pool:
    #     pool.shutdown(0)
    #     pool.close()
    # for c in proxies.list():
    #     proxies.del_proxy(c)
    # time.sleep(1)
    # sys.exit(0)
    global running
    running =False

def parse_args():
    parser = argparse.ArgumentParser(
        description='X10 mining auto switch')

    # parser.add_argument(
    #     '-s',
    #     dest='pool',
    #     type=str,
    #     default="mine.magicpool.org",
    #     help='Hostname of stratum mining pool')
    # parser.add_argument(
    #     '-t',
    #     dest='port',
    #     type=int,
    #     default=3333,
    #     help='Port of stratum mining pool')
    # parser.add_argument(
    #     '-u',
    #     dest='username',
    #     type=str,
    #     default="14MQUGn97dFYHGxXwaHqoCX175b9fwYUMo",
    #     help='Username for stratum mining pool ')
    # parser.add_argument(
    #     '-a',
    #     dest='password',
    #     type=str,
    #     default="d=1024",
    #     help='Password for stratum mining pool')
    # parser.add_argument(
    #     '-l',
    #     dest='listen',
    #     type=str,
    #     default='0.0.0.0',
    #     help='IP to listen for incomming connections (miners)')
    # parser.add_argument(
    #     '-p',
    #     dest='listen_port',
    #     type=int,
    #     default=3333,
    #     help='Port to listen on for incoming connections')
    # parser.add_argument(
    #     '-c',
    #     dest='control',
    #     type=str,
    #     default='127.0.0.1',
    #     help='IP to listen for incomming control remote management')
    # parser.add_argument(
    #     '-x',
    #     dest='control_port',
    #     type=int,
    #     default=2222,
    #     help='Control port to listen for orders')
    # parser.add_argument(
    #     '-o',
    #     dest='log',
    #     type=str,
    #     default=None,
    #     help='File to store logs')
    # parser.add_argument(
    #     '-q',
    #     dest='quiet',
    #     action="store_true",
    #     help='Enable quite mode, no stdout output')
    parser.add_argument(
        '-v',
        dest='verbose',
        type=int,
        default=3,
        help='Verbose level from 0 to 4')
    return parser.parse_args()


def get_results():
    global results
    for key in coin_json:
        #print(key,':',coin_json[key])
        d = requests.get(coin_json[key]).json()
        c=Coin(
            d['tag'],
            d['algorithm'],
            d['nethash'],
            d['block_reward24'],
            d['exchange_rate'],
            d['block_time']
        )
        #print(d)
        dailycoins = 60*60*24 * c.blockreward / float(c.blocktime)

        cal = 10000000000 #10g
        if 'skein' in key:
            cal= 5000000000 #5g
        #we calculate in mBTC, so x1000
        c.x10rev = dailycoins / c.nethash * c.price * cal * 1000
        results[key]=c
        revs[key] = c.x10rev
    pass
   # return results

args = parse_args()

signal.signal(signal.SIGINT, signal_handler)

# Set log stuff
Log.verbose = args.verbose
# Log.filename = args.log
# Log.stdout = not args.quiet
log = Log.Log('main')

print('working....')
#c.loadConfig('x10')

current_rev=0
current_algo=''
start_time=time.time()


while(running):
    
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    get_results()
    rev=0
    algo=''

    for k in coin_json.keys():
        c = results[k]
        #rev = revs[k]
        print('Coin: %s Hash(G): %.0f Rev(mSat): %.3f' %(k,c.nethash / 1000000000,c.x10rev))
    
    # print(revs)

    r = sorted(revs.items(),key = lambda x:x[1],reverse = True)
    print(r)

    time_elapsed = time.time()-start_time
    if r[0][1] > r[1][1] * 1.05 and r[0][0] != current_algo:
        current_algo = r[0][0]
        print('Changing algo to ',current_algo , ' prev elapsed:',time_elapsed)
        start_time = time.time()
        file = config_path + current_algo + '.cfg'
        if os.path.exists(file):
            print('using file ' +file)
            status, output = subprocess.getstatusoutput('cp '+file + ' /etc/haproxy/haproxy.cfg')
            if status ==0:
                status, output = subprocess.getstatusoutput('service haproxy restart')
                if status != 0:
                    print('error happens: '+output)
                    running = False
            else:
                    print('error2 happens: '+output)
                    running = False
        else:
            print('error: can not find '+file)
            running = False
    else:
        print('Current algo %s has run for %d secs' %(current_algo, time_elapsed))

    print('')
    time.sleep(10)

log.info('Closed')


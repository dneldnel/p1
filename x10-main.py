import argparse
import json
import signal
import sys
import time

import config as c
import log as Log
import requests


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

    log.info('exit')
    # if pool:
    #     pool.shutdown(0)
    #     pool.close()
    # for c in proxies.list():
    #     proxies.del_proxy(c)
    # time.sleep(1)
    # sys.exit(0)
    running=False

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
    results={}
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
        c.x10rev = dailycoins / c.nethash * c.price * cal



        results[key]=c
    return results

args = parse_args()
shutdown = False
signal.signal(signal.SIGINT, signal_handler)

# Set log stuff
Log.verbose = args.verbose
# Log.filename = args.log
# Log.stdout = not args.quiet
log = Log.Log('main')

print('working....')
#c.loadConfig('x10')



while(True):
    results = get_results()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    for (k,c) in results.items():
#        print("Coin:" , k, "  Nethash(G):",round(c.nethash / 1000000000 , 0) ," x10 rev:",round(c.x10rev,8) )
        print('Coin: %s Hash(G): %.0f Rev(mSat): %.3f' %(k,c.nethash / 1000000000,c.x10rev *1000))

    print('')
    time.sleep(10)



import logging.config
import os
import mysql.connector
from coinpayments import CoinPaymentsAPI
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import base64
import _thread
import time
import datetime
from blockchain import blockexplorer
from icq.bot import ICQBot
from icq.filter import MessageFilter
from icq.handler import (
    MessageHandler, UserAddedToBuddyListHandler, FeedbackCommandHandler, UnknownCommandHandler, CommandHandler
)

cd = os.path.dirname(os.path.abspath(__file__))
aaa = os.path.join(cd, "logging.ini")

conn = mysql.connector.connect(host='localhost', database='bin', user='binbot', password='football!!!')
query_conn = conn.cursor(buffered=True)

NAME = "PLUG_BOT"
VERSION = "0.0.19"
# TOKEN = "001.3907104052.2241892471:747224570"
TOKEN = "001.0843420055.4259868664:747300945"
OWNER = "000000000"

LOG_FILES = False
LOG_DATABASE = True

LOG_PATTERNS = {}

FLAG_USER_BAN = False

TEXT_RESPONSE_LIMIT = 10000

FORMAT_INDENT = 4

START_FLAG = {}
STOP_FLAG = {}

PP_PRICE = 5
DEBIT_PRICE = 30
CREDIT_PRICE = 50
DEAD_FULLZ_PRICE = 5

DEPOSIT_ADDRESS = {}
DEPOSIT_AMOUNT = {}
GBP_PAY_AMOUNT = {}

BIN_TYPE = {}

FULLZ_FLAG = {}
DEAD_FULLZ_FLAG = {}
PP_FLAG = {}
BUY_FLAG = {}
FULLZ_CONFIRM = {}
DEAD_FULLZ_CONFIRM = {}
PP_CONFIRM = {}

FULLZ_NAME = {}
FULLZ_NUM = {}
FULLZ_TYPE = {}

DEAD_FULLZ_NAME = {}
DEAD_FULLZ_NUM = {}
DEAD_FULLZ_TYPE = {}

PP_NUM = {}

bins_list = []
pp_amount = {}
fullz_list = {}
dead_fullz_list = {}

__key__ = hashlib.sha256(b'bin-bot-encrypt!').digest()

def encrypt(raw):
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    raw = base64.b64encode(pad(raw).encode('utf8'))
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key= __key__, mode= AES.MODE_CFB,iv= iv)
    return base64.b64encode(iv + cipher.encrypt(raw))

def decrypt(enc):
    unpad = lambda s: s[:-ord(s[-1:])]

    enc = base64.b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(__key__, AES.MODE_CFB, iv)
    return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))


# log patterns
def log_pattern():
    global LOG_PATTERNS

    LOG_PATTERNS = {}

    try:
        query_conn.execute("select id, content, params from log where 1 ")
        l_list = query_conn.fetchall()

        for ptn in l_list:
            LOG_PATTERNS[ptn[0]] = {'content': '\n'.join(ptn[1].split('\\n')), 'params': ptn[2]}
    except:
        print('log pattern error occurs.')

    return


# chat & log
def log_output(index, command, aimId, flag, result, chats=[], insert_command=True):
    global LOG_FILES, LOG_DATABASE

    time_now = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

    try:
        if LOG_FILES == True:
            sample_text = "index=>%s,time=>%s,command=>%s,aimId=>%s,flag=>%s,result=>%s@#@"
            file_name = "../var/www/html/logs/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".txt"
            result_text = sample_text % (index, datetime.datetime.now().strftime("%H:%M:%S"), command, aimId, flag, result)
            with open(file_name, "a") as log_file:
                log_file.write(result_text)
        
        if LOG_DATABASE == True:
            if insert_command == True:
                query = "insert into `chat` (`uin`, `time`, `log_id`, `log_params`, `command`) values ('%s', '%s', '0', '', '/%s')" % (aimId, time_now, command)
                query_conn.execute(query)
                conn.commit()
            if len(chats) > 0:
                for chat in chats:
                    if len(chat) > 1:
                        query = 'insert into `chat` (`uin`, `time`, `log_id`, `log_params`, `command`) values ("%s", "%s", "%s", "%s", "")' % (aimId, time_now, chat[0], chat[1])
                        query_conn.execute(query)
                        conn.commit()
    except:
        print('log output error occurs.')


def get_coin_info():
    try:
        #api = CoinPaymentsAPI(public_key='a289262d2662321065c8f156d1adac989dd632d3b5f5a38ffef7a8a2d0feaf17', private_key='09a5c13f34b6C5397eEFFCcDe3f5716a2de0CF229a7bbcF8a7cA1335Be84ad96')
        api = CoinPaymentsAPI(public_key='d5c643530e2c861fd66c1ba935eff906af6c09c653e10ec0a3e6f8d9090ca2be',
                              private_key='51C995de635f484210ada1Cc9b6cC300313309f52eA1279BD44b2fac1b6fc1F9')
        coin_address = api.get_callback_address(currency='BTC')['result']['address']
        coin_rate = api.rates()['result']['GBP']['rate_btc']
    except:
        print('get coin info error occurs.')

    return coin_address, coin_rate


# calcualte payment
def calc_payment(source, num=0, pay_amount=-1.0):
    global FULLZ_NAME, FULLZ_NUM, FULLZ_TYPE, DEAD_FULLZ_NAME, DEAD_FULLZ_NUM, DEAD_FULLZ_TYPE, PP_NUM, PP_FLAG, FULLZ_FLAG, DEAD_FULLZ_FLAG, PP_PRICE, CREDIT_PRICE, DEBIT_PRICE, DEAD_FULLZ_PRICE
    
    try:
        if pay_amount < 0.0:
            if PP_FLAG[source]:
                pay_amount = PP_PRICE * int(num)
            elif FULLZ_FLAG[source]:
                if FULLZ_TYPE[source] == "credit":
                    pay_amount = CREDIT_PRICE * int(FULLZ_NUM[source])
                elif FULLZ_TYPE[source] == "debit":
                    pay_amount = DEBIT_PRICE * int(FULLZ_NUM[source])
            elif DEAD_FULLZ_FLAG[source]:
                pay_amount = DEAD_FULLZ_PRICE * int(DEAD_FULLZ_NUM[source])
        
        gbp_pay_amount = pay_amount
        deposit_address, coin_rate = get_coin_info()
        coin_rate = float("{:.5f}".format(float(coin_rate))) + 0.00001
        pay_amount = "{:.5f}".format(float(coin_rate) * pay_amount)
        fee = "{:.5f}".format(float("{:.5f}".format(float(pay_amount) * 0.5 / 100)) + 0.00001)
        total_amount = "{:.5f}".format(float(pay_amount) + float(fee))


        return deposit_address, pay_amount, fee, total_amount, gbp_pay_amount
    except:
        print('calcualte payment error occurs.')


# insert or get user
def process_user(source):
    global FLAG_USER_BAN

    try:
        time_now = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

        # selecte user
        query = "select id, uin, buy_time, ban from `user` where uin=%s order by id desc" % source
        query_conn.execute(query)
        row = query_conn.fetchone()
        if row is not None and len(row) > 0:
            if row[3] == 'Y':
                FLAG_USER_BAN = True
            else:
                FLAG_USER_BAN = False

            # update user
            # query = "update `user` set buy_time='%s' where id=%s" % (time_now, row[0])
            # query_conn.execute(query)
            # conn.commit()
            # update_count = query_conn.rowcount
            # log_output('174', 'user', source, 'success', ('%d update user' % (update_count)), [], False)
        else:
            FLAG_USER_BAN = False

            # insert user
            query = "insert into `user` (`uin`, `buy_time`, `ban`) values ('%s', '%s', 'N')" % (source, time_now)
            query_conn.execute(query)
            conn.commit()
            insert_count = query_conn.rowcount 
            log_output('173', 'user', source, 'success', ('%d insert user' % (insert_count)), [], False)
        
    except:
        print('user process error occurs.')


# insert order
def insert_order(source):
    global BIN_TYPE, DEPOSIT_AMOUNT, GBP_PAY_AMOUNT

    try:
        time_now = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

        # current id of `chat`
        query = "select id from `chat` where uin=%s order by id desc" % source
        query_conn.execute(query)
        row = query_conn.fetchone()
        current_chat_id = row[0]

        if BIN_TYPE[source] == 'Fullz':
            table_name = 'fullz'
        elif BIN_TYPE[source] == 'dead_fullz':
            table_name = 'dead_fullz'
        elif BIN_TYPE[source] == 'PP':
            table_name = 'pp'
        else:
            return

        # insert order
        query = "select id from %s where lock_customer=%s and status='lock'" % (table_name, source)
        query_conn.execute(query)
        f_list = query_conn.fetchall()
        temp_ids = ''
        for f in f_list:
            temp_ids += str(f[0]) + ','
        query = "insert into `order` (`uin`, `time`, `product_type`, `product_id`, `btc`, `gbp`, `success`, `ongoing`, `chat_id`, `canceled`) values ('%s', '%s', '%s', '%s', '%s', '%s', 'N', 'Y', '%s', 'N')" % (source, time_now, table_name, temp_ids, DEPOSIT_AMOUNT[source], GBP_PAY_AMOUNT[source], current_chat_id)
        query_conn.execute(query)
        conn.commit()
    except Exception as e:
        print('insert order error occurs.')
        print(e)


def start_cb():
    # log_output('170', 'start', source, 'success', '', [[37, '']])
    pass

def stop_cb():
    # log_output('171', 'stop', source, 'success', '', [[37, '']])
    pass

def help_cb():
    # log_output('172', 'help', source, 'success', '', [[38, '']])
    pass

def command_cb(bot, event):
    global START_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, PP_CONFIRM, LOG_PATTERNS, FLAG_USER_BAN

    source = event.data["source"]["aimId"]
    START_FLAG[source] = True

    try:
        # process user
        process_user(source)

        if FLAG_USER_BAN == True:
            log_output('181', 'command', source, 'fail', 'ban', [[43, '']])
            message = LOG_PATTERNS[43]['content'] #43
            bot.send_im(target=source, message=message)
            return

        if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
            log_output('168', 'command', source, 'fail', 'not CONFIRM', [[1, '']])
            bot.send_im(target=source, message=LOG_PATTERNS[1]['content']) #1
            return

        log_output('169', 'command', source, 'success', 'command', [[2, '']])
        bot.send_im(target=source, message=LOG_PATTERNS[2]['content']) #2
    except:
        print('command cb error occurs.')


def chat_cb(bot, event):
    global bins_list, BUY_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, PP_CONFIRM, FULLZ_FLAG, DEAD_FULLZ_FLAG, PP_FLAG, fullz_list, dead_fullz_list, pp_amount, DEPOSIT_ADDRESS, DEPOSIT_AMOUNT, BIN_TYPE, PP_NUM, FLAG_USER_BAN

    source = event.data["source"]["aimId"]
    if source not in START_FLAG:
        START_FLAG[source] = True
        BUY_FLAG[source] = False
        FULLZ_CONFIRM[source] = False
        DEAD_FULLZ_CONFIRM[source] = False
        PP_CONFIRM[source] = False
        FULLZ_FLAG[source] = False
        DEAD_FULLZ_FLAG[source] = False
        PP_FLAG[source] = False
        fullz_list[source] = []
        dead_fullz_list[source] = []
        pp_amount[source] = ""
        bins_list = []
        DEPOSIT_ADDRESS[source] = ""
        DEPOSIT_AMOUNT[source] = ""
        BIN_TYPE[source] = ""
        PP_NUM[source] = ""

    # process user
    process_user(source)
    command = event.data["message"].strip()
    
    if FLAG_USER_BAN == True:
        log_output('182', command, source, 'fail', 'ban', [[43, '']])
        message = LOG_PATTERNS[43]['content'] #43
        bot.send_im(target=source, message=message)
        return

    if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
        log_output('165', command, source, 'fail', 'not CONFIRM', [[1, '']])
        message = LOG_PATTERNS[1]['content'] #1
    elif FULLZ_FLAG[source] or DEAD_FULLZ_FLAG[source] or PP_FLAG[source] or BUY_FLAG[source]:
        BUY_FLAG[source], FULLZ_FLAG[source], DEAD_FULLZ_FLAG[source], PP_FLAG[source] = False, False, False, False
        log_output('166', command, source, 'fail', 'BUY_FLAG', [[3, '']])
        message = LOG_PATTERNS[3]['content'] #3
    else:
        log_output('167', command, source, 'success', 'chat', [[4, '']])
        message = LOG_PATTERNS[4]['content'] #4
    bot.send_im(target=source, message=message)


def bins_cb(bot, event):
    global bins_list, BUY_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, PP_CONFIRM, FULLZ_FLAG, DEAD_FULLZ_FLAG, PP_FLAG, fullz_list, dead_fullz_list, pp_amount, DEPOSIT_ADDRESS, DEPOSIT_AMOUNT, BIN_TYPE, PP_NUM, FLAG_USER_BAN

    result_list = []
    result_text = ""
    source = event.data["source"]["aimId"]

    # process user
    process_user(source)
    
    if FLAG_USER_BAN == True:
        log_output('180', 'bins', source, 'fail', 'ban', [[43, '']])
        message = LOG_PATTERNS[43]['content'] #43
        bot.send_im(target=source, message=message)
        return
    
    if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
        log_output('162', 'bins', source, 'fail', 'not CONFIRM', [[1, '']])
        message = LOG_PATTERNS[1]['content'] #1
        bot.send_im(target=source, message=message)
        return

    START_FLAG[source] = True
    BUY_FLAG[source] = False
    #FULLZ_CONFIRM[source] = False
    PP_CONFIRM[source] = False
    #FULLZ_FLAG[source] = False
    PP_FLAG[source] = False
    fullz_list[source] = []
    dead_fullz_list[source] = []
    pp_amount[source] = ""
    bins_list = []
    DEPOSIT_ADDRESS[source] = ""
    DEPOSIT_AMOUNT[source] = ""
    BIN_TYPE[source] = ""
    PP_NUM[source] = ""
    #if FULLZ_CONFIRM[source] or PP_CONFIRM[source]:
    #    message = "(INVALID COMMAND) Please only use commands /confirm and /cancel please note that if you have already paid and you cancel you will lose your product.\nPlease type /cancel if you want to cancel your current purchase."#1
    #    bot.send_im(target=source, message=message)
    #    return

    try:
        query_conn.execute("select card_bin, type from fullz where status='on'")
        bin_list = query_conn.fetchall()
        for index, bin in enumerate(bin_list):
            bin1 = decrypt(bin[0]).replace("| Card BIN : ", "")
            result_text += bin1.replace("\n", "") +"(" + decrypt(bin[1]) + ")\n"
            result_list.append(bin1.replace("\n", ""))
        
        if result_text == "":
            log_output('164', 'bins', source, 'fail', 'none fullz', [[41, '']])
            result_text = LOG_PATTERNS[41]['content'] #41
        else:
            log_output('163', 'bins', source, 'success', ('bin=%s' % bin1.replace("\n", "")), [[0, result_text]])
        bot.send_im(target=source, message=result_text)
    except:
        print('bin cb error occurs.')


def buy_cb(bot, event):
    global DEPOSIT_AMOUNT, DEPOSIT_ADDRESS, BIN_TYPE, BUY_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, PP_CONFIRM, FULLZ_FLAG, DEAD_FULLZ_FLAG, PP_FLAG, PP_NUM, fullz_list, dead_fullz_list, pp_amount, bins_list, FLAG_USER_BAN

    source = event.data["source"]["aimId"]
    time_now = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
    if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
        log_output('160', 'buy', source, 'fail', 'not CONFIRM', [[1, '']])
        message = LOG_PATTERNS[1]['content'] #1
        bot.send_im(target=source, message=message)
        return

    START_FLAG[source] = True
    BUY_FLAG[source] = True
    FULLZ_CONFIRM[source] = False
    DEAD_FULLZ_CONFIRM[source] = False
    PP_CONFIRM[source] = False
    FULLZ_FLAG[source] = False
    DEAD_FULLZ_FLAG[source] = False
    PP_FLAG[source] = False
    fullz_list[source] = []
    dead_fullz_list[source] = []
    pp_amount[source] = ""
    bins_list = []
    DEPOSIT_ADDRESS[source] = ""
    DEPOSIT_AMOUNT[source] = ""
    BIN_TYPE[source] = ""
    PP_NUM[source] = ""

    try:

        # process user
        process_user(source)

        if FLAG_USER_BAN == True:
            log_output('179', 'buy', source, 'fail', 'ban', [[43, '']])
            message = LOG_PATTERNS[43]['content'] #43
            bot.send_im(target=source, message=message)
            return

        query = "update fullz set status='on', lock_time=0, lock_customer='' where status='lock' and lock_customer=%s" % source
        query_conn.execute(query)
        conn.commit()
        update_count1 = query_conn.rowcount
        query = "update dead_fullz set status='on', lock_time=0, lock_customer='' where status='lock' and lock_customer=%s" % source
        query_conn.execute(query)
        conn.commit()
        update_count2 = query_conn.rowcount
        query = "update pp set status='on', lock_time=0, lock_customer='' where status='lock' and lock_customer=%s" % source
        query_conn.execute(query)
        conn.commit()
        update_count3 = query_conn.rowcount
        log_output('161', 'buy', source, 'success', ('%d update fullz %d update dead_fullz %d update pp' % (update_count1, update_count2, update_count3)), [[42, str(update_count1)+'###'+str(update_count2)+'###'+str(update_count3)]])
        message = LOG_PATTERNS[42]['content'] #42
        bot.send_im(target=source, message=message)
    except:
        print('buy cb error occurs.')

def pp_cb(bot, event):
    global BUY_FLAG, PP_FLAG, PP_CONFIRM, PP_NUM, FULLZ_FLAG, DEAD_FULLZ_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, FLAG_USER_BAN

    source = event.data["source"]["aimId"]
    PP_NUM[source] = "0"

    try:

        # process user
        process_user(source)
        
        if FLAG_USER_BAN == True:
            log_output('178', 'pp', source, 'fail', 'ban', [[43, '']])
            message = LOG_PATTERNS[43]['content'] #43
            bot.send_im(target=source, message=message)
            return

        if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
            log_output('153', 'pp', source, 'fail', 'not CONFIRM', [[1, '']])
            message = LOG_PATTERNS[1]['content'] #1
            bot.send_im(target=source, message=message)
            return
        elif FULLZ_FLAG[source]:
            log_output('154', 'pp', source, 'fail', 'FULLZ_FLAG', [[5, '']])
            message = LOG_PATTERNS[5]['content'] #5
            bot.send_im(target=source, message=message)
        elif DEAD_FULLZ_FLAG[source]:
            log_output('155', 'pp', source, 'fail', 'DEAD_FULLZ_FLAG', [[6, '']])
            message = LOG_PATTERNS[6]['content'] #6
            bot.send_im(target=source, message=message)
        else:
            if source in BUY_FLAG:
                if BUY_FLAG[source]:
                    PP_FLAG[source] = True
                    query_conn.execute("select email, password from pp where status='on'")
                    pp_list = query_conn.fetchall()
                    if pp_list == []:
                        log_output('156', 'pp', source, 'fail', 'none pp', [[7, '']])
                        message = LOG_PATTERNS[7]['content'] #7
                    else:
                        PP_NUM[source] = str(len(pp_list))
                        log_output('157', 'pp', source, 'success', 'pp_list', [[8, str(PP_NUM[source])]])
                        message = LOG_PATTERNS[8]['content']  % PP_NUM[source] #8
                    BUY_FLAG[source] = False
                    bot.send_im(target=source, message=message)
                else:
                    log_output('158', 'pp', source, 'fail', 'not BUY_FLAG', [[9, '']])
                    message = LOG_PATTERNS[9]['content'] #9
                    bot.send_im(target=source, message=message)
            else:
                log_output('159', 'pp', source, 'fail', 'not BUY_FLAG', [[9, '']])
                message = LOG_PATTERNS[9]['content'] #9
                bot.send_im(target=source, message=message)
    except:
        print('pp cb error occurs.')

def fullz_cb(bot, event):
    global BUY_FLAG, PP_FLAG, PP_CONFIRM, PP_NUM, FULLZ_FLAG, DEAD_FULLZ_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, bins_list, FLAG_USER_BAN

    source = event.data["source"]["aimId"]

    try:

        # process user
        process_user(source)
        
        if FLAG_USER_BAN == True:
            log_output('177', 'fullz', source, 'fail', 'ban', [[43, '']])
            message = LOG_PATTERNS[43]['content'] #43
            bot.send_im(target=source, message=message)
            return

        if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
            log_output('146', 'fullz', source, 'fail', 'not CONFIRM', [[1, '']])
            message = LOG_PATTERNS[1]['content'] #1
            bot.send_im(target=source, message=message)
            return
        if PP_FLAG[source]:
            log_output('147', 'fullz', source, 'fail', 'PP_FLAG', [[10, '']])
            message = LOG_PATTERNS[10]['content'] #10
            bot.send_im(target=source, message=message)
        elif DEAD_FULLZ_FLAG[source]:
            log_output('148', 'fullz', source, 'fail', 'DEAD_FULLZ_FLAG', [[11, '']])
            message = LOG_PATTERNS[11]['content'] #11
            bot.send_im(target=source, message=message)
        else:
            if source in BUY_FLAG:
                if BUY_FLAG[source]:
                    FULLZ_FLAG[source] = True
                    bins_list = []
                    result_list = []
                    result_text = LOG_PATTERNS[12]['content'] #12
                    query_conn.execute("select card_bin, type from fullz where status='on'")
                    bin_list = query_conn.fetchall()
                    if bin_list == []:
                        log_output('149', 'fullz', source, 'fail', 'none fullz', [[13, '']])
                        message = LOG_PATTERNS[13]['content'] #13
                        bot.send_im(target=source, message=message)
                    else:
                        for index, bin in enumerate(bin_list):
                            bin_name = decrypt(bin[0]).replace("| Card BIN : ", "")
                            bin_type = decrypt(bin[1])
                            result_list.append([bin_name.replace("\n", ""), bin_type])
                        for bin in result_list:
                            temp1 = bin[0] + "X" + str(result_list.count(bin))
                            # temp2 = [bin, result_list.count(bin)]
                            temp2 = [bin[0], bin[1], result_list.count(bin)]
                            if temp2 not in bins_list:
                                bins_list.append(temp2)
                                result_text += temp1 + "\n"
                            BUY_FLAG[source] = False
                        log_output('150', 'fullz', source, 'success', result_text, [[0, result_text]])
                        bot.send_im(target=source, message=result_text)

                else:
                    log_output('151', 'fullz', source, 'fail', 'not BUY_FLAG', [[14, '']])
                    message = LOG_PATTERNS[14]['content'] #14
                    bot.send_im(target=source, message=message)
            else:
                log_output('152', 'fullz', source, 'fail', 'not BUY_FLAG', [[14, '']])
                message = LOG_PATTERNS[14]['content'] #14
                bot.send_im(target=source, message=message)
    except:
        print('fullz cb error occurs.')

def dead_fullz_cb(bot, event):
    global BUY_FLAG, PP_FLAG, PP_CONFIRM, PP_NUM, FULLZ_FLAG, DEAD_FULLZ_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, bins_list, FLAG_USER_BAN

    source = event.data["source"]["aimId"]

    try:

        # process user
        process_user(source)
        
        if FLAG_USER_BAN == True:
            log_output('176', 'dead_fullz', source, 'fail', 'ban', [[43, '']])
            message = LOG_PATTERNS[43]['content'] #43
            bot.send_im(target=source, message=message)
            return

        if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
            log_output('141', 'dead_fullz', source, 'fail', 'not CONFIRM', [[1, '']])
            message = LOG_PATTERNS[1]['content'] #1
            bot.send_im(target=source, message=message)
            return
        if PP_FLAG[source]:
            log_output('142', 'dead_fullz', source, 'fail', 'PP_FLAG', [[15, '']])
            message = LOG_PATTERNS[15]['content'] #15
            bot.send_im(target=source, message=message)
        elif FULLZ_FLAG[source]:
            log_output('143', 'dead_fullz', source, 'fail', 'FULLZ_FLAG', [[16, '']])
            message = LOG_PATTERNS[16]['content'] #16
            bot.send_im(target=source, message=message)
        else:
            if source in BUY_FLAG:
                if BUY_FLAG[source]:
                    DEAD_FULLZ_FLAG[source] = True
                    bins_list = []
                    result_list = []
                    result_text = LOG_PATTERNS[17]['content'] #17
                    query_conn.execute("select card_bin, type from dead_fullz where status='on'")
                    bin_list = query_conn.fetchall()
                    if bin_list == []:
                        log_output('144', 'dead_fullz', source, 'fail', 'none dead_fullz', [[18, '']])
                        message = LOG_PATTERNS[18]['content'] #18
                        bot.send_im(target=source, message=message)
                    else:
                        for index, bin in enumerate(bin_list):
                            bin_name = decrypt(bin[0]).replace("| Card BIN : ", "")
                            bin_type = decrypt(bin[1])
                            result_list.append([bin_name.replace("\n", ""), bin_type])
                        for bin in result_list:
                            temp1 = bin[0] + "X" + str(result_list.count(bin))
                            # temp2 = [bin, result_list.count(bin)]
                            temp2 = [bin[0], bin[1], result_list.count(bin)]
                            if temp2 not in bins_list:
                                bins_list.append(temp2)
                                result_text += temp1 + "\n"
                            BUY_FLAG[source] = False
                        log_output('145', 'dead_fullz', source, 'success', result_text, [[0, result_text]])
                        bot.send_im(target=source, message=result_text)

                else:
                    log_output('140', 'dead_fullz', source, 'fail', 'not BUY_FLAG', [[19, '']])
                    message = LOG_PATTERNS[19]['content'] #19
                    bot.send_im(target=source, message=message)
            else:
                log_output('139', 'dead_fullz', source, 'fail', 'not BUY_FLAG', [[19, '']])
                message = LOG_PATTERNS[19]['content'] #19
                bot.send_im(target=source, message=message)
    except:
        print('dead fullz cb error occurs.')

def unknown_cb(bot, event):
    global bins_list, fullz_list, dead_fullz_list, pp_amount, FULLZ_NAME, FULLZ_NUM, FULLZ_TYPE, DEAD_FULLZ_NAME, DEAD_FULLZ_NUM, DEAD_FULLZ_TYPE, PP_NUM, PP_FLAG, FULLZ_FLAG, DEAD_FULLZ_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, PP_CONFIRM, GBP_PAY_AMOUNT, PP_PRICE, CREDIT_PRICE, DEBIT_PRICE, DEAD_FULLZ_PRICE, FLAG_USER_BAN

    source = event.data["source"]["aimId"]
    fullz_list[source] = []
    dead_fullz_list[source] = []
    FULLZ_NAME[source] = ""
    FULLZ_NUM[source] = ""
    FULLZ_TYPE[source] = ""
    DEAD_FULLZ_NAME[source] = ""
    DEAD_FULLZ_NUM[source] = ""
    DEAD_FULLZ_TYPE[source] = ""
    message = ""
    note_text = LOG_PATTERNS[20]['content'] #20
    confirm_text = LOG_PATTERNS[21]['content'] #21
    command = event.data["message"].strip()
    command_string = command[1:]


    try:

        # process user
        process_user(source)
        
        if FLAG_USER_BAN == True:
            log_output('175', command_string, source, 'fail', 'ban', [[43, '']])
            message = LOG_PATTERNS[43]['content'] #43
            bot.send_im(target=source, message=message)
            return

        if (source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]) or (source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]) or (source in PP_CONFIRM and PP_CONFIRM[source]):
            log_output('101', command_string, source, 'fail', 'not CONFIRM', [[1, '']])
            message = LOG_PATTERNS[1]['content'] #1
            bot.send_im(target=source, message=message)
            return

        if source not in START_FLAG:
            START_FLAG[source] = True
            BUY_FLAG[source] = False
            FULLZ_CONFIRM[source] = False
            DEAD_FULLZ_CONFIRM[source] = False
            PP_CONFIRM[source] = False
            FULLZ_FLAG[source] = False
            DEAD_FULLZ_FLAG[source] = False
            PP_FLAG[source] = False
            fullz_list[source] = []
            dead_fullz_list[source] = []
            pp_amount[source] = ""
            bins_list = []
            DEPOSIT_ADDRESS[source] = ""
            DEPOSIT_AMOUNT[source] = ""
            GBP_PAY_AMOUNT[source] = ""
            BIN_TYPE[source] = ""
            PP_NUM[source] = ""
            message = LOG_PATTERNS[22]['content'] #22
        else:
            if PP_FLAG[source]:
                num = command[1:]
                try:
                    if num == "0" or num == "":
                        log_output('102', command_string, source, 'fail', 'pp num=0', [[23, '']])
                        message = LOG_PATTERNS[23]['content'] #23
                    elif int(num) > int(PP_NUM[source]):
                        log_output('103', command_string, source, 'fail', 'pp num>PP_NUM', [[23, '']])
                        message = LOG_PATTERNS[23]['content'] #23
                    elif int(num) <= int(PP_NUM[source]):
                        query_conn.execute("select id from pp where status='on'")
                        a_list = query_conn.fetchall()
                        for i in range(int(num)):
                            p_id = a_list[i][0]
                            lock_time = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
                            query = "update pp set status='lock', lock_time=%s, lock_customer=%s where id=%s" % (
                                lock_time, source, p_id)
                            query_conn.execute(query)
                            conn.commit()
                            update_count = query_conn.rowcount
                            log_output('104', command_string, source, 'success', ('%d update pp status=lock where id=%s' % (update_count, p_id)), [], False)
                        
                        deposit_address, pay_amount, fee, total_amount, gbp_pay_amount = calc_payment(source, num)

                        # message = "Deposit Address: %s\nDeposit Amount: %s" % (deposit_address, str(pay_amount))
                        message = LOG_PATTERNS[24]['content']  % (deposit_address, str(pay_amount), str(fee), str(total_amount), confirm_text, note_text) #24
                        log_output('105', command_string, source, 'success', message, [[0, message]])
                        pp_amount[source] = num
                        PP_FLAG[source] = False
                        BIN_TYPE[source] = "PP"
                        DEPOSIT_ADDRESS[source] = deposit_address
                        DEPOSIT_AMOUNT[source] = total_amount
                        GBP_PAY_AMOUNT[source] = gbp_pay_amount
                        PP_CONFIRM[source] = True
                        insert_order(source)
                    else:
                        log_output('106', command_string, source, 'fail', 'not pp', [[25, '']])
                        message = LOG_PATTERNS[25]['content'] #25
                except:
                    log_output('107', command_string, source, 'fail', 'not pp', [[25, '']])
                    message = LOG_PATTERNS[25]['content'] #25
            elif FULLZ_FLAG[source]:
                bin = ""
                num = ""
                if "\n" in command or command.count("/") > 1:
                    pay_amount = 0.0
                    command = command.replace("\n", "")
                    command_list = command.split("/")
                    command_list.remove("")
                    message_temp1 = ""
                    for item in command_list:
                        message_temp = ""
                        FULLZ_NUM[source] = ""
                        FULLZ_TYPE[source] = ""
                        FULLZ_NAME[source] = ""
                        if "x" in item:
                            bin = item[: item.index("x")].replace(" ", "")
                            num = item[item.index("x") + 1:]
                        elif "X" in item:
                            bin = item[: item.index("X")].replace(" ", "")
                            num = item[item.index("X") + 1:]
                        else:
                            # message = "There is no amount of BIN.\nPlease set the amount of BIN correctly."
                            bin = item[:]
                            num = "0"

                        for item in bins_list:
                            if item[0] == bin:
                                if num == "0":
                                    log_output('108', command_string, source, 'fail', 'fullz num=0', [], False)
                                    message_temp = LOG_PATTERNS[26]['content']  % (bin, bin) #26
                                elif int(num) > int(item[2]):
                                    log_output('109', command_string, source, 'fail', 'fullz num>BIN_amount', [], False)
                                    message_temp = LOG_PATTERNS[27]['content']  % bin #27
                                else:
                                    FULLZ_NAME[source] = bin
                                    FULLZ_NUM[source] = num
                                    FULLZ_TYPE[source] = item[1]
                        if FULLZ_NAME[source] == "" or FULLZ_NUM[source] == "" or FULLZ_TYPE[source] == "":
                            if message_temp == "":
                                log_output('110', command_string, source, 'fail', 'not fullz', [], False)
                                message_temp1 = LOG_PATTERNS[28]['content'] #28
                                # message_temp1 = message_temp
                        else:
                            lock_num = 0
                            query_conn.execute("select id, card_bin from fullz where status='on'")
                            f_list = query_conn.fetchall()
                            for f in f_list:
                                bin_name = decrypt(f[1]).replace("| Card BIN : ", "").replace("\n", "")
                                bin_id = f[0]
                                if bin_name == FULLZ_NAME[source]:
                                    lock_time = int(
                                        (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
                                    query = "update fullz set status='lock', lock_time=%s, lock_customer=%s where id=%s" % (
                                    lock_time, source, bin_id)
                                    query_conn.execute(query)
                                    conn.commit()
                                    update_count = query_conn.rowcount
                                    log_output('120', command_string, source, 'success', ('%d update fullz status=lock where id=%s' % (update_count, bin_id)), [], False)
                                    lock_num += 1
                                if lock_num == int(FULLZ_NUM[source]):
                                    break
                            if FULLZ_TYPE[source] == "credit":
                                pay_amount_temp = CREDIT_PRICE * int(FULLZ_NUM[source])
                            elif FULLZ_TYPE[source] == "debit":
                                pay_amount_temp = DEBIT_PRICE * int(FULLZ_NUM[source])
                            pay_amount += float(pay_amount_temp)
                            fullz_list[source].append([FULLZ_NAME[source], FULLZ_NUM[source]])
                    if pay_amount > 0.0:
                        deposit_address, pay_amount, fee, total_amount, gbp_pay_amount = calc_payment(source, 0, pay_amount)

                        message = LOG_PATTERNS[29]['content']  % (deposit_address, str(pay_amount), str(fee), str(total_amount), confirm_text, note_text, message_temp1) #29
                        log_output('121', command_string, source, 'success', message, [[0, message]])
                        FULLZ_FLAG[source] = False
                        FULLZ_CONFIRM[source] = True
                        BIN_TYPE[source] = "Fullz"
                        DEPOSIT_ADDRESS[source] = deposit_address
                        DEPOSIT_AMOUNT[source] = total_amount
                        GBP_PAY_AMOUNT[source] = gbp_pay_amount
                        insert_order(source)
                    else:
                        log_output('122', command_string, source, 'fail', 'not fullz', [[30, '']])
                        message = LOG_PATTERNS[30]['content'] #30
                else:
                    if "x" in command:
                        bin = command[1: command.index("x")].replace(" ", "")
                        num = command[command.index("x") + 1:]
                    elif "X" in command:
                        bin = command[1: command.index("X")].replace(" ", "")
                        num = command[command.index("X") + 1:]
                    else:
                        # message = "There is no amount of BIN.\nPlease set the amount of BIN correctly."
                        bin = command[1:]
                        num = "0"

                    for item in bins_list:
                        if item[0] == bin:
                            if num == "0":
                                log_output('123', command_string, source, 'fail', 'fullz num=0', [[26, '']])
                                message = LOG_PATTERNS[26]['content'] #26
                            elif int(num) > int(item[2]):
                                log_output('124', command_string, source, 'fail', 'fullz num>BIN_amount', [[27, '']])
                                message = LOG_PATTERNS[27]['content'] #27
                            else:
                                FULLZ_NAME[source] = bin
                                FULLZ_NUM[source] = num
                                FULLZ_TYPE[source] = item[1]
                    if FULLZ_NAME[source] == "" or FULLZ_NUM[source] == "" or FULLZ_TYPE[source] == "":
                        if message == "":
                            log_output('125', command_string, source, 'fail', 'not fullz', [[22, '']])
                            message = LOG_PATTERNS[22]['content'] #22
                    else:
                        lock_num = 0
                        query_conn.execute("select id, card_bin from fullz where status='on'")
                        f_list = query_conn.fetchall()
                        for f in f_list:
                            bin_name = decrypt(f[1]).replace("| Card BIN : ", "").replace("\n", "")
                            bin_id = f[0]
                            if bin_name == FULLZ_NAME[source]:
                                lock_time = int(
                                    (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
                                query = "update fullz set status='lock', lock_time=%s, lock_customer=%s where id=%s" % (
                                lock_time, source, bin_id)
                                query_conn.execute(query)
                                conn.commit()
                                update_count = query_conn.rowcount
                                log_output('126', command_string, source, 'success', ('%d update fullz status=lock where id=%s' % (update_count, bin_id)), [], False)
                                lock_num += 1
                            if lock_num == int(FULLZ_NUM[source]):
                                break

                        deposit_address, pay_amount, fee, total_amount, gbp_pay_amount = calc_payment(source)

                        message = LOG_PATTERNS[24]['content']  % (deposit_address, str(pay_amount), str(fee), str(total_amount), confirm_text, note_text) #24
                        log_output('127', command_string, source, 'success', message, [[0, message]])
                        fullz_list[source].append([FULLZ_NAME[source], FULLZ_NUM[source]])
                        FULLZ_FLAG[source] = False
                        FULLZ_CONFIRM[source] = True
                        BIN_TYPE[source] = "Fullz"
                        DEPOSIT_ADDRESS[source] = deposit_address
                        DEPOSIT_AMOUNT[source] = total_amount
                        GBP_PAY_AMOUNT[source] = gbp_pay_amount
                        insert_order(source)
            elif DEAD_FULLZ_FLAG[source]:
                bin = ""
                num = ""
                if "\n" in command or command.count("/") > 1:
                    pay_amount = 0.0
                    command = command.replace("\n", "")
                    command_list = command.split("/")
                    command_list.remove("")
                    message_temp1 = ""
                    for item in command_list:
                        message_temp = ""
                        DEAD_FULLZ_NUM[source] = ""
                        DEAD_FULLZ_TYPE[source] = ""
                        DEAD_FULLZ_NAME[source] = ""
                        if "x" in item:
                            bin = item[: item.index("x")].replace(" ", "")
                            num = item[item.index("x") + 1:]
                        elif "X" in item:
                            bin = item[: item.index("X")].replace(" ", "")
                            num = item[item.index("X") + 1:]
                        else:
                            # message = "There is no amount of BIN.\nPlease set the amount of BIN correctly."
                            bin = item[:]
                            num = "0"

                        for item in bins_list:
                            if item[0] == bin:
                                if num == "0":
                                    log_output('128', command_string, source, 'fail', 'dead_fullz num=0', [], False)
                                    message_temp = LOG_PATTERNS[26]['content']  % (bin, bin) #26
                                elif int(num) > int(item[2]):
                                    log_output('129', command_string, source, 'fail', 'dead_fullz num>BIN_amount', [], False)
                                    message_temp = LOG_PATTERNS[27]['content']  % bin #27
                                else:
                                    DEAD_FULLZ_NAME[source] = bin
                                    DEAD_FULLZ_NUM[source] = num
                                    DEAD_FULLZ_TYPE[source] = item[1]
                        if DEAD_FULLZ_NAME[source] == "" or DEAD_FULLZ_NUM[source] == "" or DEAD_FULLZ_TYPE[source] == "":
                            if message_temp == "":
                                log_output('130', command_string, source, 'fail', 'not dead_fullz', [], False)
                                message_temp1 = LOG_PATTERNS[28]['content'] #28
                                # message_temp1 = message_temp
                        else:
                            lock_num = 0
                            query_conn.execute("select id, card_bin from dead_fullz where status='on'")
                            f_list = query_conn.fetchall()
                            for f in f_list:
                                bin_name = decrypt(f[1]).replace("| Card BIN : ", "").replace("\n", "")
                                bin_id = f[0]
                                if bin_name == DEAD_FULLZ_NAME[source]:
                                    lock_time = int(
                                        (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
                                    query = "update dead_fullz set status='lock', lock_time=%s, lock_customer=%s where id=%s" % (
                                    lock_time, source, bin_id)
                                    query_conn.execute(query)
                                    conn.commit()
                                    update_count = query_conn.rowcount
                                    log_output('131', command_string, source, 'success', ('%d update dead_fullz status=lock where id=%s' % (update_count, bin_id)), [], False)
                                    lock_num += 1
                                if lock_num == int(DEAD_FULLZ_NUM[source]):
                                    break
                            pay_amount_temp = DEAD_FULLZ_PRICE * int(DEAD_FULLZ_NUM[source])
                            pay_amount += float(pay_amount_temp)
                            dead_fullz_list[source].append([DEAD_FULLZ_NAME[source], DEAD_FULLZ_NUM[source]])
                    if pay_amount > 0.0:
                        deposit_address, pay_amount, fee, total_amount, gbp_pay_amount = calc_payment(source, 0, pay_amount)

                        message = LOG_PATTERNS[29]['content']  % (deposit_address, str(pay_amount), str(fee), str(total_amount), confirm_text, note_text, message_temp1) #29
                        log_output('132', command_string, source, 'success', message, [[0, message]])
                        DEAD_FULLZ_FLAG[source] = False
                        DEAD_FULLZ_CONFIRM[source] = True
                        BIN_TYPE[source] = "dead_fullz"
                        DEPOSIT_ADDRESS[source] = deposit_address
                        DEPOSIT_AMOUNT[source] = total_amount
                        GBP_PAY_AMOUNT[source] = gbp_pay_amount
                        insert_order(source)
                    else:
                        log_output('133', command_string, source, 'fail', 'not dead_fullz', [[30, '']])
                        message = LOG_PATTERNS[30]['content'] #30
                else:
                    if "x" in command:
                        bin = command[1: command.index("x")].replace(" ", "")
                        num = command[command.index("x") + 1:]
                    elif "X" in command:
                        bin = command[1: command.index("X")].replace(" ", "")
                        num = command[command.index("X") + 1:]
                    else:
                        # message = "There is no amount of BIN.\nPlease set the amount of BIN correctly."
                        bin = command[1:]
                        num = "0"

                    for item in bins_list:
                        if item[0] == bin:
                            if num == "0":
                                log_output('134', command_string, source, 'fail', 'dead_fullz num=0', [[31, '']])
                                message = LOG_PATTERNS[31]['content'] #31
                            elif int(num) > int(item[2]):
                                log_output('135', command_string, source, 'fail', 'dead_fullz num>BIN_amount', [[32, '']])
                                message = LOG_PATTERNS[32]['content'] #32
                            else:
                                DEAD_FULLZ_NAME[source] = bin
                                DEAD_FULLZ_NUM[source] = num
                                DEAD_FULLZ_TYPE[source] = item[1]
                    if DEAD_FULLZ_NAME[source] == "" or DEAD_FULLZ_NUM[source] == "" or DEAD_FULLZ_TYPE[source] == "":
                        if message == "":
                            log_output('136', command_string, source, 'fail', 'not dead_fullz', [[25, '']])
                            message = LOG_PATTERNS[25]['content'] #25
                    else:
                        lock_num = 0
                        query_conn.execute("select id, card_bin from dead_fullz where status='on'")
                        f_list = query_conn.fetchall()
                        for f in f_list:
                            bin_name = decrypt(f[1]).replace("| Card BIN : ", "").replace("\n", "")
                            bin_id = f[0]
                            if bin_name == DEAD_FULLZ_NAME[source]:
                                lock_time = int(
                                    (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
                                query = "update dead_fullz set status='lock', lock_time=%s, lock_customer=%s where id=%s" % (
                                lock_time, source, bin_id)
                                query_conn.execute(query)
                                conn.commit()
                                update_count = query_conn.rowcount
                                log_output('137', command_string, source, 'success', ('%d update dead_fullz status=lock where id=%s' % (update_count, bin_id)), [], False)
                                lock_num += 1
                            if lock_num == int(DEAD_FULLZ_NUM[source]):
                                break
                        
                        deposit_address, pay_amount, fee, total_amount, gbp_pay_amount = calc_payment(source)

                        message = LOG_PATTERNS[24]['content'] % (deposit_address, str(pay_amount), str(fee), str(total_amount), confirm_text, note_text) #24
                        log_output('138', command_string, source, 'success', message, [[0, message]])
                        dead_fullz_list[source].append([DEAD_FULLZ_NAME[source], DEAD_FULLZ_NUM[source]])
                        DEAD_FULLZ_FLAG[source] = False
                        DEAD_FULLZ_CONFIRM[source] = True
                        BIN_TYPE[source] = "dead_fullz"
                        DEPOSIT_ADDRESS[source] = deposit_address
                        DEPOSIT_AMOUNT[source] = total_amount
                        GBP_PAY_AMOUNT[source] = gbp_pay_amount
                        insert_order(source)
            else:
                log_output('111', command_string, source, 'fail', 'not START_FLAG not FLAG', [[22, '']])
                message = LOG_PATTERNS[22]['content'] #22
    except:
        print('unknown cb error occurs.')

    bot.send_im(target=source, message=message)


def confirm_cb(bot, event):
    global FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, PP_CONFIRM, fullz_list, dead_fullz_list, pp_amount, DEPOSIT_ADDRESS, DEPOSIT_AMOUNT, GBP_PAY_AMOUNT, BIN_TYPE, FLAG_USER_BAN

    source = event.data["source"]["aimId"]
    result_text = ""
    amount = 0
    time_now = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

    try:

        # process user
        process_user(source)

        if FLAG_USER_BAN == True:
            log_output('185', 'confirm', source, 'fail', 'ban', [[43, '']])
            message = LOG_PATTERNS[43]['content'] #43
            bot.send_im(target=source, message=message)
            return

        if source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]:
            confirm_time = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

            query = "update fullz set status='confirm', lock_time=%s, deposit_address='%s' where lock_customer=%s and status='lock'" % (confirm_time, DEPOSIT_ADDRESS[source], source)
            query_conn.execute(query)
            conn.commit()
            update_count = query_conn.rowcount
            
            query = "insert into `deposit` (`bin_type`,`deposit_address`, `deposit_amount`,`uin`, `start_time`) values ('%s', '%s', '%s', '%s', '%s')" % (BIN_TYPE[source], DEPOSIT_ADDRESS[source], DEPOSIT_AMOUNT[source], source, time_now)
            query_conn.execute(query)
            conn.commit()
            insert_count = query_conn.rowcount
            
            FULLZ_FLAG[source], FULLZ_CONFIRM[source] = False, False
            log_output('112', 'confirm', source, 'success', ('%d update fullz %d insert deposit' % (update_count, insert_count)), [[33, '']])
            result_text = LOG_PATTERNS[33]['content'] #33
            bot.send_im(target=source, message=result_text)
        elif source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]:
            confirm_time = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

            query = "update dead_fullz set status='confirm', lock_time=%s, deposit_address='%s' where lock_customer=%s and status='lock'" % (confirm_time, DEPOSIT_ADDRESS[source], source)
            query_conn.execute(query)
            conn.commit()
            update_count = query_conn.rowcount
            
            query = "insert into `deposit` (`bin_type`,`deposit_address`, `deposit_amount`,`uin`, `start_time`) values ('%s', '%s', '%s', '%s', '%s')" % (BIN_TYPE[source], DEPOSIT_ADDRESS[source], DEPOSIT_AMOUNT[source], source, time_now)
            query_conn.execute(query)
            conn.commit()
            insert_count = query_conn.rowcount
            
            DEAD_FULLZ_FLAG[source], DEAD_FULLZ_CONFIRM[source] = False, False
            log_output('113', 'confirm', source, 'success', ('%d update dead_fullz %d insert deposit' % (update_count, insert_count)), [[33, '']])
            result_text = LOG_PATTERNS[33]['content'] #33
            bot.send_im(target=source, message=result_text)
        elif source in PP_CONFIRM and PP_CONFIRM[source]:
            confirm_time = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
            
            query = "update pp set status='confirm', lock_time=%s, deposit_address='%s' where lock_customer=%s and status='lock'" % (confirm_time, DEPOSIT_ADDRESS[source], source)
            query_conn.execute(query)
            conn.commit()
            update_count = query_conn.rowcount
            
            query = "insert into `deposit` (`bin_type`, `deposit_address`, `deposit_amount`,`uin`, `start_time`) values ('%s', '%s', '%s', '%s', '%s')" % (BIN_TYPE[source], DEPOSIT_ADDRESS[source], DEPOSIT_AMOUNT[source], source, time_now)
            query_conn.execute(query)
            conn.commit()
            insert_count = query_conn.rowcount
            
            PP_FLAG[source], PP_CONFIRM[source] = False, False
            log_output('114', 'confirm', source, 'success', ('%d update pp %d insert deposit' % (update_count, insert_count)), [[33, '']])
            result_text = LOG_PATTERNS[33]['content'] #33
            bot.send_im(target=source, message=result_text)
        else:
            log_output('115', 'confirm', source, 'fail', 'not CONFIRM', [[34, '']])
            message = LOG_PATTERNS[34]['content'] #34
            bot.send_im(target=source, message=message)
    except:
        print('confirm cb error occurs.')

def cancel_cb(bot, event):
    global bins_list, fullz_list, dead_fullz_list, pp_amount, FULLZ_NAME, FULLZ_NUM, FULLZ_TYPE, DEAD_FULLZ_NAME, DEAD_FULLZ_NUM, DEAD_FULLZ_TYPE, PP_NUM, PP_FLAG, FULLZ_FLAG, DEAD_FULLZ_FLAG, FULLZ_CONFIRM, DEAD_FULLZ_CONFIRM, PP_CONFIRM, PP_PRICE, CREDIT_PRICE, DEBIT_PRICE, FLAG_USER_BAN

    source = event.data["source"]["aimId"]
    message = ""
    # print(source)

    try:
        if source in FULLZ_CONFIRM and FULLZ_CONFIRM[source]:
            query = "update fullz set status='on', lock_time=0, lock_customer='', deposit_address='' where status='lock' and lock_customer=%s" % source
            query_conn.execute(query)
            conn.commit()
            update_count = query_conn.rowcount

            query = "update `order` set `canceled`='Y' where uin=%s and product_type='fullz' and ongoing='Y'" % source
            query_conn.execute(query)
            conn.commit()

            log_output('116', 'cancel', source, 'success', ('%d update fullz status=on' % update_count), [[35, '']])
            message = LOG_PATTERNS[35]['content'] #35
            FULLZ_CONFIRM[source] = False
            DEPOSIT_AMOUNT[source], DEPOSIT_ADDRESS[source], BIN_TYPE[source] = ("", "", "")
        elif source in DEAD_FULLZ_CONFIRM and DEAD_FULLZ_CONFIRM[source]:
            query = "update dead_fullz set status='on', lock_time=0, lock_customer='', deposit_address='' where status='lock' and lock_customer=%s" % source
            query_conn.execute(query)
            conn.commit()
            update_count = query_conn.rowcount

            query = "update `order` set `canceled`='Y' where uin=%s and product_type='dead_fullz' and ongoing='Y'" % source
            query_conn.execute(query)
            conn.commit()

            log_output('117', 'cancel', source, 'success', ('%d update dead_fullz status=on' % update_count), [[35, '']])
            message = LOG_PATTERNS[35]['content'] #35
            DEAD_FULLZ_CONFIRM[source] = False
            DEPOSIT_AMOUNT[source], DEPOSIT_ADDRESS[source], BIN_TYPE[source] = ("", "", "")
        elif source in PP_CONFIRM and PP_CONFIRM[source]:
            query = "update pp set status='on', lock_time=0, lock_customer='', deposit_address='' where status='lock' and lock_customer=%s" % source
            query_conn.execute(query)
            conn.commit()
            update_count = query_conn.rowcount

            query = "update `order` set `canceled`='Y' where uin=%s and product_type='pp' and ongoing='Y'" % source
            query_conn.execute(query)
            conn.commit()

            log_output('118', 'cancel', source, 'success', ('%d update pp status=on' % update_count), [[35, '']])
            message = LOG_PATTERNS[35]['content'] #35
            PP_CONFIRM[source] = False
            PP_NUM[source] = ""
        else:
            log_output('119', 'cancel', source, 'fail', 'bitcoin', [[36, '']])
            message = LOG_PATTERNS[36]['content'] #36
    except:
        print('cancel cb error occurs.')
        
    bot.send_im(target=source, message=message)


def main():

    # get log patterns
    log_pattern()

    # Creating a new bot instance.
    bot = ICQBot(token=TOKEN, name=NAME, version=VERSION)
    # Registering handlers.
    bot.dispatcher.add_handler(UserAddedToBuddyListHandler(chat_cb))
    bot.dispatcher.add_handler(UnknownCommandHandler(callback=unknown_cb))
    bot.dispatcher.add_handler(MessageHandler(filters=MessageFilter.text, callback=chat_cb))
    bot.dispatcher.add_handler(MessageHandler(filters=MessageFilter.chat, callback=chat_cb))

    bot.dispatcher.add_handler(CommandHandler(command="command", callback=command_cb))
    bot.dispatcher.add_handler(CommandHandler(command="bins", callback=bins_cb))
    bot.dispatcher.add_handler(CommandHandler(command="buy", callback=buy_cb))
    bot.dispatcher.add_handler(CommandHandler(command="PP", callback=pp_cb))
    bot.dispatcher.add_handler(CommandHandler(command="Fullz", callback=fullz_cb))
    bot.dispatcher.add_handler(CommandHandler(command="dead_fullz", callback=dead_fullz_cb))
    bot.dispatcher.add_handler(CommandHandler(command="confirm", callback=confirm_cb))
    bot.dispatcher.add_handler(CommandHandler(command="start", callback=start_cb))
    bot.dispatcher.add_handler(CommandHandler(command="stop", callback=stop_cb))
    bot.dispatcher.add_handler(CommandHandler(command="help", callback=help_cb))
    bot.dispatcher.add_handler(CommandHandler(command="cancel", callback=cancel_cb))

    bot.dispatcher.add_handler(FeedbackCommandHandler(target=OWNER))

    # Starting a polling thread watching for new events from server. This is a non-blocking call.
    bot.start_polling()

    # Blocking the current thread while the bot is working until SIGINT, SIGTERM or SIGABRT is received.
    bot.idle()


if __name__ == "__main__":
    main()




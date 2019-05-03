from mycrypt import encrypt, decrypt
from mydatabase import conn, query_conn
import datetime

# mysql model

class BinModel:
    def __init__(self):
        pass

    def getPP(self, where='1'):
        query = "select id, email, password, ip_address, location, user_agent, browser, platform, status, lock_time, lock_customer, deposit_address from pp where %s" % where
        query_conn.execute(query)
        f_list = query_conn.fetchall()
        r_list = []
        for f in f_list:
            r_list.append({'id': f[0], 'email': decrypt(f[1]), 'password': decrypt(f[2]), 'ip_address': decrypt(f[3]), 'location': decrypt(f[4]), 'user_agent': decrypt(f[5]), 'browser': decrypt(f[6]), 'platform': decrypt(f[7]), 'status': f[8], 'lock_time': f[9], 'lock_customer': f[10], 'deposit_address': f[11]})
        return r_list

    def getFullz(self, where='1'):
        query = "select id, full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, type, status, lock_time, lock_customer, deposit_address from fullz where %s" % where
        query_conn.execute(query)
        f_list = query_conn.fetchall()
        r_list = []
        for f in f_list:
            r_list.append({'id': f[0], 'full_name': decrypt(f[1]), 'birth_date': decrypt(f[2]), 'address': decrypt(f[3]), 'zip': decrypt(f[4]), 'country': decrypt(f[5]), 'phone': decrypt(f[6]), 'ssn': decrypt(f[7]), 'secu_question': decrypt(f[8]), 'secu_answer': decrypt(f[9]), 'card_bin': decrypt(f[10]), 'card_bank': decrypt(f[11]), 'card_type': decrypt(f[12]), 'card_number': decrypt(f[13]), 'expire_date': decrypt(f[14]), 'cvv': decrypt(f[15]), 'account_number': decrypt(f[16]), 'sortcode': decrypt(f[17]), 'user_name': decrypt(f[18]), 'password': decrypt(f[19]), 'ip_address': decrypt(f[20]), 'location': decrypt(f[21]), 'user_agent': decrypt(f[22]), 'browser': decrypt(f[23]), 'platform': decrypt(f[24]), 'type': decrypt(f[25]), 'status': f[26], 'lock_time': f[27], 'lock_customer': f[28], 'deposit_address': f[29]})
        return r_list

    def getDeadFullz(self, where='1'):
        query = "select id, full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, type, status, lock_time, lock_customer, deposit_address from dead_fullz where %s" % where
        query_conn.execute(query)
        f_list = query_conn.fetchall()
        r_list = []
        for f in f_list:
            r_list.append({'id': f[0], 'full_name': decrypt(f[1]), 'birth_date': decrypt(f[2]), 'address': decrypt(f[3]), 'zip': decrypt(f[4]), 'country': decrypt(f[5]), 'phone': decrypt(f[6]), 'ssn': decrypt(f[7]), 'secu_question': decrypt(f[8]), 'secu_answer': decrypt(f[9]), 'card_bin': decrypt(f[10]), 'card_bank': decrypt(f[11]), 'card_type': decrypt(f[12]), 'card_number': decrypt(f[13]), 'expire_date': decrypt(f[14]), 'cvv': decrypt(f[15]), 'account_number': decrypt(f[16]), 'sortcode': decrypt(f[17]), 'user_name': decrypt(f[18]), 'password': decrypt(f[19]), 'ip_address': decrypt(f[20]), 'location': decrypt(f[21]), 'user_agent': decrypt(f[22]), 'browser': decrypt(f[23]), 'platform': decrypt(f[24]), 'type': decrypt(f[25]), 'status': f[26], 'lock_time': f[27], 'lock_customer': f[28], 'deposit_address': f[29]})
        return r_list

    def getLog(self):
        query = "select id, content, params from log where 1 "
        query_conn.execute(query)
        f_list = query_conn.fetchall()
        r_list = {}
        for f in f_list:
            r_list[f[0]] = {'content': f[1], 'params': f[2]}
        return r_list

    def getChat(self, uin):
        try:
            log_list = self.getLog()
            query = "select id, uin, `time`, log_id, log_params, command from chat where uin=%s order by time asc, id asc" % uin
            query_conn.execute(query)
            f_list = query_conn.fetchall()
            r_list = []
            for f in f_list:
                time = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=f[2])).strftime('%Y-%m-%d %H:%M:%S')
                if f[5] != '':
                    message = f[5]
                    is_bot = False
                else:
                    if f[3] in log_list:
                        if log_list[f[3]]['params'] > 0:
                            patterns = f[4].split('###')
                            message = log_list[f[3]]['content'] % tuple(patterns)
                        else:
                            message = log_list[f[3]]['content']
                    else:
                        message = f[4]
                    is_bot = True
                r_list.append({'id': f[0], 'time': time, 'message': message, 'is_bot': is_bot})
            return r_list
        except:
            print('get chat model error occurs.')

    def getUser(self, uin=''):
        if uin == '':
            query = "select uin, max(buy_time), max(ban), max(chat_time) from user group by uin"
        else:
            query = "select uin, buy_time, ban, chat_time from user where uin=%s order by id desc limit 1" % uin
        query_conn.execute(query)
        f_list = query_conn.fetchall()
        r_list = []
        for f in f_list:
            buy_time = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=f[1])).strftime('%Y-%m-%d %H:%M:%S')
            chat_time = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=f[3])).strftime('%Y-%m-%d %H:%M:%S')
            r_list.append({'uin': f[0], 'time': chat_time, 'ban': f[2]})
        r_list.sort(key=lambda item: item['time'], reverse=True)
        return r_list

    def getOrder(self, where='1'):
        query = "select id, uin, `time`, product_type, product_id, btc, success, ongoing, chat_id, gbp, canceled from `order` where %s order by `time` desc" % where
        query_conn.execute(query)
        f_list = query_conn.fetchall()
        r_list = []
        for f in f_list:
            time = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=f[2])).strftime('%Y-%m-%d %H:%M:%S')
            r_list.append({'id': f[0], 'uin': f[1], 'time': time, 'product_type': f[3], 'product_id': f[4], 'btc': f[5], 'success': f[6], 'ongoing': f[7], 'chat_id': f[8], 'gbp': f[9], 'canceled': f[10]})
        return r_list

    def setUserBan(self, uin, ban):
        if ban == 'true':
            set_ban = 'Y'
        else:
            set_ban = 'N'
        query = "update `user` set ban='%s' where uin=%s" % (set_ban, uin)
        query_conn.execute(query)
        conn.commit()
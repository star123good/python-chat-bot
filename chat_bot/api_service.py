from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import datetime
from mybin import BinModel


PORT = 8082



# http request handler
class myHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # model instance
        self.bins = BinModel()
        
        # route method & parameters
        routes = self.path.split('/')
        if len(routes) > 1:
            method_name = routes[1].lower()
        else:
            method_name = ''
        if len(routes) > 2:
            param_value = routes[2].lower()
        else:
            param_value = ''
        if len(routes) > 3:
            param_key = routes[3].lower()
        else:
            param_key = ''

        # route of myHandler
        if method_name != '':
            if method_name == 'main':
                message = self.getMain(param_value)
            elif method_name == 'user':
                message = self.getUser(param_value)
            elif method_name == 'order':
                message = self.getOrder(param_value, param_key)
            elif method_name == 'chat':
                message = self.getChat(param_value)
            elif method_name == 'pp':
                message = self.getPP(param_value)
            elif method_name == 'fullz':
                message = self.getFullz(param_value)
            elif method_name == 'dead_fullz':
                message = self.getDeadFullz(param_value)
            elif method_name == 'set_ban':
                message = self.setUserBan(param_value, param_key)
            else:
                message = "post url is not correct."
        else:
            message = "post url is not correct."

        # output json data
        self.wfile.write(bytes(json.dumps({'result': message}), "utf8"))
        return

    def do_GET(self):
        print ("get request...")
        self.send_response(200)
        self.send_header('Content-type','text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        message = "Nothing to see here."
        self.wfile.write(bytes(message, "utf8"))
        return

    # order list process
    def processOrder(self, orders):
        pps_sold = pps_money = pps_unfinished = pps_trans = fzs_sold = fzs_money = fzs_unfinished = fzs_trans = dfs_sold = dfs_money = dfs_unfinished = dfs_trans = 0
        pps_week = [0,0,0,0,0,0,0]
        fzs_week = [0,0,0,0,0,0,0]
        dfs_week = [0,0,0,0,0,0,0]
        unfinished_pays = []
        unfinished_counts = 0
        unfinished_count_limit = 5
        date_now = datetime.datetime.now()
        
        for od in orders:
            tmp_ids = od['product_id'].split(',')
            tmp_cnt = 0
            for tmp in tmp_ids:
                if tmp != '' and int(tmp) > 0:
                    tmp_cnt += 1

            delta_day = (date_now - datetime.datetime.strptime(od['time'], '%Y-%m-%d %H:%M:%S')).days
            
            if od['product_type'] == 'pp':
                if od['success'] == 'Y':
                    pps_sold += tmp_cnt
                    pps_money += float(od['gbp'])
                    pps_trans += 1;
                    if delta_day < 7:
                        pps_week[6-delta_day] += float(od['gbp'])
                if od['success'] == 'N' and od['ongoing'] == 'Y':
                    pps_unfinished += float(od['gbp'])
                    unfinished_counts += 1
                    if unfinished_counts < unfinished_count_limit:
                        unfinished_pays.append(od)
            elif od['product_type'] == 'fullz':
                if od['success'] == 'Y':
                    fzs_sold += tmp_cnt
                    fzs_money += float(od['gbp'])
                    fzs_trans += 1;
                    if delta_day < 7:
                        fzs_week[6-delta_day] += float(od['gbp'])
                if od['success'] == 'N' and od['ongoing'] == 'Y':
                    fzs_unfinished += float(od['gbp'])
                    unfinished_counts += 1
                    if unfinished_counts < unfinished_count_limit:
                        unfinished_pays.append(od)
            elif od['product_type'] == 'dead_fullz':
                if od['success'] == 'Y':
                    dfs_sold += tmp_cnt
                    dfs_money += float(od['gbp'])
                    dfs_trans += 1;
                    if delta_day < 7:
                        dfs_week[6-delta_day] += float(od['gbp'])
                if od['success'] == 'N' and od['ongoing'] == 'Y':
                    dfs_unfinished += float(od['gbp'])
                    unfinished_counts += 1
                    if unfinished_counts < unfinished_count_limit:
                        unfinished_pays.append(od)

        return pps_sold, pps_money, pps_unfinished, fzs_sold, fzs_money, fzs_unfinished, dfs_sold, dfs_money, dfs_unfinished, pps_week, fzs_week, dfs_week, unfinished_pays, unfinished_counts, pps_trans, fzs_trans, dfs_trans

    # /main (dashboard page)
    def getMain(self, param_value):
        # order
        orders = self.bins.getOrder()

        pps_sold, pps_money, pps_unfinished, fzs_sold, fzs_money, fzs_unfinished, dfs_sold, dfs_money, dfs_unfinished, pps_week, fzs_week, dfs_week, unfinished_pays, unfinished_counts, pps_trans, fzs_trans, dfs_trans = self.processOrder(orders)

        # pp
        pps = self.bins.getPP()
        pps_total = len(pps)
        pps_on = self.bins.getPP('`status`="on"')
        pps_remain = len(pps_on)

        # fullz
        fzs = self.bins.getFullz()
        fzs_total = len(fzs)
        fzs_on = self.bins.getFullz('`status`="on"')
        fzs_remain = len(fzs_on)

        # dead_fullz
        dfs = self.bins.getDeadFullz()
        dfs_total = len(dfs)
        dfs_on = self.bins.getDeadFullz('`status`="on"')
        dfs_remain = len(dfs_on)

        # result
        result = {
            'pp': {'current_total': pps_total, 'current_remain': pps_remain, 'sold_count': pps_sold, 'sold_money': pps_money, 'unfinished_money': pps_unfinished, 'week': pps_week}, 
            'fullz': {'current_total': fzs_total, 'current_remain': fzs_remain, 'sold_count': fzs_sold, 'sold_money': fzs_money, 'unfinished_money': fzs_unfinished, 'week': fzs_week}, 
            'dead_fullz': {'current_total': dfs_total, 'current_remain': dfs_remain, 'sold_count': dfs_sold, 'sold_money': dfs_money, 'unfinished_money': dfs_unfinished, 'week': dfs_week},
            'unfinished': unfinished_pays,
            'unfinished_counts': unfinished_counts
            }

        return result

    # /user (user page)
    def getUser(self, param_value):
        users = self.bins.getUser(param_value)
        if len(users) > 0:
            if param_value == '':
                # users page
                return users
            else:
                # user page
                # print(users)
                
                # pp
                # pps = self.bins.getPP('lock_customer=%s' % param_value)
                # fullz
                # fzs = self.bins.getFullz('lock_customer=%s' % param_value)
                # dead_fullz
                # dfs = self.bins.getDeadFullz('lock_customer=%s' % param_value)

                # order
                orders = self.bins.getOrder('uin=%s' % param_value)

                pps_sold, pps_money, pps_unfinished, fzs_sold, fzs_money, fzs_unfinished, dfs_sold, dfs_money, dfs_unfinished, pps_week, fzs_week, dfs_week, unfinished_pays, unfinished_counts, pps_trans, fzs_trans, dfs_trans = self.processOrder(orders)

                result = {
                    'pp': pps_sold, 
                    'fullz': fzs_sold, 
                    'dead_fullz': dfs_sold,
                    'trans': pps_trans+fzs_trans+dfs_trans,
                    'price': pps_money+fzs_money+dfs_money,
                    'ban': users[0]['ban']
                    }
                return result

        return

    # /order (order page)
    def getOrder(self, param_value, param_key):
        if param_key == 'uin':
            # search by UIN
            result = self.bins.getOrder('uin=%s' % param_value)
        elif param_key == 'pid':
            # search by product id
            result = self.bins.getOrder('product_id like "%s"' % ('%'+str(param_value)+'%'))
        elif param_key == 'oid':
            # search by order id
            result = self.bins.getOrder('id=%s' % param_value)
        else:
            result = self.bins.getOrder()
        return result

    # /chat (chat page)
    def getChat(self, param_value):
        users = self.bins.getUser()
        if param_value == '':
            param_value = users[0]['uin']
        
        chats = self.bins.getChat(param_value)
        result = {
            'users': users, 
            'chats': chats,
            'selected': param_value
            }
        return result

    def getPP(self, param_value):
        return self.bins.getPP()

    def getFullz(self, param_value):
        return self.bins.getFullz()

    def getDeadFullz(self, param_value):
        return self.bins.getDeadFullz()

    def setUserBan(self, param_value, param_key):
        self.bins.setUserBan(param_value, param_key)
        return 


def main():
    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT), myHandler)
        print('Started httpserver on port ' , PORT)
        
        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()

if __name__ == '__main__':
    main()
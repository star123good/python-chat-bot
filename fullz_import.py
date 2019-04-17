import mysql.connector
import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

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
    fullz_file = open("fullz.txt", "r")
    fullz_data_list = list(fullz_file)
except Exception as e:
    print(e)
    exit


for index, data in enumerate(fullz_data_list):
    try:
        if data.index("Card BIN : ") >= 0:
            id, full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform = fullz_data_list[index-12], fullz_data_list[index-11], fullz_data_list[index-10], fullz_data_list[index-9], fullz_data_list[index-8], fullz_data_list[index-7], fullz_data_list[index-6], fullz_data_list[index-5], fullz_data_list[index-4], fullz_data_list[index-3], fullz_data_list[index], fullz_data_list[index+1], fullz_data_list[index+2], fullz_data_list[index+3], fullz_data_list[index+4], fullz_data_list[index+5], fullz_data_list[index+6], fullz_data_list[index+7], fullz_data_list[index+10], fullz_data_list[index+11], fullz_data_list[index+14], fullz_data_list[index+15], fullz_data_list[index+16], fullz_data_list[index+17], fullz_data_list[index+18]
            id = id.replace("| id : ", "").replace("\n", "")
            bin1 = card_bin.replace("| Card BIN : ", "").replace("\n", "")
            url = "https://lookup.binlist.net/" + bin1
            bin_data = requests.get(url)
            bin_data = bin_data.json()
            type = bin_data['type']
            type = encrypt(type).decode('utf-8')
            full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform = encrypt(full_name).decode('utf-8'), encrypt(birth_date).decode('utf-8'), encrypt(address).decode('utf-8'), encrypt(zip).decode('utf-8'), encrypt(country).decode('utf-8'), encrypt(phone).decode('utf-8'), encrypt(ssn).decode('utf-8'), encrypt(secu_question).decode('utf-8'), encrypt(secu_answer).decode('utf-8'), encrypt(card_bin).decode('utf-8'), encrypt(card_bank).decode('utf-8'), encrypt(card_type).decode('utf-8'), encrypt(card_number).decode('utf-8'), encrypt(expire_date).decode('utf-8'), encrypt(cvv).decode('utf-8'), encrypt(account_number).decode('utf-8'), encrypt(sortcode).decode('utf-8'), encrypt(user_name).decode('utf-8'), encrypt(password).decode('utf-8'), encrypt(ip).decode('utf-8'), encrypt(location).decode('utf-8'), encrypt(user_agent).decode('utf-8'), encrypt(browser).decode('utf-8'), encrypt(platform).decode('utf-8')

            #item = [fullz_data_list[index].replace("| Email: ", "").replace("\n", ""), fullz_data_list[index+1].replace("Email: ", "").replace("\n", ""), fullz_data_list[index+2].replace("Email: ", "").replace("\n", ""), fullz_data_list[index+3].replace("Email: ", "").replace("\n", ""), fullz_data_list[index+4].replace("Email: ", "").replace("\n", ""), fullz_data_list[index+5].replace("Email: ", "").replace("\n", ""), fullz_data_list[index+6].replace("Email: ", "").replace("\n", "")]

            query = "insert into `fullz` (`id`, `full_name`, `birth_date`, `address`, `zip`, `country`, `phone`, `ssn`, `secu_question`, `secu_answer`, `card_bin`, `card_bank`, `card_type`, `card_number`, `expire_date`, `cvv`, `account_number`, `sortcode`, `user_name`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`, `type`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform, type)
            query_conn.execute(query)
            conn.commit()
    except Exception as e:
        pass

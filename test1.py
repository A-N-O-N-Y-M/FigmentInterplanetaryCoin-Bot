import pymysql
from pymysql import cursors

db_host = 'FVH1.spaceweb.ru'
db_port = 3306
db_user = 'reichstag1'
db_password = 'EW_PUG3JR7DBeX2Z'
db_database='reichstag1'

connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,database=db_database, cursorclass=cursors.DictCursor)
cursor = connection.cursor()

# cursor.execute('select was_added_as_fren from Data where user_id = 5154179374')
# x = cursor.fetchone()
# connection.commit()
# print(x)

# cursor.execute('update Data set referrals="5125737209,1234567890,012498891529" where user_id=1251526792')
# connection.commit()

# cursor.execute(f'''SELECT user_id FROM Data WHERE FIND_IN_SET('5125737209', referrals) > 0;''')
# referral_id = cursor.fetchone()
# referral_id = referral_id['user_id']
# connection.commit()
#
# print(referral_id)

# cursor.execute('delete from PassiveFarm where fic_id="3823067:1I5mTXyXteawAI9M8SlfADz3MgZl8oIOE5O1g53h"')
# connection.commit()

cursor.execute('select user_id from Data')
uids = cursor.fetchall()
connection.commit()

old = ''
new = ''

for el in uids:
    cursor.execute(f'select referral_link from Data where user_id={el["user_id"]}')
    rl = cursor.fetchone()
    connection.commit()

    old += rl['referral_link']

    new_rl = (str(rl['referral_link'])).replace('FreeIvannikovCoin', 'FigmentInterplanetaryCoin')
    cursor.execute(f'update Data set referral_link="{new_rl}" where user_id={el["user_id"]}')
    connection.commit()

    cursor.execute(f'select referral_link from Data where user_id={el["user_id"]}')
    new_rl_db = cursor.fetchone()
    connection.commit()

    new += new_rl_db['referral_link']

print(f'Till:\n{old}\n\nUpdated:\n{new}')


connection.close()
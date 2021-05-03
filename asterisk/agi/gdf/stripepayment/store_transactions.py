import sys
import MySQLdb
from config import *



class storTransactions:

    """A Stripe database connector class"""

    def __init__(self):
        """Constructor"""
        self.db = None
        

    def connect(self):
        """ Database connector function"""
        self.db = MySQLdb.connect(host=DBHOST, user=DBUSER,
                                  passwd=DBPASSWD, db=DBNAME)


    def storeResult(self,caller_id,call_id,dbresult,transaction_id):
            """Inserts a new transaction data"""
            result = dict()
            result['status'] = False
            try:
                self.connect()

                db = self.db.cursor()

                sql = 'INSERT INTO gdf_stripe_transactions VALUES (NULL,%s,%s,%s,%s,NOW())' 
                value =(caller_id, call_id,dbresult,transaction_id)
                # print(value,sql)
                db.execute(sql,value)

                db.close()
                self.db.commit()
                action_id = db.lastrowid
                self.db.close()

                result['status'] = True
                result['string'] = 'Your transaction  successfully committed, action_id is %s' % action_id

            except MySQLdb.Error, e:
                result['error_cause'] = 'MySQL Error [%d]: %s' % (
                    e.args[0], e.args[1])
            except:
                result['error_cause'] = 'Unknown error occurred'

            return result
 
# res=storTransactions().storeResult('None','None','None','None')
# if res['status']==True:
#     print('got database result %s' %res['string'])
# else:
#     print(res['error_cause'])
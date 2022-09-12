from geoville_ms_publisher.publisher import *

sender = Publisher('test',
                   db_ini_file='database.ini',
                   db_ini_section='postgresql',
                   rabbit_mq_user=None)

#for i in range(3000):
#    data = {'number': i}
#    sender.publish(data)
#    print("sent: " + str(i))

data = {
  "tile": "33UXP",
  "date": "2019-06-30",
  "token": "sen2cor",
  "user_id": "7c5c398a2e0da81aed29109be1e8a81f12c17c179b08726d782c2f8dfc798862"
}

sender.publish(data)
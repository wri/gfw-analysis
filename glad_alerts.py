__author__ = 'sgibbes'
import datetime

start = datetime.datetime.strptime("1/1/16","%m/%d/%y")
end_date1 = start + datetime.timedelta(days=34)
end_date2 = start + datetime.timedelta(days=40)
print end_date1
print end_date2
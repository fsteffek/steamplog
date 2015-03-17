import datetime


def round_datetime(a_date=datetime.datetime.now()):
    '''Round a datetime object to the nearest minute multiple of 10'''
    discard = datetime.timedelta(
            minutes=a_date.minute % 10,
            seconds=a_date.second,
            microseconds=a_date.microsecond)
    a_date -= discard
    if discard >= datetime.timedelta(minutes=5):
        a_date += datetime.timedelta(minutes=10)
    return a_date

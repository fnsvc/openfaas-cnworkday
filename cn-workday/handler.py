# coding: utf-8
import csv
from datetime import datetime
from io import open
import os

import pytz

CACHE = {}
TZ = pytz.timezone('Asia/Shanghai')


def cleanup_dict(d):
    r = {}
    for k, v in d.items():
        if isinstance(k, str):
            k = k.strip()
        if isinstance(v, str):
            v = v.strip()
        r[k] = v

    return r


def load_data(year):
    '''Load CSV data into memory'''
    year = str(year)
    if year in CACHE:
        return True

    data_file = os.path.join(os.path.dirname(__file__), 'data', '{}.csv'.format(year))
    if not os.path.isfile(data_file):
        return False

    CACHE[year] = {}
    with open(data_file, encoding='utf-8') as rf:
        # Detect CSV header line
        has_header = csv.Sniffer().has_header(rf.read(1024))
        rf.seek(0)  # Reset fd cursor

        reader = csv.DictReader(rf, ['name', 'date', 'description', 'isholiday', 'isworkday'])
        if has_header:
            next(reader)

        for row in reader:
            day = cleanup_dict(row)
            dt = TZ.localize(datetime.strptime(day['date'], '%Y-%m-%d'))
            CACHE[year][day['date']] = {
                'name': day['name'],
                'year': dt.year,
                'month': dt.month,
                'day': dt.day,
                'is_holiday': bool(int(day['isholiday'])),
                'is_workday': bool(int(day['isworkday'])),
                'is_weekend': dt.weekday() > 4
            }

    return True


def handle(event, context):
    date = event.query.get('date')
    if not date:
        date = TZ.normalize(pytz.utc.localize(datetime.utcnow()))
    else:
        try:
            date = TZ.localize(datetime.strptime(date, '%Y-%m-%d'))
        except Exception:
            return {
                'statusCode': 400,
                'body': {
                    'code': 1,
                    'msg': 'Invalid date format. Must match pattern 2013-12-25',
                }
            }

    year = str(date.year)
    day = {
        'data': {
            'date': date.strftime('%Y-%m-%d'),
            'is_weekend': date.weekday() > 4
        }
    }

    if load_data(year):
        matched_days = list(filter(
            lambda x: all([
                x['year'] == date.year,
                x['month'] == date.month,
                x['day'] == date.day,
            ]),
            CACHE[year].values()
        ))

        if matched_days:
            that_day = matched_days[0]
            day['data'].update({
                'is_holiday': that_day['is_holiday'],
                'is_workday': that_day['is_workday'],
                'is_weekend': that_day['is_weekend'],
                'description': that_day['name'],
            })
        else:
            day['data'].update({
                'is_holiday': False,
                'is_workday': not day['data']['is_weekend'],
                'description': '',
            })
        day['code'] = 0
    else:
        day.update({
            'code': 2,
            'msg': 'No data for year {}'.format(year)
        })

    return {
        "statusCode": 200,
        "body": day,
    }


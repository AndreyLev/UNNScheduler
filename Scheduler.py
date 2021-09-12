import datetime
import requests

class Scheduler:

    def __init__(self, login, password):
        self._portal = 'https://portal.unn.ru'
        self._session = requests.Session()
        self._login = login
        self._password = password
        self._log_in()
        self._date_template = '%Y.%m.%d'

    def _log_in(self):
        data = {
            'AUTH_FORM': 'Y',
            'TYPE': 'AUTH',
            'USER_LOGIN': f'{self._login}',
            'USER_PASSWORD': f'{self._password}'
        }
        login_response = self._session.post(self._portal, data=data)

    def _get_group_id(self, group_name):
        query_str = f'https://portal.unn.ru/ruzapi/search?term={group_name}&type=group'
        response = self._session.get(query_str)
        if response.status_code == 200:
            response_json = response.json()
            if len(response_json):
                return response_json[0]['id']

    def _handle_schedule(self, schedule_json):
        schedule_items = [
            {
                'day': item['dayOfWeekString'],
                'room': item['auditorium'],
                'name': item['discipline'],
                'building': item['building'],
                'lecturer': item['lecturer'],
                'date': item['date'],
                'begin': item['beginLesson'],
                'end': item['endLesson']
            }
            for item in schedule_json
        ]

        for item in schedule_items:
            if item['lecturer'] == '!Вакансия':
                item['lecturer'] = 'Отсутствует'
            if item['room'] == 'д.а.':
                item['room'] = 'Онлайн'
            if item['building'] == 'Виртуальное':
                item['building'] = ''
            else:
                item['building'] = ' [' + item['building'] + ']'
            date_items = item['date'].split('.')
            item['date'] = '.'.join(date_items[::-1])

        schedule_strings = [
            f'{item["day"]} {item["date"]} {item["room"]}{item["building"]} {item["name"]} {item["begin"]}-{item["end"]}'
            for item in schedule_items
        ]
        result_string = ''
        for str in schedule_strings:
            result_string += str + '\n'
        return result_string
    
    def get_by_group(self, group_name, days_before_today = 0, days_after_today = 7):
        group_id = self._get_group_id(group_name)
        if group_id:
            today = datetime.datetime.now()
            start_date = today
            end_date = today
            if days_before_today:
                before_timedelta = datetime.timedelta(days_before_today)
                start_date -= before_timedelta
            if days_after_today:
                after_timedelta = datetime.timedelta(days_after_today)
                end_date += after_timedelta
            start_date = start_date.strftime(self._date_template)
            end_date = end_date.strftime(self._date_template)
            query_str = f'https://portal.unn.ru/ruzapi/schedule/group/{group_id}?start={start_date}&finish={end_date}&lng=1'
            schedule_response = self._session.get(query_str)
            if schedule_response.status_code == 200:
                schedule = schedule_response.json()
                if len(schedule):
                    schedule_str = self._handle_schedule(schedule)
                    return schedule_str
                    

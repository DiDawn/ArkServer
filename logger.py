from time import localtime
import os


class Log:
    def __init__(self, save_logs):
        self.save_logs = save_logs

        if not os.path.exists('log.txt'):
            with open('log.txt', 'w') as f:
                f.write('')
        with open('log.txt', 'r') as f:
            self.log = f.readlines()

    def __str__(self):
        return '\n'.join(self.log)

    def append(self, msg):
        date = localtime()
        year, month = date.tm_year, date.tm_mon
        if month < 10:
            month = f'0{month}'
        day, hour, minute, second = date.tm_mday, date.tm_hour, date.tm_min, date.tm_sec
        if day < 10:
            day = f'0{day}'
        if hour < 10:
            hour = f'0{hour}'
        if minute < 10:
            minute = f'0{minute}'
        if second < 10:
            second = f'0{second}'
        msg = f'[{year}/{month}/{day} {hour}:{minute}:{second}]~{msg}'
        self.log.append(msg)

        if self.save_logs:
            with open('log.txt', 'a') as f:
                f.write(msg+'\n')

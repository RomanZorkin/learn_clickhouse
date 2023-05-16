import re
from datetime import datetime
from dateutil.parser import parse
from typing import Any


class LogRecord:

    def __init__(self, record: str) -> None:
        self.head = ''
        self.body = ''
        self.date = None
        self.vm = ''
        self.auth_service = ''
        self.ip = ''
        self.ip_geo = ''
        self.target_port = ''
        self.target_user = ''
        self.accept = False
        self._parse_record(record)

    def to_list(self) -> list[Any]:
        return [
            self.date, self.vm, self.auth_service, self.body, self.accept,
            self.ip, self.ip_geo, self.target_user, self.target_port,
        ]

    def _rec_date(self) -> datetime:
        result = re.search(r'^\w+ \d{2} \d{2}:\d{2}:\d{2}', self.head)
        if result:
            return parse(result.group(0))
        result = re.search(r'^\w+  \d{1} \d{2}:\d{2}:\d{2}', self.head)
        if result:
            return parse(result.group(0))
        print(f'###!!!! ERORR DATE {self.head}')

    def _head_mark(self) -> None:
        head = self.head.split()
        self.vm = head[3]
        self.auth_service = head[4]

    def _adress_mark(self):
        result = re.search(r' (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}) ', self.body)
        if result:
            self.ip = result.group(1)            
        result = re.search(r'port (\d{1,5})', self.body)
        if result:
            self.target_port = result.group(1)

    def _user_mark(self):
        result = re.search(r'user \b(\w+)\b', self.body)
        if result:
            self.target_user = result.group(1)

    def _accept_mark(self):
        result = re.search(r'^Accepted\b', self.body)
        if result:
            self.accept = True

    def _parse_record(self, record):
        record = record.split(': ')
        self.head: str = record[0]
        self.body = record[1].replace('\n', '')
        self.date = self._rec_date()
        self._head_mark()
        self._adress_mark()
        self._user_mark()
        self._accept_mark()

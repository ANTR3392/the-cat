from json import dump as save, load
import os


class db:
    def __init__(self, data):
        self.data = str(data)

    def __enter__(self):
        if not os.path.exists(f'db/{self.data}.json'):
            with open(f'db/{self.data}.json', 'w') as f:
                f.write('{}')

        self.json = load(open(f'db/{self.data}.json')) or {}
        self.json = {**{
            'age': '',
            'bio': '',
            'name': '',
            'last_msg': 0,
            'lvl': 1,
            'xp': 0,
            'msg_amt': 0,
            'voice': 0,
            'bal': 0,
            'gender': '',
            'dep': 0,
            'mc_name': ''
        }, **self.json}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save(self.json, open(f'db/{self.data}.json', 'w'))


class ServerData:
    def __init__(self): ...

    def __enter__(self):
        if not os.path.exists(f'db/server.json'):
            with open(f'db/server.json', 'w') as f:
                f.write('{}')

        self.json = load(open(f'db/server.json')) or {}
        self.json = {**{
            'audit': []
        }, **self.json}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save(self.json, open(f'db/server.json', 'w'))


class Const:
    audit_change_bal = 0
    audit_add_item = 1
    audit_rm_item = 2
    audit_edit_item = 3
    audit_pay = 4
    audit_rob = 5

# -*- coding: utf-8 -*-
# hi-rez-API: Smite, Paladins, Realm.
import datetime
import hashlib
import requests
import json
import os


class HiRezAPI:
    url_prefix = 'http://api.smitegame.com/smiteapi.svc/'  # Default prefix from class Smite

    def __init__(self, dev_id,
                 auth_key,
                 save_session_to_json=True):
        self.name_cls = self.__class__.__name__
        self.save_session_toJson = save_session_to_json
        self.DevId = dev_id
        self.AuthKey = auth_key
        self.session = self.session_to_json('r')
        self.t_now = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        self.langCode = self.lang_results()  # Default is 1 - English

    def create_signature(self, method):
        signature_raw = f'{self.DevId}{method}{self.AuthKey}{self.t_now}'
        signature = hashlib.md5(signature_raw.encode("utf-8")).hexdigest()
        return signature

    def create_session(self):
        if datetime.datetime.utcnow() - self.session['time'] > datetime.timedelta(minutes=14, seconds=59):
            sign = self.create_signature("createsession")
            url_session = f'{self.url_prefix}{"createsession"}Json/{self.DevId}/{sign}/{self.t_now}'
            self.session['time'] = datetime.datetime.utcnow()
            self.session['id'] = requests.get(url_session).json()['session_id']
            if self.save_session_toJson:
                self.session_to_json('w')
        return self.session['id']

    def create_method_url(self, method):
        sign = self.create_signature(method)
        url_method = f'{self.url_prefix}{method}Json/{self.DevId}/{sign}/{self.create_session()}/{self.t_now}'
        return url_method

    def session_to_json(self, method):
        name_json_file = f'{self.DevId}_session'
        if method == 'r' or method == 'read':
            if self.save_session_toJson:
                if os.path.isfile(f'{name_json_file}.json'):
                    with open(f'{name_json_file}.json', "r") as read_file:
                        data_json = json.load(read_file)
                    if self.name_cls in data_json:
                        self.session = data_json[self.name_cls]
                        self.session['time'] = datetime.datetime.strptime(self.session['time'], "%Y-%m-%d %H:%M:%S.%f")
                        return self.session

            self.session = {'id': None,
                            'time': datetime.datetime.utcnow() - datetime.timedelta(minutes=15)}

            return self.session

        if method == 'w' or method == 'write':
            if os.path.isfile(f'{name_json_file}.json'):
                with open(f'{name_json_file}.json', "r") as read_file:
                    data_json = json.load(read_file)
                data_json[self.name_cls] = self.session
                with open(f'{name_json_file}.json', "w") as write_file:
                    json.dump(data_json, write_file, default=str, indent=4)
            else:
                with open(f'{name_json_file}.json', "w") as write_file:
                    json.dump(({self.name_cls: self.session}), write_file, default=str, indent=4)

    def lang_results(self, lang='English'):
        lang_list = {'English': '1', 'German': '2', 'French': '3', 'Chinese': '5', 'Spanish': '7',
                     'Spanish (Latin America)': '9', 'Portuguese': '10', 'Russian': '11', 'Polish': '12',
                     'Turkish': '13'}
        self.langCode = lang_list[lang]
        return lang_list[lang]

    def ping(self):
        url = f'{self.url_prefix}pingJson'
        return requests.get(url).json()

    def test_session(self):
        url = self.create_method_url('testsession')
        return requests.get(url).json()

    def get_data_used(self):
        url = self.create_method_url('getdataused')
        return requests.get(url).json()

    def get_hi_rez_server_status(self):
        url = self.create_method_url('gethirezserverstatus')
        return requests.get(url).json()

    def get_patch_info(self):
        url = self.create_method_url('getpatchinfo')
        return requests.get(url).json()

    def get_gods(self):
        if self.name_cls == 'Realm':
            return 'Only for Smite and Paladins'
        url = f"{self.create_method_url('getgods')}/{self.langCode}"
        return requests.get(url).json()

    def get_items(self):
        if self.name_cls == 'Realm':
            return 'Only for Smite and Paladins'
        url = f"{self.create_method_url('getitems')}/{self.langCode}"
        return requests.get(url).json()

    def get_player(self, player, portal_id=1):
        """
        portal_id: Example values currently supported are: 1:Hi-Rez, 5:Steam, 9:PS4, 10:Xbox, 22:Switch
        """
        url = f"{self.create_method_url('getplayer')}/{player}/{portal_id}"
        print(url)
        return requests.get(url).json()


class Smite(HiRezAPI):

    def get_god_leader_board(self, god_id, queue):
        """
        Returns the current season’s leaderboard for a god/queue combination.
        queue: only queues 440 -Joust Ranked(1v1), 450 - Joust Ranked(3v3), 451 Conquest Ranked.
        """
        url = f"{self.create_method_url('getgodleaderboard')}/{god_id}/{queue}"
        return requests.get(url).json()

    def get_god_skins(self, god_id):
        url = f"{self.create_method_url('getgodskins')}/{god_id}/{self.langCode}"
        return requests.get(url).json()

    def get_god_recommended_items(self, god_id):
        url = f"{self.create_method_url('getgodrecommendeditems')}/{god_id}/{self.langCode}"
        return requests.get(url).json()


class Paladins(HiRezAPI):
    url_prefix = 'http://api.paladins.com/paladinsapi.svc/'

    def get_champions(self):
        url = f"{self.create_method_url('getchampions')}/{self.langCode}"
        return requests.get(url).json()

    def get_champion_cards(self, champion_id):
        url = f"{self.create_method_url('getchampioncards')}/{champion_id}/{self.langCode}"
        return requests.get(url).json()

    def get_champion_leader_board(self, champion_id, queue=428):
        """
        Returns the current season’s leaderboard for a champion/queue combination.
        queue: only queue 428 - LIVE competitive gamepad
        """
        url = f"{self.create_method_url('getchampionleaderboard')}/{champion_id}/{queue}"
        return requests.get(url).json()

    def get_champion_skins(self, champion_id):
        url = f"{self.create_method_url('getchampionskins')}/{champion_id}/{self.langCode}"
        return requests.get(url).json()


class Realm(HiRezAPI):
    url_prefix = 'http://api.realmroyale.com/realmapi.svc/'

    def get_leader_board(self, queue_id=474, ranking_criteria=1):
        """
        queue_id: 474 - LIVE Solo, 475 - LIVE Duo, 476 - LIVE Quad
        ranking_criteria: 1 -Team Wins, 2 -Team Average Placement (shown below),
        3 - Individual Average Kills, 4	- Winrate.
        """
        url = f"{self.create_method_url('getleaderboard')}/{queue_id}/{ranking_criteria}"
        return requests.get(url).json()

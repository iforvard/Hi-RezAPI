# -*- coding: utf-8 -*-
# hi-rez-API: Smite, Paladins, Realm.
import datetime
import hashlib
import requests
import json
import os


class Err_API(Exception):
    err_info_hard = True

    def base_err(self, text):
        if type(self.err_info_hard) == bool:
            if self.err_info_hard:
                raise Err_API(f'Hard error: {text}')
            else:
                return {'ret_msg': f'Soft error: {text}'}
        else:
            raise Err_API(f'Hard error: err_info must be bool')


class HiRezAPI(Err_API):
    url_prefix = 'http://api.smitegame.com/smiteapi.svc/'  # Default prefix from class Smite

    def __init__(
            self, dev_id,
            auth_key,
            save_session_to_json=True,
            lang='English',
            err_info=True
    ):
        self.name_cls = self.__class__.__name__
        self.save_session_toJson = save_session_to_json
        self.DevId = dev_id
        self.AuthKey = auth_key
        self.session = self.session_to_json('r')
        self.t_now = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        self.langCode = self.lang_results(lang)  # Default is 1 - English
        self.err_info_hard = err_info

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
        if self.name_cls == 'RealmAPI':
            return self.base_err('Only for Smite and Paladins')
        url = f"{self.create_method_url('getgods')}/{self.langCode}"
        return requests.get(url).json()

    def get_items(self):
        if self.name_cls == 'RealmAPI':
            return self.base_err('Only for Smite and Paladins')
        url = f"{self.create_method_url('getitems')}/{self.langCode}"
        return requests.get(url).json()

    def get_player(self, player, portal_id=1):
        """
        portal_id: Example values currently supported are: 1:Hi-Rez, 5:Steam, 9:PS4, 10:Xbox, 22:Switch
        """
        url = f"{self.create_method_url('getplayer')}/{player}/{portal_id}"
        return requests.get(url).json()

    def get_player_id_by_name(self, player):
        url = f"{self.create_method_url('getplayeridbyname')}/{player}"
        return requests.get(url).json()

    def get_player_id_by_portal_user_id(self, portal_user_id=76561198078536687, portal_id=5):
        url = f"{self.create_method_url('getplayeridbyportaluserid')}/{portal_id}/{portal_user_id}"
        return requests.get(url).json()

    def get_player_status(self, player_id):
        url = f"{self.create_method_url('getplayerstatus')}/{player_id}"
        return requests.get(url).json()

    def get_match_player_details(self, match_id):
        url = f"{self.create_method_url('getmatchplayerdetails')}/{match_id}"
        return requests.get(url).json()

    def get_friends(self, player_id):
        url = f"{self.create_method_url('getfriends')}/{player_id}"
        return requests.get(url).json()

    def get_player_achievements(self, player_id):
        url = f"{self.create_method_url('getplayerachievements')}/{player_id}"
        return requests.get(url).json()

    def get_match_history(self, player_id):
        url = f"{self.create_method_url('getmatchhistory')}/{player_id}"
        return requests.get(url).json()

    def get_match_details(self, match_id):
        url = f"{self.create_method_url('getmatchdetails')}/{match_id}"
        return requests.get(url).json()

    def get_match_details_batch(self, match_id_list: tuple) -> list:
        str_match_id_list = ','.join([str(champion) for champion in match_id_list])
        url = f"{self.create_method_url('getmatchdetailsbatch')}/{str_match_id_list}"
        print(url)
        return requests.get(url).json()

    def get_match_ids_by_queue(self, queue: str, date: str, hour: str) -> list:
        """
        ------------------------------------------------------------------------------------
        example: queue:'426', date:'2020-05-26', hour:'12,40'
        ------------------------------------------------------------------------------------
        Lists all Match IDs for a particular Match Queue;
        useful for API developers interested in constructing data by Queue.
        To limit the data returned, an {hour} parameter was added (valid values: 0 - 23).
        An {hour} parameter of -1 represents the entire day,
        but be warned that this may be more data than we can return for certain queues.
        Also, a returned “active_flag” means that there is no match information/stats for the corresponding match.
        Usually due to a match being in-progress, though there could be other reasons.
        ------------------------------------------------------------------------------------
        NOTE - To avoid HTTP timeouts in the method, you can now specify a 10-minute window within the specified {hour}
        field to lessen the size of data returned by appending a “,mm” value to the end of {hour}.
        For example, to get the match Ids for the first 10 minutes of hour 3, you would specify {hour} as “3,00”.
        This would only return the Ids between the time 3:00 to 3:09.
        Rules below: Only valid values for mm are “00”, “10”, “20”, “30”, “40”, “50”
        To get the entire third hour worth of Match Ids, call 6 times,
        specifying the following values for {hour}:“3,00”, “3,10”, “3,20”, “3,30”, “3,40”, “3,50”.
        The standard, full hour format of {hour} = “hh” is still supported.
        """
        date = date
        url = f"{self.create_method_url('getmatchidsbyqueue')}/{queue}/{date}/{hour}"
        return requests.get(url).json()


class SmiteAPI(HiRezAPI):

    def get_god_leader_board(self, god_id, queue):
        """
        Returns the current season’s leaderboard for a god/queue combination.
        queue: only queues 440 -Joust Ranked(1v1), 450 - Joust Ranked(3v3), 451 - Conquest Ranked(5v5).
        """
        url = f"{self.create_method_url('getgodleaderboard')}/{god_id}/{queue}"
        return requests.get(url).json()

    def get_god_skins(self, god_id):
        url = f"{self.create_method_url('getgodskins')}/{god_id}/{self.langCode}"
        return requests.get(url).json()

    def get_god_recommended_items(self, god_id):
        url = f"{self.create_method_url('getgodrecommendeditems')}/{god_id}/{self.langCode}"
        return requests.get(url).json()

    def get_god_ranks(self, player_id):
        url = f"{self.create_method_url('getgodranks')}/{player_id}"
        return requests.get(url).json()


class PaladinsAPI(HiRezAPI):
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

    def get_player_batch(self, champion_id_list: list):
        """
        Returns league and other high level data for a particular CSV set of up to 20 playerIds.  [PaladinsAPI only]
        """
        champion_id_list = ','.join([str(champion) for champion in champion_id_list])
        url = f"{self.create_method_url('getplayerbatch')}/{champion_id_list}"
        return requests.get(url).json()

    def get_champion_ranks(self, champion_id):
        url = f"{self.create_method_url('getchampionranks')}/{champion_id}"
        return requests.get(url).json()

    def get_player_loadouts(self, champion_id):
        """
        Returns deck loadouts per Champion.
        """
        url = f"{self.create_method_url('getplayerloadouts')}/{champion_id}/{self.langCode}"
        return requests.get(url).json()


class RealmAPI(HiRezAPI):
    url_prefix = 'http://api.realmroyale.com/realmapi.svc/'

    def get_leader_board(self, queue_id=474, ranking_criteria=1):
        """
        queue_id: 474 - LIVE Solo, 475 - LIVE Duo, 476 - LIVE Quad
        ranking_criteria: 1 -Team Wins, 2 -Team Average Placement (shown below),
        3 - Individual Average Kills, 4	- Winrate.
        """
        url = f"{self.create_method_url('getleaderboard')}/{queue_id}/{ranking_criteria}"
        return requests.get(url).json()

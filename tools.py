#####
#####
#####
from HiRezAPI import SmiteAPI, PaladinsAPI, RealmAPI
import datetime
import time
DevId = ''
AuthKey = ''

smite = SmiteAPI(DevId, AuthKey)
paladins = PaladinsAPI(DevId, AuthKey)
realm = RealmAPI(DevId, AuthKey, err_info=False)


def create_statistics_matches(matches_id):
    matches = {}
    statistics = smite.get_match_details_batch(matches_id)
    for player_match in statistics:
        match_id = player_match['Match']
        if not match_id in matches:
            matches[match_id] = {'losers': [], 'winners': []}

        if player_match['Win_Status'] == 'Loser':
            matches[match_id]['losers'].append(player_match['Reference_Name'])
        else:
            matches[match_id]['winners'].append(player_match['Reference_Name'])
    return matches


def get_match_ids(day):
    """
    426-CONQUEST, 451-CONQUEST RANKED, 448-JUST, 435-ARENA,
    """
    queryset = smite.get_match_ids_by_queue('426', f'2020-05-{day}', '-1')
    return [match['Match'] for match in queryset]


if __name__ == '__main__':
    print(max([len(get_match_ids(day_num)) for day_num in range(1, 26)]))

    # print(len(ranked))
    # # print(ranked)
    # #
    # start_t = time.time()
    # for match in create_statistics_matches(ranked).items():
    #     print(*match)
    # print(time.time() - start_t)
    # for i in smite.get_match_details_batch((1039111688, 1039108433)):
    #     print(i['playerName'] if i['playerName'] else None, end=' ')
    #     print(i['Account_Level'], end=' ')
    #     print(i['Match'], end=' ')
    #     print(i['Reference_Name'], end=' ')
    #     print(i['Win_Status'], end=' ')
    #     print(i['Mastery_Level'], end=' ')
    #     print(i['GodId'])

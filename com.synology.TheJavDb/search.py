import argparse
import html
import os
import json
import copy
import re
import constant
import lib


def _plugin_run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help='json string')
    parser.add_argument("--lang", type=str, required=True, default=None, help='enu|cht|...')
    parser.add_argument("--type", type=str, required=True, default=None, help='movie|tvshow|...')
    parser.add_argument("--limit", type=int, default=1, help='result count')
    parser.add_argument("--allowguess", type=bool, default=True)
    parser.add_argument("--apikey", type=str, default='')

    # unknownPrm is useless, just for prevent error when unknow param inside
    args, unknownPrm = parser.parse_known_args()

    argv_input = json.loads(args.input)
    argv_lang = args.lang
    argv_type = args.type
    argv_limit = args.limit
    argv_allowguess = args.allowguess
    argv_apikey = args.apikey

    if argv_apikey:
        os.environ["METADATA_PLUGIN_APIKEY"] = argv_apikey

    result = None
    success = True
    error_code = 0
    try:
        if argv_type == 'movie':
            result = _search_and_parse(argv_input, argv_type)

    except SystemExit as query_e:
        error_code = constant.ERROR_PLUGIN_QUERY_FAIL
        success = False

    except Exception as e:
        error_code = constant.ERROR_PLUGIN_PARSE_RESULT_FAIL
        success = False

    _process_output(success, error_code, result)


def _match_title(file_name):
    return re.search('([A-Za-z]+-?\d{3})(\D|$)', file_name)


# Title needs to be valid.
def _normalize_title(title):
    if (title.find('-') == -1):
        m = re.search('([A-Za-z]+)(\d+)', title)
        title = title[m.start(1):m.end(1)] + '-' + title[m.start(2):m.end(2)]
    return title


# Try parse out a title like 'ABC-123' from the file name.
def _parse_out_title(file_name):
    file_name = file_name.replace(" ", "-")

    # Split by '@' or 'abc-com' or '-cc', etc.
    sections = re.split("@|[A-Za-z0-9]+-com|[A-Za-z0-9]+-cc|[A-Za-z0-9]+-co", file_name)
    for candidate in sections:
        m = _match_title(candidate)
        if (m != None):
            title = candidate[m.start(1):m.end(1)]
            return _normalize_title(title)
    return file_name
     

def _search_and_parse(input_obj, media_type):
    result = []
    file_name = input_obj['title']
    title = _parse_out_title(file_name)

    # Search. We use `movie` media type here.
    if media_type == 'movie':
        movie_data = lib.main(title)

    result.append(_parse_movie_info(movie_data))

    return result



def _parse_movie_info(movie_data):
    data = copy.deepcopy(constant.MOVIE_DATA_TEMPLATE)

    data['title'] = movie_data['title']
    data['original_available'] = movie_data['original_available']
    data['genre'] = movie_data['genre']
    data['tagline'] = movie_data['tagline']
    data['summary'] = movie_data['summary']
    data['actor'] = movie_data['actor']
    data['director'] = movie_data['director']
    data['writer'] = movie_data['writer']

    if movie_data['rating']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'rating', constant.PLUGINID], movie_data['rating'])
    if movie_data['backdrop']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'backdrop'], movie_data['backdrop'])
    if movie_data['poster']:
        data = _set_data_value(data, ['extra', constant.PLUGINID, 'poster'], movie_data['poster'])
    return data



def _set_data_value(data, key_list, value):
    if not value:
        return data

    now_data = data
    for attr in key_list[:-1]:
        if attr not in now_data:
            now_data[attr] = {}
        now_data = now_data[attr]

    now_data[key_list[-1]] = value
    return data



def _process_output(success, error_code, datas):
    result_obj = {}
    if success:
        result_obj = {'success': True, 'result': datas}
    else:
        result_obj = {'success': False, 'error_code': error_code}

    json_string = json.dumps(result_obj, ensure_ascii=False, separators=(',', ':'))
    json_string = html.unescape(json_string)
    print(json_string)



if __name__ == "__main__":
    _plugin_run()

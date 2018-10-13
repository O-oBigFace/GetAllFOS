import requests
import json
import random
from Logger import logger
import warnings
import time
import os
warnings.filterwarnings("ignore")

topFos = [
    33923547,
    185592680,
    121332964,
    41008148,
    86803240,
    16259570,
    15744967,
    39432304,
    205649164,
    144024400,
    71924100,
    127313418,
    17744445,
    95457728,
    144133560,
    162324750,
    127413603,
    142362112,
    138885662
]

_RECORD_SET = set()

_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'academic.microsoft.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235',
    'cookie':'A=I&I=AxUFAAAAAADcBgAAppxkMXdDMh8WbdW6REgxYA!!&V=4; MC1=GUID=b696858225fe44c09863f86e57fa4c09&HASH=b696&LV=201802&V=4&LU=1519437260089; MUID=04435427E0D767D039295F68E4D76468; msacademic=143996b2-ae82-4969-b7ce-6130b0cf5bab2322323; ai_user=lXzhe|2018-07-12T02:39:50.922Z; _ga=GA1.2.1293331498.1532580770; optimizelyEndUserId=oeu1533104931073r0.32495626027565705; ARRAffinity=448d1b6569c3bbf9a82424dc025f29e939bdc82cd1dfd58ddc9965e8c0ced922; MSCC=1537857855; _gid=GA1.2.965994342.1537858304; graceIncr=0; AMCVS_EA76ADE95776D2EC7F000101%40AdobeOrg=1; AMCV_EA76ADE95776D2EC7F000101%40AdobeOrg=-894706358%7CMCIDTS%7C17800%7CMCMID%7C04348057071353624694285395856562408311%7CMCAAMLH-1538464171%7C11%7CMCAAMB-1538464171%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCCIDH%7C881028428%7CMCOPTOUT-1537866571s%7CNONE%7CvVersion%7C2.3.0; ai_session=++41|1537866332206|1537866340445.8'
}

_HOST = "https://academic.microsoft.com/api/browse/GetEntityDetails?entityId={0}"
_SESSION = requests.session()
_MAXRETRY = 6
_ERRORMESSAGE = "id: {0} | Error: {1}"
_INFOMESSAGE = "id: {0} has done."

proxyHost = "zproxy.lum-superproxy.io"
proxyPort = "22225"
proxyUser = "lum-customer-hl_6c34939f-zone-zone1"
proxyPass = "s5tlbqckrdft"
proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}
_PROXIES = {
    "http": proxyMeta,
    "https": proxyMeta,
}


def _get_page(pagerequest):
    resp = _SESSION.get(
        pagerequest,
        headers=_HEADERS,
        proxies=_PROXIES,
        verify=False,
        timeout=random.choice(range(30, 100))
    )
    resp.encoding = "utf-8"
    if resp.status_code == 200:
        return resp.text
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


# 存储list形式的文件
def save_list_to_file(filename, list):
    with open(filename, "w", encoding="utf-8") as f:
        for l in list:
            f.write(json.dumps(l) + "\n")


def save_str_to_file(filename, s):
    with open(filename, "w", encoding="utf-8") as f:
            f.write(s)


def save_dict_to_file(filename, d, mode="w"):
    with open(filename, mode, encoding="utf-8") as f:
            f.write(json.dumps(d) + "\n")


def getfos(fos_list):
    path_result_json = os.path.join(os.getcwd(), "result", "json")
    path_result = os.path.join(os.getcwd(), "result", "fosdata")

    # 重载
    for fos in fos_list:
        if isinstance(fos, int):
            fos_id = fos
        else:
            fos_id = fos["id"]
        if fos_id in _RECORD_SET:
            continue

        url = _HOST.format(str(fos_id))

        tries = 0
        js = None

        file_path = os.path.join(path_result_json, str(id))
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    js = json.loads(f.read())
                    tries = _MAXRETRY
            except Exception:
                os.remove(file_path)

        while tries < _MAXRETRY:
            tries += 1
            try:
                html = _get_page(url)
                # save_str_to_file(os.path.join(path_result_json, str(fos_id)), html)
                js = json.loads(html.strip())
                break
            except Exception as e:
                if tries < _MAXRETRY:
                    logger.info(_ERRORMESSAGE.format(str(fos_id), str(e)) + " | tries: %d" % tries)
                else:
                    logger.error(_ERRORMESSAGE.format(str(fos_id), str(e)) + " | tries: %d" % tries)
                time.sleep(tries)

        if js is None:
            continue

        list_pfos = []
        if "parentFieldsOfStudy" in js.keys():
            list_pfos = js["parentFieldsOfStudy"]
        list_rfos = []
        if "relatedFieldsOfStudy" in js.keys():
            list_rfos = js["relatedFieldsOfStudy"]
        list_cfos = []
        if "childFieldsOfStudy" in js.keys():
            list_cfos = js["childFieldsOfStudy"]

        fosdata = {
                "id": fos_id,
                "name": js["entity"]["dfn"],
                "pfos": list_pfos,
                "rfos": list_rfos,
                "cfos": list_cfos
                   }
        save_dict_to_file(path_result, fosdata, "a")
        logger.info(_INFOMESSAGE.format(str(fos_id)))

        # 将爬取过的页面加入到 RECORD 集合中
        _RECORD_SET.add(fos_id)
        if len(list_cfos) > 1:
            getfos(list_cfos)


if __name__ == '__main__':
    getfos(fos_list=topFos)

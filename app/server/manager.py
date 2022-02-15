
import sqlite3
import os
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.model import *
from requests import get
from urllib.parse import urlencode
from datetime import datetime
from pprint import pprint
from api.restful.restful_telegram import *


this_folder = os.path.dirname(os.path.abspath(__file__))
print(this_folder, 'bot started')

class TelegramBot(TelegramAPI):
    def __init__(self,
        botid: str = '5150682044:AAHOOBOS28DVmiJmeHkS_nRVGEPI1gp674I',
        chat_id: str = '-748063135',
        update_limit: int = 10
    ) -> None:
        super().__init__(botid, chat_id, update_limit)
        self.db_path = f'{this_folder}/sqlite/sqlite.db'
        try:
            os.remove(self.db_path)
        except: pass
        sleep(0.5)
        self.init_db(); sleep(0.5)
        self.db_engine = create_engine(f'sqlite:///{self.db_path}')
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        Base.metadata.create_all(self.db_engine)
        self.boot_time = int(datetime.now().timestamp())


    def init_db(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        try:
            cur.execute('''CREATE TABLE handled_msg
                (update_id text, from_id text, date integer)''')
            con.commit()
        except Exception as e:
            pass   
        con.close()

    def find_record(self, update_id):
        while True:
            try:
                res = self.session.query(HandledMsg).filter_by(update_id=update_id).count()
            except Exception as e:
                continue
            break
        if res > 0:
            return True
        return False

    def insert_record(self, record):
        record = HandledMsg(
            update_id=record['update_id'],
            from_id=record['from_id'],
            date=record['date'],)
        self.session.add(record)
        self.session.commit()

    def thread_update_worker(self):
        self.send_message('Bot online', '2024554472')
        while True:
            try:
                res = self.get_updates()
                res_list = res['result'][::-1]
                for msg in res_list:
                    update_id = str(msg['update_id'])
                    from_id = str(msg['message']['from']['id'])
                    chat_id = str(msg['message']['chat']['id'])
                    date = int(msg['message']['date'])
                    if date < self.boot_time: break
                    text = str(msg['message']['text'])
                    if not text.startswith('/'): break
                    is_exist = self.find_record(update_id)
                    if is_exist: break
                    self.insert_record({
                        'update_id': update_id,
                        'from_id': from_id,
                        'date': date,
                    })
                    print(date, from_id, text)
                    try:
                        text = text.replace('@lilony_bot', '')
                        if ':' in text:
                            func = getattr(self, text.split(':')[0].replace('/', ''))
                            arg = tuple(text.split(':')[-1].split(','))
                            res = func(arg)
                        else:
                            func = getattr(self, text.replace('/', ''))
                            res = func()
                        if res:
                            for i in res:
                                self.send_message(i, chat_id)
                                sleep(0.1)
                        else:
                            self.send_message('empty list', chat_id)
                    except Exception as e:
                        self.send_message(e, chat_id)
            except Exception as e:
                print(e)
            sleep(0.5)

    def get_covid_info(self, premise) -> list:
        url = f'https://services8.arcgis.com/PXQv9PaDJHzt8rp0/ArcGIS/rest/services/CompulsoryTestingBuilding_View2/FeatureServer/0/query?'
        params = {
            'where': f"SpecifiedPremises_ZH LIKE '%{premise}%' AND Status = 'Active'",
            'geometryType': 'esriGeometryEnvelope',
            'spatialRel': 'esriSpatialRelIntersects',
            'resultType': 'standard',
            'distance': '0.0',
            'units': 'esriSRUnit_Meter',
            'returnGeodetic': 'false',
            'outFields': 'Period_EN, Status_Cal, Deadline_EN, SpecifiedPremises_EN, URL_ZH_CAL',
            'returnGeometry': 'false',
            'featureEncoding': 'esriDefault',
            'multipatchOption': 'xyFootprint',
            'applyVCSProjection': 'false',
            'returnIdsOnly': 'false',
            'returnUniqueIdsOnly': 'false',
            'returnCountOnly': 'false',
            'returnExtentOnly': 'false',
            'returnQueryGeometry': 'false',
            'returnDistinctValues': 'false',
            'cacheHint': 'false',
            'returnZ': 'false',
            'returnM': 'false',
            'returnExceededLimitFeatures': 'true',
            'sqlFormat': 'none',
            'f': 'pjson',
            'token': ''
        }
        res = get(f'{url}{urlencode(params)}').json()
        f_text_list = []
        for feature in res['features']:
            attributes = feature['attributes']
            f_text = f'''🏠: {attributes['SpecifiedPremises_EN']}
💥: {attributes['Status_Cal']}
📆: {attributes['Period_EN']}
🔔: {attributes['Deadline_EN']}
📻: {attributes['URL_ZH_CAL'].split('"')[1]}
            '''
            f_text_list.append(f_text)
        return f_text_list

    def covidinfo_ny(self) -> list:
        res = self.get_covid_info('盛鼎閣')
        return res
        
    def covidinfo_ll(self) -> list:
        res = self.get_covid_info('喜翠樓')
        return res

    def covidinfo(self, arg) -> list:
        res = self.get_covid_info(arg[0])
        return res

    def healthcheck(self):
        return 'Lilony_bot: ONLINE'

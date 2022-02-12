from requests import get, post


class TelegramAPI:
    def __init__(self,
        botid:str='5150682044:AAHOOBOS28DVmiJmeHkS_nRVGEPI1gp674I',
        chatid: str='-748063135',
        update_limit: int=10
    ) -> None:
    
        self.botid = botid
        self.chatid = chatid
        self.update_limit = update_limit
        self.base_url = f'https://api.telegram.org/bot{self.botid}/' 
        pass

    def get_updates(self):
        res = get(f'{self.base_url}getUpdates')
        return res.json()

    def send_message(self, text):
        params = {
            'chat_id': self.chatid,
            'text': text
        }
        res = get(f'{self.base_url}sendMessage', params=params)
        return res

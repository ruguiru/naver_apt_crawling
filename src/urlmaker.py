import os.path
import sys

# 상위 패키지의 경로를 얻어옵니다.
current_file = os.path.abspath(__file__)  # 현재 스크립트 파일의 절대 경로
current_directory = os.path.dirname(current_file)  # 현재 스크립트 파일이 있는 디렉토리
parent_directory = os.path.dirname(current_directory)  # 상위 패키지 디렉토리

# sys.path에 상위 패키지 경로를 추가합니다.
sys.path.append(parent_directory)

from src.config import Config

class UrlMaker:
    init_url = 'https://new.land.naver.com/'

    location_url = '?ms=37.5629065,126.9946818,16'
    base_url = 'https://new.land.naver.com/complexes'
    append_url = ''
    tail_url = '&ad=false'

    def __init__(self) -> None:
        pass

    def __init__(self, conf: Config) -> None:
        self.make(conf)
        pass

    def make(self, conf: Config):
        self.append_saletype(conf.apartment, conf.officetel)
        self.append_tradetype(conf.maemae, conf.jeonse, conf.wolse)
        self.append_price(conf.min_price, conf.max_price, conf.wolse_min_price, conf.wolse_max_price)
        self.append_area(conf.min_area, conf.max_area)
        self.append_years(conf.min_year, conf.max_year)
        self.append_rooms(conf.room_cnt, conf.bathroom_cnt)
        pass

    def append_saletype(self, apt, opst):
        suburl = '&a='
        if apt == True:
            suburl += 'APT:'
        if opst == True:
            suburl += 'OPST:'

        if len(suburl) > 3:
            suburl = suburl[:-1]
            self.append_url += suburl            
        pass

    def append_tradetype(self, maemae, jeonse, wolse):
        suburl = '&b='
        if maemae == True:
            suburl += 'A1:'
        if jeonse == True:
            suburl += 'B1:'
        if wolse == True:
            suburl += 'B2:'

        if len(suburl) > 3:
            suburl = suburl[:-1]
            self.append_url += suburl        
        pass

    def append_price(self, min, max, wolse_min, wolse_max):
        suburl = ''
        if min > 0:
            suburl += f'&f={min}'
        if max > 0:
            suburl += f'&g={max}'

        if wolse_min > 0:
            suburl += f'&c={min}'
        if wolse_max > 0:
            suburl += f'&d={max}'

        suburl += '&e=RETAIL'
        self.append_url += suburl
        pass

    def append_area(self, min, max):
        suburl = ''
        if min > 0:
            min *= 3.3
            suburl += f'&h={min}'
        if max > 0:
            max += 10
            max *= 3.3
            suburl += f'&i={max}'

        self.append_url += suburl
        pass

    def append_years(self, min, max):
        suburl = ''
        if min > 0:
            suburl += f'&k={min}'
        if max > 0:
            suburl += f'&j={max}'

        self.append_url += suburl
        pass

    def append_rooms(self, room_cnt, bathroom_cnt):
        suburl = ''
        if room_cnt == 1:
            suburl += '&q=ONEROOM'
        elif room_cnt == 2:
            suburl += '&q=TWOROOM'
        elif room_cnt == 3:
            suburl += '&q=THREEROOM'
        elif room_cnt >= 4:
            suburl += '&q=FOURROOM'

        if bathroom_cnt == 1:
            suburl += '&r=ONEBATH'
        elif bathroom_cnt == 2:
            suburl += '&r=TWOBATH'
        elif bathroom_cnt == 3:
            suburl += '&r=THREEBATH'
        elif bathroom_cnt >= 4:
            suburl += '&r=FOURBATH'

        self.append_url += suburl
        pass

    def set_location_url(self, spot):
        self.location_url = '?' + spot

    def url(self):
        return self.base_url + self.location_url + self.append_url + self.tail_url
    
    def startingUrl(self):
        return self.init_url
    
    pass

if __name__ == '__main__':
    full_path = os.getcwd() + '\\config.ini'
    conf = Config(full_path)

    urlmaker = UrlMaker(conf)
    print(urlmaker.url())

    pass

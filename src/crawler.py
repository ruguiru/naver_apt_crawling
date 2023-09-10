
import os.path
import sys
import re
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import datetime
import traceback

# 상위 패키지의 경로를 얻어옵니다.
current_file = os.path.abspath(__file__)  # 현재 스크립트 파일의 절대 경로
current_directory = os.path.dirname(current_file)  # 현재 스크립트 파일이 있는 디렉토리
parent_directory = os.path.dirname(current_directory)  # 상위 패키지 디렉토리

# sys.path에 상위 패키지 경로를 추가합니다.
sys.path.append(parent_directory)

from src.config import Config
from src.urlmaker import UrlMaker
from src.filter import *
from src.log import Log

class Crawler:
    def __init__(self, conf_file) -> None:
        self.conf_file = conf_file
        self.brower = webdriver.Chrome(options=self.options())

        self.caching_data = set()
        pass

    def options(self):
        ops = Options()
        ops.add_argument("--start-maximized")
        ops.add_argument("--headless-new")
        ops.add_experimental_option("detach", True)
        return ops
    
    def path(self):
        if __name__ == '__main__':
            return parent_directory
        else:
            return os.getcwd()
    
    def find_location(self, cur_url):
        pattern = r'\?(.*?)&'
        result = re.search(pattern, cur_url)
        return result.group(1)
    
    def parsing_table(self, input):
        soup = BeautifulSoup(self.brower.page_source, 'html.parser')
        table = soup.find(input)
        for row in table.find_all('tr'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['th', 'td']):
                    row_data.append(cell.text.strip())
                # 만약 테이블의 열 수가 4개인 경우, 2개씩 나누어 새로운 행을 생성합니다.
                if len(row_data) == 4:
                    table_data.append(row_data[:2])
                    table_data.append(row_data[2:])
                else:
                    table_data.append(row_data)

            return dict(table_data)
        pass
    
    def extract_price(self, text: str):
        text = text.replace(' ', '')
        dealtype = text[:2]
        text = text[2:]
        price = 0
        wolse = 0
        price_str = ''
        if dealtype == '월세':
            wolse_str = text.replace(',', '')
            if wolse_str.find('/') != -1:
                parts = wolse_str.split('/')
                price_str = parts[0]
                wolse = int(parts[1])
            else:
                wolse = int(wolse_str)
                return dealtype, price, wolse
        else:
            price_str = text.split('(')[0].replace(',', '')

        if price_str.find('억') != -1:
            parts = price_str.split('억')
            if parts[1]:
                price = int(parts[0]) * 10000 + int(parts[1])
            else:
                price = int(parts[0]) * 10000
        else:
            price = int(price_str)

        return dealtype, price, wolse
    
    def extract_detail(self, info_dic: dict):
        room_cnt_str = info_dic['방수/욕실수'][0]
        room_cnt = int(room_cnt_str) if room_cnt_str != '-' else 0
        bathroom_cnt_str = info_dic['방수/욕실수'][2]
        bathroom_cnt = int(bathroom_cnt_str) if bathroom_cnt_str != '-' else 0
        area_str = ''
        if info_dic.get('공급/전용면적') != None:
            area_str = str(info_dic['공급/전용면적'])
        elif info_dic.get('계약/전용면적') != None:
            area_str = str(info_dic['계약/전용면적'])
                
        area = float(area_str.split('㎡/')[0].strip())

        return room_cnt, bathroom_cnt, area
    
    def search_building(self, input):
        input_box = self.brower.find_element(By.CSS_SELECTOR, '.search_input')
        input_box.send_keys(input)
        input_box.send_keys(Keys.RETURN)
        pass

    def is_duplicated(self, name, price, spec):
        if (name, price, spec) in self.caching_data:
            return True

        self.caching_data.add((name, price, spec))
        return False
    
    def run(self):
        # 검색 조건 및 url 설정
        conf = Config(self.path() + '\\' + self.conf_file)
        urlmaker = UrlMaker(conf)
        logger = Log(self.path(), conf.search_str() + '_' + conf.dealtype)

        logger.info(str(conf) + '\n')

        # 네이버 부동산 초기 화면 띄우기
        self.brower.get(urlmaker.startingUrl())
        time.sleep(2)

        # 서치하는 지역으로 이동
        self.search_building(conf.search_str())
        time.sleep(2)

        # 필터 url 적용
        urlmaker.set_location_url(self.find_location(self.brower.current_url))
        self.brower.get(urlmaker.url())
        time.sleep(2)

        # 매물 보기 버튼
        active_btn = self.brower.find_element(By.XPATH, '//*[@id="region_filter"]/div/a/span[4]')
        active_btn.click()
        time.sleep(1)

        # 단지 찾기
        buildings = []
        elements = self.brower.find_elements(By.CSS_SELECTOR, '.complex_item_inner')
        for element in elements:
            # 매물 기본 정보
            title = element.find_element(By.CSS_SELECTOR, '.complex_title').text
            info_elem = element.find_element(By.CSS_SELECTOR, '.information_area')
            quantity = info_elem.find_element(By.CSS_SELECTOR, '.quantity_area')
            saletype = info_elem.find_element(By.CSS_SELECTOR, '.sale_type').text
            spans = quantity.find_elements(By.TAG_NAME, 'span')

            maemae_cnt = int(spans[1].text)
            jeonse_cnt = int(spans[3].text)
            wolse_cnt = int(spans[5].text)

            # 기본 정보에서 1차 필터링
            if not simple_filtering(conf, saletype, maemae_cnt, jeonse_cnt, wolse_cnt):
                continue

            # logger.info(f'{title} {saletype} 매매:{maemae_cnt} 전세:{jeonse_cnt} 월세:{wolse_cnt}')
            buildings.append((title, saletype))
            pass

        overlap_check_once = False

        # 단지 순회
        for building in buildings:
            # 검색창에 1차 필터링된 매물 검색
            self.search_building(conf.search_str() + ' ' + building[0])
            time.sleep(2)

            # 중복 결과 나온 경우 정확히 일치하는 매물 클릭
            panels = self.brower.find_elements(By.CSS_SELECTOR, '.search_panel')
            if panels:                
                items = panels[0].find_elements(By.CSS_SELECTOR, '.item')
                for item in items:
                    title = item.find_element(By.CSS_SELECTOR, '.title')                    
                    if title.text == building[0]:
                        item.click()
                        time.sleep(1)
                        break

            # 동일 매물 묶기 해제
            if not overlap_check_once:            
                tie_btn = self.brower.find_element(By.XPATH, '//*[@id="complexOverviewList"]/div[2]/div[1]/div[3]/div')
                if tie_btn.is_selected():
                    tie_btn.click()
                    overlap_check_once = True
                    time.sleep(1)

            # 매물 목록
            item_area = self.brower.find_element(By.CSS_SELECTOR, '.item_area')
            items = item_area.find_elements(By.CSS_SELECTOR, '.item')

            if not items:
                continue
            
            # 단지 정보 가져오기
            btn = self.brower.find_element(By.CSS_SELECTOR, 'button.complex_link')
            btn.click()
            time.sleep(1)
            date = self.parsing_table('tbody')['사용승인일']
            years = datetime.datetime.now().year - int(date[:4])

            # 스크롤
            limit = 20
            while limit <= len(items):
                action = ActionChains(self.brower)
                action.move_to_element(items[limit-1]).perform()
                time.sleep(1)
                items = item_area.find_elements(By.CSS_SELECTOR, '.item')
                limit += 20

            time.sleep(2)

            self.caching_data.clear()

            # 매물 순회
            # 가장 아래 스크롤상태에서 역으로 올라가면서 클릭해야 씹히지 않는다
            cnt = 0
            for item in reversed(items):
                try:
                    # 약식 정보로 동일매물 체크
                    name = item.find_element(By.CSS_SELECTOR, '.item_title').text
                    price_line = item.find_element(By.CSS_SELECTOR, '.price_line').text
                    info_elem = item.find_element(By.CSS_SELECTOR, '.info_area')
                    spec = info_elem.find_elements(By.CSS_SELECTOR, 'span.spec')[0].text
                    description = info_elem.find_elements(By.CSS_SELECTOR, 'span.spec')[1].text

                    spec = spec.replace(' ',  '')

                    if self.is_duplicated(name, price_line, spec):
                        # logger.info(f'[동일매물] {name} {price} {main_info}')
                        action = ActionChains(self.brower)
                        action.move_to_element(item).perform()
                        continue

                    cnt += 1

                    # 상세 정보 클릭
                    # 타 웹사이트 링크로 가는 케이스 차단
                    view_btns = item.find_elements(By.CSS_SELECTOR, 'a.label.label--cp')
                    view_btns[0].click() if view_btns else item.click()
                    time.sleep(1)
                
                    info_dic = self.parsing_table('table')
                except NoSuchElementException:
                    logger.error(f'[NoSuchElementException][{cnt}][{building[0]}] {traceback.format_exc()}')
                    continue
                except StaleElementReferenceException:
                    logger.error(f'[StaleElementReferenceException][{cnt}][{building[0]}] {traceback.format_exc()}')
                    continue

                saletype = building[1]
                dealtype, price, wolse = self.extract_price(price_line)
                room_cnt, bathroom_cnt, area = self.extract_detail(info_dic)
                keywords = extract_keywords(conf, description)

                price_str = f'{price}/{wolse}' if dealtype == '월세' else str(price)
                log_msg = f'[{cnt}] 매물:{name} 타입:{saletype} 연식:{years}년 면적:{area}m² 가격:{dealtype}{price_str} 방/욕실:{room_cnt}/{bathroom_cnt} 스펙:{spec} 키워드:{keywords}'

                # 2차 필터링
                result, reason = detail_filtering(conf, dealtype, price, wolse, area, years, room_cnt, bathroom_cnt)
                if not result:
                    logger.info(f'[필터링][{reason}] ' + log_msg)
                    continue                    

                logger.info(log_msg)
                pass # end for 매물 순회

            print(f'{building[0]} 완료')
            pass # end for 단지 순회

        logger.info('크롤링 완료!')
        pass # end run()

if __name__ == '__main__':
    mycrawler = Crawler('config.ini')
    mycrawler.run()
    pass
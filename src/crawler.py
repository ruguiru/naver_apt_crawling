
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
import time

# 상위 패키지의 경로를 얻어옵니다.
current_file = os.path.abspath(__file__)  # 현재 스크립트 파일의 절대 경로
current_directory = os.path.dirname(current_file)  # 현재 스크립트 파일이 있는 디렉토리
parent_directory = os.path.dirname(current_directory)  # 상위 패키지 디렉토리

# sys.path에 상위 패키지 경로를 추가합니다.
sys.path.append(parent_directory)

from src.config import Config
from src.urlmaker import UrlMaker
from src.filter import *

class Crawler:
    def __init__(self, conf_file) -> None:
        self.conf_file = conf_file
        pass

    def options(self):
        ops = Options()
        ops.add_argument("--start-maximized")
        ops.add_argument("--headless-new")
        ops.add_experimental_option("detach", True)
        return ops
    
    def path(self):
        if __name__ == '__main__':
            return parent_directory + '\\' + self.conf_file
        else:
            return os.getcwd() + '\\' + self.conf_file
    
    def find_location(self, cur_url):
        pattern = r'\?(.*?)&'
        result = re.search(pattern, cur_url)
        return result.group(1)

    def run(self):
        # 검색 조건 및 url 설정
        conf = Config(self.path())
        urlmaker = UrlMaker(conf)

        logger = logging.getLogger('my_logger')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.FileHandler('crawling_result.log', encoding='utf-8'))
        logger.addHandler(logging.StreamHandler())

        # 네이버 부동산 초기 화면 띄우기
        brower = webdriver.Chrome(options=self.options())
        brower.get(urlmaker.startingUrl())
        time.sleep(2)

        # 서치하는 지역으로 이동
        input_box = brower.find_element(By.CSS_SELECTOR, '#search_input')
        input_box.send_keys(conf.search_str())
        input_box.send_keys(Keys.RETURN)
        time.sleep(2)

        urlmaker.set_location_url(self.find_location(brower.current_url))
        brower.get(urlmaker.url())
        time.sleep(2)

        # 매물 보기 버튼
        active_btn = brower.find_element(By.XPATH, '//*[@id="region_filter"]/div/a/span[4]')
        active_btn.click()

        time.sleep(1)
        buildings = []
        elements = brower.find_elements(By.CSS_SELECTOR, '.complex_item_inner')
        for element in elements:
            # 매물 기본 정보
            title = element.find_element(By.CSS_SELECTOR, '.complex_title').text
            info = element.find_element(By.CSS_SELECTOR, '.information_area')
            quantity = info.find_element(By.CSS_SELECTOR, '.quantity_area')
            saletype = info.find_element(By.CSS_SELECTOR, '.sale_type').text
            spans = quantity.find_elements(By.TAG_NAME, 'span')

            maemae_cnt = int(spans[1].text)
            jeonse_cnt = int(spans[3].text)
            wolse_cnt = int(spans[5].text)

            # 기본 정보에서 1차 필터링
            if not simple_filtering(conf, saletype, maemae_cnt, jeonse_cnt, wolse_cnt):
                continue

            print(f'{title} {saletype} 매매:{maemae_cnt} 전세:{jeonse_cnt} 월세:{wolse_cnt}')

            buildings.append((title, saletype))
            pass

        for building in buildings:
            # 검색창에 1차 필터링된 매물 검색
            input_box = brower.find_element(By.CSS_SELECTOR, '#search_input')
            input_box.send_keys(conf.search_str() + ' ' + building[0])
            input_box.send_keys(Keys.RETURN)
            time.sleep(1)

            # 중복 결과 나온 경우 정확히 일치하는 매물 클릭
            panels = brower.find_elements(By.CSS_SELECTOR, '.search_panel')
            if len(panels) > 0:                
                items = panels[0].find_elements(By.CSS_SELECTOR, '.item')
                for item in items:
                    title = item.find_element(By.CSS_SELECTOR, '.title')                    
                    if title.text == building[0]:
                        item.click()
                        time.sleep(1)
                        break

            # 동일 매물 묶기 해제
            tie_btn = brower.find_element(By.XPATH, '//*[@id="complexOverviewList"]/div[2]/div[1]/div[3]/div')
            if tie_btn.is_selected():                
                tie_btn.click()
                time.sleep(1)

            # 매물 목록
            item_area = brower.find_element(By.CSS_SELECTOR, '.item_area')
            items = item_area.find_elements(By.CSS_SELECTOR, '.item')

            # 스크롤
            limit = 20
            while limit <= len(items):
                action = ActionChains(brower)
                action.move_to_element(items[limit-1]).perform()
                items = item_area.find_elements(By.CSS_SELECTOR, '.item')
                limit += 20

            cnt = 0
            # 가장 아래 스크롤상태에서 역으로 올라가면서 클릭해야 씹히지 않는다
            for item in reversed(items):
                cnt += 1

                # 상세 정보 클릭
                view_btns = item.find_elements(By.CSS_SELECTOR, 'a.label.label--cp')
                # 타 웹사이트 링크로 가는 케이스 차단
                if len(view_btns) > 0:
                    view_btns[0].click()
                else:                 
                    item.click()

                time.sleep(1.5)

                # 상세 정보 패널 크롤링

                # 매물특징
                # 공급/전용면적
                # 해당층/총층
                # 방수/욕실수
                # 월관리비
                # 관리비 포함
                # 융자금
                # 기보증금/월세
                # 방향
                # 현관구조
                # 난방(방식/연료)
                # 입주가능일
                # 총주차대수
                # 해당면적 세대수
                # 건축물 용도
                # 매물번호
                # 매물설명
                # 중개사
                soup = BeautifulSoup(brower.page_source, 'html.parser')
                table = soup.find('table')               
                info_dic = self.extract_table(table)

                id = int(info_dic['매물번호'])
                room_cnt = int(info_dic['방수/욕실수'][0])
                bathroom_cnt = int(info_dic['방수/욕실수'][2])
                area_origin = str(info_dic['공급/전용면적'])
                area = float(area_origin.split('㎡/')[0].strip())
                saletype = building[1]

                detail_panel = brower.find_element(By.CSS_SELECTOR, '.detail_panel')
                title = detail_panel.find_element(By.CSS_SELECTOR, '.info_title_wrap').text
                price_origin = detail_panel.find_element(By.CSS_SELECTOR, '.info_article_price').text
                dealtype = self.extract_dealtype(price_origin)
                price = self.extract_price(price_origin)

                # 2차 필터링
                if not detail_filtering(conf, dealtype, price, area, 0, room_cnt, bathroom_cnt):
                    logger.info(f'[필터링][{cnt}] 매물:{title} 매물번호:{id} 타입:{saletype} 면적:{area} 가격:{dealtype}/{price} 방/욕실:{room_cnt}/{bathroom_cnt}')
                    continue                    

                logger.info(f'[{cnt}] 매물:{title} 매물번호:{id} 타입:{saletype} 면적:{area} 가격:{dealtype}/{price} 방/욕실:{room_cnt}/{bathroom_cnt}')

                # 데이터 프레임화 및 DB 저장

            time.sleep(3)
            pass
        pass

    def extract_table(self, table):
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

    def extract_dealtype(self, text):
        return text[:2]
    
    def extract_price(self, text: str):
        parts = text.split('(')
        pattern = r'\d+'
        price = parts[0].strip()
        numbers = re.findall(pattern, price)
        result = ''.join(numbers)

        if price.find('억'):
            if len(numbers) == 1:
                result += '0000'

        return int(result)


if __name__ == '__main__':
    mycrawler = Crawler('config.ini')
    mycrawler.run()
    pass
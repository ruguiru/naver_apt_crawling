
import configparser
import os.path

class Config():
    def __init__(self, file):
        self.parsing(file)
        pass

    def boolean(self, data):
        if len(data) == 0:
            return False
        
        if int(data) == 0:
            return False
        
        return True
    
    def integer(self, data):
        if len(data) == 0:
            return 0

        return int(data)

    def parsing(self, file):
        config = configparser.ConfigParser()
        config.read(file, encoding='utf-8')

        # [SEARCH] 섹션 읽기
        search_section = config['SEARCH']

        self.sido = search_section.get('시도')
        self.sigungu = search_section.get('시군구')
        self.eupmyeondong = search_section.get('읍면동')

        # [FILTER] 섹션 읽기
        filter_section = config['FILTER']

        self.apartment = self.boolean(filter_section.get('아파트'))
        self.officetel = self.boolean(filter_section.get('오피스텔'))
        self.maemae = self.boolean(filter_section.get('매매'))
        self.jeonse = self.boolean(filter_section.get('전세'))
        self.wolse = self.boolean(filter_section.get('월세'))

        # 가격 범위 읽기
        self.min_price = self.integer(filter_section.get('최소가격'))
        self.max_price = self.integer(filter_section.get('최대가격'))
        self.wolse_min_price = self.integer(filter_section.get('월세최소가격'))
        self.wolse_max_price = self.integer(filter_section.get('월세최대가격'))

        # 면적 범위 읽기
        self.min_area = self.integer(filter_section.get('최소면적'))
        self.max_area = self.integer(filter_section.get('최대면적'))
        self.min_area_sq = self.min_area * 3.3
        self.max_area_sq = (self.max_area + 10) * 3.3

        # 연식 범위 읽기
        self.min_year = self.integer(filter_section.get('최소연식'))
        self.max_year = self.integer(filter_section.get('최대연식'))

        # 방수와 욕실수 읽기
        self.room_cnt = self.integer(filter_section.get('방수'))
        self.bathroom_cnt = self.integer(filter_section.get('욕실수'))

        # 키워드 읽기
        self.keywords = filter_section.get('키워드').split(',')
        pass

    def search_str(self):
        return f'{self.sido} {self.sigungu} {self.eupmyeondong}'
        pass

    pass


if __name__ == '__main__':
    full_path = os.getcwd() + '\\config.ini'
    conf = Config(full_path)
    pass
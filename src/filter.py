
from src.config import Config

def simple_filtering(conf: Config, saletype, maemae_cnt, jeonse_cnt, wolse_cnt):
    if saletype == '아파트':
        if not conf.apartment:
            return False
        
    if saletype == '오피스텔':
        if not conf.officetel:
            return False
        
    if conf.dealtype == '매매' and maemae_cnt <= 0:
        return False
    
    if conf.dealtype == '전세' and jeonse_cnt <= 0:
        return False
    
    if conf.dealtype == '월세' and wolse_cnt <= 0:
        return False
    
    return True


def detail_filtering(conf: Config, dealtype, price, wolse, area, years, room_cnt, bathroom_cnt):
    if (conf.min_price != 0 and price < conf.min_price) or (conf.max_price != 0 and price > conf.max_price):
        return False, '가격'
    
    if (conf.min_wolse != 0 and wolse < conf.min_wolse) or (conf.max_wolse != 0 and wolse > conf.max_wolse):
        return False, '월세'

    if (conf.min_area_sq != 0 and area < conf.min_area_sq) or (conf.max_area_sq !=0 and area > conf.max_area_sq):
        return False, '면적'
    
    if (conf.min_year != 0 and years < conf.min_year) or (conf.max_year != 0 and years > conf.max_year):
        return False, '연식'
    
    if conf.room_cnt != 0 and (room_cnt != conf.room_cnt):
        return False, '방수'
    
    if conf.bathroom_cnt != 0 and (bathroom_cnt != conf.bathroom_cnt):
        return False, '욕실수'

    return True, '성공'

def extract_keywords(conf: Config, etc_info: str):
    included_keywords = ''
    for keyword in conf.keywords:
        if keyword in etc_info:
            included_keywords += keyword + ','

    if included_keywords:
        included_keywords = included_keywords[:-1]

    return included_keywords
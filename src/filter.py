
from src.config import Config

def simple_filtering(conf: Config, saletype, maemae_cnt, jeonse_cnt, wolse_cnt):
    if saletype == '아파트':
        if not conf.apartment:
            return False
        
    if saletype == '오피스텔':
        if not conf.officetel:
            return False

    find = False
    if conf.maemae and maemae_cnt > 0:
        find = True

    if conf.jeonse and jeonse_cnt > 0:
        find = True

    if conf.wolse and wolse_cnt > 0:
        find = True

    return find


def detail_filtering(conf: Config, dealtype, price, area, years, room_cnt, bathroom_cnt):
    if dealtype != '월세':
        if price < conf.min_price or price > conf.max_price:
            return False
    else:
        if price < conf.wolse_min_price or price > conf.wolse_max_price:
            return False

    if area < conf.min_area_sq or area > conf.max_area_sq:
        return False
    
    if years < conf.min_year or years > conf.max_year:
        return False
    
    if room_cnt != conf.room_cnt:
        return False
    
    if bathroom_cnt != conf.bathroom_cnt:
        return False

    return True
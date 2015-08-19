#!/usr/bin/env python
import os
import sys
from django.utils import timezone
from datetime import date

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from django.core.cache import cache
from discount.models import Payment, Shop, Product, User, ProductMail, ModelHistory, ProductType
from discount import models, helper
from discount import tasks
from collections import OrderedDict
from django.db.models import Q
from urllib.request import urlopen


#s = Shop.objects.get(pk=2)

s = models.Shop.objects.get(pk=59)
#print(s)


l = [
"D-1-15-19,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_kokteylnie_platya/d-1-15-19-zhenskoe-plate/",
"D-1-15-22,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d-1-15-22-zhenskoe-plate/",
"D-1-15-30,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d-1-15-30-zhenskoe-plate/",
"D-1-15-35,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d-1-15-35-zhenskoe-plate/",
"D15-300,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_platya_na_vipusknoy/d15-300-zhenskoe-plate/",
"D15-301,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d15-301-zhenskoe-plate/",
"D15-336,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_kokteylnie_platya/d15-336-zhenskoe-plate/",
"D15-338,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d15-338-zhenskoe-plate/",
"D15-359,1499,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_platya_na_vipusknoy/d15-359-zhenskoe-plate/",
"D15-398,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-398-zhenskoe-plate/",
"D15-400,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-400-zhenskoe-plate/",
"D15-405,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d15-405-zhenskoe-plate/",
"D15-423,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/d15-423-zhenskoe-plate/",
"D15-438,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_kokteylnie_platya/d15-438-zhenskoe-plate/",
"D15-439,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_kokteylnie_platya/d15-439-zhenskoe-plate/",
"D15-446,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-446-zhenskoe-plate/",
"D15-477,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d15-477-zhenskoe-plate/",
"D15-503,2199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-503-zhenskoe-plate/",
"D15-506,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-506-zhenskoe-plate/",
"D15-506-1,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-506-1-zhenskoe-plate/",
"D15-517,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-517-zhenskoe-plate/",
"D15-532,1499,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d15-532-zhenskoe-plate/",
"D15-535,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/d15-535-zhenskoe-plate/",
"D15-539,1499,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d15-539-zhenskoe-plate/",
"D15-550,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/d15-550-zhenskoe-plate/",
"D15-552,1599,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_kokteylnie_platya/d15-552-zhenskoe-plate/",
"D15-563,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d15-563-zhenskoe-plate/",
"D15-595,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d15-595-zhenskoe-plate/",
"D3008,1499,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_delovie_platya/d3008-zhenskoe-plate/",
"D3027,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_delovie_platya/d3027-zhenskoe-plate/",
"D3033,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d3033-zhenskoe-plate/",
"D3042,1599,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_delovie_platya/d3042-zhenskoe-plate/",
"D3043,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/d3043-zhenskoe-plate/",
"D3045,1599,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_kokteylnie_platya/d3045-zhenskoe-plate/",
"D3046,1599,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_vechernie_platya/d3046-zhenskoe-plate/",
"D3047,1599,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/d3047-zhenskoe-plate/",
"DR-1-15-10,799,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/dr-1-15-10-zhenskoe-plate/",
"DR-1-15-24,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/dr-1-15-24-zhenskoe-plate/",
"DR15-349,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/dr15-349-zhenskoe-plate/",
"DR15-353,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/dr15-353-zhenskoe-plate/",
"DR15-377,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_delovie_platya/dr15-377-zhenskoe-plate/",
"DR15-415,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/dr15-415-zhenskoe-plate/",
"DR15-447,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/dr15-447-zhenskoe-plate/",
"DR15-480,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/dr15-480-zhenskoe-plate/",
"DR15-558,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/dr15-558-zhenskoe-plate/",
"DR15-568,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/dr15-568-zhenskoe-plate/",
"DR6018,1499,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_delovie_platya/dr6018-zhenskoe-plate/",
"DR6019,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/dr6019-zhenskoe-plate/",
"DR6020,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/dr6020-zhenskoe-plate/",
"DR6021,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_vechernie_platya/dr6021-zhenskoe-plate/",
"DR6024,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_korotkie_platya/dr6024-zhenskoe-plate/",
"DR6030,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_letnie_platya/dr6030-zhenskoe-plate/",
"DR6077,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/dr6077-zhenskoe-plate/",
"DR6080,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_platya_dlinnie_platya/dr6080-zhenskoe-plate/",
"L-1-15-01,599,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l-1-15-01-zhenskaya-bluzka/",
"L-1-15-02,599,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l-1-15-02-zhenskaya-bluzka/",
"L15-355,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-355-zhenskaya-bluzka/",
"L15-373,399,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-373-zhenskaya-bluzka/",
"L15-404,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-404-zhenskaya-bluzka/",
"L15-412,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-412-zhenskaya-bluzka/",
"L15-425,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-425-zhenskaya-bluzka/",
"L15-426,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-426-zhenskaya-bluzka/",
"L15-451,499,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-451-zhenskaya-bluzka/",
"L15-453,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-453-zhenskaya-bluzka/",
"L15-514,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-514-zhenskaya-bluzka/",
"L15-554,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l15-554-zhenskaya-bluzka/",
"L3001,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3001-zhenskaya-bluzka/",
"L3002,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3002-zhenskaya-bluzka/",
"L3003,1299,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3003-zhenskaya-bluzka/",
"L3004,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3004-zhenskaya-bluzka/",
"L3005,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3005-zhenskaya-bluzka/",
"L3006,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3006-zhenskaya-bluzka/",
"L3007,1399,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3007-zhenskaya-bluzka/",
"L3022,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3022-zhenskaya-bluzka/",
"L3023,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3023-zhenskaya-bluzka/",
"L3024,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3024-zhenskaya-bluzka/",
"L3025,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3025-zhenskaya-bluzka/",
"L3026,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3026-zhenskaya-bluzka/",
"L3030,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3030-zhenskaya-bluzka/",
"L3031,1199,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3031-zhenskaya-bluzka/",
"L3032,799,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3032-zhenskaya-bluzka/",
"L3035,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3035-zhenskaya-bluzka/",
"L3048,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_bluzki_bluzki/l3048-zhenskaya-bluzka/",
"LD15-392,499,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld15-392-dzhemper-zhenskiy/",
"LD6004V,799,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6004v-dzhemper-zhenskiy/",
"LD6005,799,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_vodolazki/ld6005-dzhemper-zhenskiy/",
"LD6006,899,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6006-dzhemper-zhenskiy/",
"LD6007,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6007-dzhemper-zhenskiy/",
"LD6008,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6008-dzhemper-zhenskiy/",
"LD6010,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6010-dzhemper-zhenskiy/",
"LD6010-1,999,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6010-1-dzhemper-zhenskiy/",
"LD6011,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6011-dzhemper-zhenskiy/",
"LD6013,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6013-dzhemper-zhenskiy/",
"LD6014,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6014-dzhemper-zhenskiy/",
"LD6015,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6015-dzhemper-zhenskiy/",
"LD6024,799,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6024-dzhemper-zhenskiy/",
"LD6028,699,http://visavis-fashion.ru/catalog/dlya_zhenschin_trikotazh_dzhemper/ld6028-dzhemper-zhenskiy/",


]


for e in l:
    e = e.split(',')
    #print(e)
    product_shop_code, stock_price, link = e

    try:
        opened = urlopen(link)
    except:
        opened = None

    p = s.products.get(product_shop_code=product_shop_code)
    now_price = p.stock_price
    p.stock_price = int(round(int(stock_price) * 0.95))
    p.use_code_postfix = False
    if opened is None:
        p.status = models.STATUS_FINISHED
    else:
        p.link = link

    print(now_price, stock_price, p.stock_price, p.status_text)
    p.save()


"""
for p in s.products.all():
    old_stock_price = p.stock_price
    old_percent = p.get_percent()
    delta = p.normal_price * 0.015
    p.stock_price = helper.myround(p.stock_price - delta)
    print(old_stock_price, old_percent, p.stock_price, p.get_percent())
    p.save()
"""

"""
for p in s.products.all():
    p.use_simple_code = True
    p.use_code_postfix = False
    p.simple_code = 'TATAMO'
    p.end_date = date(day=15, month=9, year=2015)
    p.save()
    print(p, p.simple_code)

"""

"""
for p in s.products.filter(status=models.STATUS_TO_APPROVE):
    p.status = models.STATUS_NEED_REWORK
    p.save()
"""
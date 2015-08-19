import os
import sys
from django.utils import timezone
from datetime import date

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from discount.load_products import ProductLoader
from discount import models
from io import StringIO

line_as_list = []
line_as_list.append('500')
line_as_list.append('200')
line_as_list.append('8080')
line_as_list.append('01.08.2015')
line_as_list.append('15.08.2015')
line_as_list.append('Бренд-145')
line_as_list.append('1')
line_as_list.append('2')
line_as_list.append('3')
line_as_list.append('4')
line_as_list.append('зеленый, синий, белый')
line_as_list.append('38, 40, 42')
line_as_list.append('1.jpg, 2.jpg')

line = ';'.join(line_as_list)


shop = models.Shop.objects.get(pk=1658)
user = models.User.objects.get(username='kulik')


file = StringIO(line)

l = ProductLoader(file, shop, user)

l.load()
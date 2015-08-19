import os
import sys
from django.utils import timezone
from datetime import date
from PIL import Image


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kulik.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


from discount import models

pts = models.ProductType.objects.filter(has_childs=False)

for pt in pts:
    if pt.level == 3:
        print('{0}|{1}|{2}|{3}'.format(pt.parent.parent, pt.parent, pt, pt.pk))
    else:
        print('{0}|{1}|{2}'.format(pt.parent, pt, pt.pk))



print('***********Цвета***************')
fvs = models.FilterValue.objects.filter(filter_type=models.FILTER_TYPE_COLOR)
for fv in fvs:
    print(fv)


print('**********Мужские размеры************')
fvs = models.FilterValue.objects.filter(filter_type=models.FILTER_TYPE_SIZE_MAN)
for fv in fvs:
    print(fv)

print('**********Женские размеры************')
fvs = models.FilterValue.objects.filter(filter_type=models.FILTER_TYPE_SIZE_WOMAN)
for fv in fvs:
    print(fv)

print('**********Детские размеры************')
fvs = models.FilterValue.objects.filter(filter_type=models.FILTER_TYPE_SIZE_CHILDS)
for fv in fvs:
    print(fv)

print('**********Размеры обуви************')
fvs = models.FilterValue.objects.filter(filter_type=models.FILTER_TYPE_SIZE_SHOES)
for fv in fvs:
    print(fv)
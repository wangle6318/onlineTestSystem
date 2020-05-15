from django.conf import settings
from django.shortcuts import Http404
import time
import os


class SaveImg:

    def get_img_path(self, parent):
        current_time = time.localtime()
        year = str(current_time.tm_year)
        month = str(current_time.tm_mon)
        img_path = parent + '\\' + year + '\\' + month + '\\'
        path = os.path.join(settings.MEDIA_ROOT, img_path)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def img_save(self, file, root):
        save_path = self.get_img_path(root)
        img_suffixes = ['jpg', 'jpeg', 'png', 'gif', 'jfif', 'bmp']
        from uuid import uuid1
        img_suffix = file.name.split(".")[-1]
        if img_suffix.lower() not in img_suffixes:
            img_suffix = 'jpg'
        file_name = str(uuid1()) + "." + img_suffix
        save_path = save_path + file_name
        with open(save_path, 'wb') as img:
            for f in file.chunks():
                img.write(f)
        return save_path

    def excel_save(self, file, root):
        save_path = self.get_img_path(root)
        img_suffixes = ['xlsx', 'xls']
        from uuid import uuid1
        img_suffix = file.name.split(".")[-1]
        if img_suffix.lower() not in img_suffixes:
            raise Http404
        file_name = str(uuid1()) + "." + img_suffix
        save_path = save_path + file_name
        with open(save_path, 'wb') as img:
            for f in file.chunks():
                img.write(f)
        return save_path

    def delete_question_img(self, path):
        path = os.path.join(settings.MEDIA_ROOT, path)
        try:
            os.remove(path=path)
        except FileExistsError:
            pass
from uuid import uuid4
from flask import *
import os
import traceback
import models
from models import get_uid
import pandas as pd
import numpy as np

# class :: Book
class Project():
    id, uid, title, fil = None, None, None, None

    # constructor
    def __init__(self, user_id, title, src, write_disc=True):
        self.id =str(get_uid())
        self.uid = user_id
        self.title = title
        self.fil = src
        # Create book folder
        if write_disc:
            base = os.path.join('instance', self.id)
            os.makedirs(base, exist_ok=True)

            config = os.path.join(base, 'anxconfig.anx')
            resource = os.path.join(base, 'anxresource.anx')
            # write config file
            with open(config, 'w') as file:
                file.write(f"{self.id}\n{self.uid}\n{self.title}\n")

            # write resource file
            with open(resource, 'w') as file:
                file.write('')

            # save cover image
            if src is not None:
                # save image

                cid = self.id + os.path.splitext(src.filename)[1]
                self.fil = cid
                src.save(os.path.join(base, cid)) # save the file with the name.
                with open(config, 'a') as file:
                    file.write(cid + '\n')

    # static method :: write a new scene
    @staticmethod
    def write_scene(bid, data, image=None):
        scene_id = get_uid()
        if data != '':
            base = os.path.join('instance', bid)
            resource = os.path.join(base, 'anxresource.anx')
            # Save the file to a specific directory
            # with open(base, 'w') as file:
            #     file.write(data)
            if image is not None:
                # save image
                simg_id = scene_id + os.path.splitext(image.filename)[1]
                image.save(os.path.join(base, simg_id))
                with open(resource, 'a') as file:
                    file.write(simg_id + ',')

            scene_text_filename = os.path.join(base, scene_id + '.txt')
            with open(scene_text_filename, 'w') as file:
                file.write(data)
            # write resource file
            with open(resource, 'a') as file:
                file.write(scene_id + '.txt' + '\n')
            return 'Scene uploaded successfully'
        else:
            return 'No file selected'


    # static method :: update a scene from the book
    @staticmethod
    def update_scene(bid,index, data, image=None):
        index = eval(index)
        if data != '':
            base = os.path.join('instance', bid)
            resource = os.path.join(base, 'anxresource.anx')
            # Save the file to a specific directory
            # with open(base, 'w') as file:
            #     file.write(data)
            sid = None
            list  = None
            with open(resource, 'r') as res:
                list =  res.read().split('\n')
                smth = list[index].split(',')
                if len(smth) >1:
                    sid = smth[1]
                else:
                    sid = list[index]

            # if image exist
            if image is not None:
                # save image
                simg_id = sid.replace('.txt', '') + os.path.splitext(image.filename)[1]
                list[index] = simg_id
                image.save(os.path.join(base, simg_id))


            scene_text_filename = os.path.join(base, sid )
            with open(scene_text_filename, 'w') as file:
                file.write(data)
                if image != None:
                    list[index] = list[index] +f',{sid}'

                # write updates resource file
                with open(resource, 'w') as file:
                    file.write('\n'.join(list))
            return 'Scene updated successfully'
        else:
            return 'No file selected'


    # static method :: update book details
    @staticmethod
    def updateBook(bid, title, fil):
        base = os.path.join('instance', bid)


        config = os.path.join(base, 'anxconfig.anx') # get path
        resource = os.path.join(base, 'anxresource.anx') # get path
        # write config file
        with open(config, 'r') as file:
            list = file.read().split('\n')
            list[2] = title
            length = len(list)
            if fil:
                 list[3] = bid + os.path.splitext(fil.filename)[1]+ '\n'

        with open(config, 'w') as file:
            text = '\n'.join(list)
            file.write(text)


        # save cover image
        if fil:
            # save image

            cid = bid + os.path.splitext(fil.filename)[1]
            fil.save(os.path.join(base, cid))  # save the file with the name.


    # static methods
    # get a book from id
    @staticmethod
    def getBook(bid):
        folder = os.path.join('instance', bid)
        config = os.path.join(folder, 'anxconfig.anx')
        book = None
        bookJson = None
        with open(config, 'r') as file: # open in config file
            data = file.read()
            list = data.split("\n")
            uid = list [1]
            title = list [2]
            img = list [3]
            book = Project(uid, title, img, False)
            bookJson = {'uid':uid, 'title':book.title, 'bid':bid, 'fil':book.fil}

        return bookJson # return book json


    # static method :: get Image of the book
    @staticmethod
    def getImage(bid):
        print(bid)
        folder = os.path.join('instance', bid)
        config = os.path.join(folder, 'anxconfig.anx')
        with open(config, 'r') as file: # open book config file
            data = file.read()
            list = data.split("\n")
            image = list[3]
            try:
                with open(os.path.join(folder,image), 'r') as imgc:
                    print(image)
                    imgg = os.path.join(folder, image)
                    return send_file(imgg, mimetype='image/*') # get image and return
            except:
                return ''


    # static method :: get scene from server
    @staticmethod
    def getScene(bid, index):
        folder = os.path.join('instance', bid)
        res = os.path.join(folder, 'anxresource.anx')
        with open(res, 'r') as file: # resource file is opened
            data = file.read()
            list = data.split('\n')
            print(list)
            if len(list) == 0 or list[0] == '':
                return {'text':'', 'img':None} # image does not exist
            else:
                try:
                    name = list[eval(index)]
                    list1 = name.split(',')
                    if len(list1) >1:
                        imgName = list1[0]
                        textName = list1[1]
                        with open(os.path.join(folder, textName), 'r') as textfile:
                            textData = textfile.read()
                            print({'text':textData, 'img': imgName})
                            return {'text':textData, 'img': imgName} # return whole scene with image name in it
                    else:
                        with open(os.path.join(folder, list1[0]), 'r') as textfile:
                            textData = textfile.read()
                            return {'text':textData, 'img': None}

                except:
                    return {'text': '', 'img': None}


    # static method :: get cover image of the scene
    @staticmethod
    def getSceneImage(bid, sid):
        bookFolder = os.path.join('instance', bid)
        scene_id_path = os.path.join(bookFolder, sid)
        img_file = None
        with open(scene_id_path, 'r') as img: # open image scene

            imgg = (scene_id_path)
            return send_file(imgg, mimetype='image/*')
        return img_file


    # static method :: get latest scene text
    @staticmethod
    def getSceneLatest(bid):
        bookFolder = os.path.join('instance', bid)
        res = os.path.join(bookFolder, 'anxresource.anx')
        with open(res, 'r') as file: # open resource file
            data  = file.read()
            list = data.split("\n")
            length = len(list)
            if length == 1:
                return {'index':length- 1 }
            else:
                return {'index':length -2 }


    # static method :: add book to the event
    @staticmethod
    def add_like(bid, uid):
        bookFolder = os.path.join('instance', bid)
        fav = os.path.join(bookFolder, 'fav.anx') # favourites file
        with open(fav, 'a') as file:
            with open(fav, 'r') as fileread:
                data = fileread.read()
                list = data.split('\n')
                print(list)
                if uid in data:
                    print('already')
                    return 'already liked'
                else:
                    file.write(uid+'\n')
                    return 'added to liked'


    # static method :: add book to the event
    @staticmethod
    def get_likes(bid):
        bookFolder = os.path.join('instance', bid)
        fav = os.path.join(bookFolder, 'fav.anx')  # favourites file
        try:
            with open(fav, 'r') as file:
                data = file.read()
                list = data.split('\n')
                return len(list) - 1
        except:
            return 0


    # static method :: add book to the event
    @staticmethod
    def add_book_to_event(bid):
        doc = os.path.join('instance', 'event')
        eve = os.path.join(doc, 'eve.anx')  # event file
        try:
            with open(eve, 'a') as file:
                data = file.write(bid+'\n')
                return 'success'
        except:
            return 'smth has happened'


    # get project info
    @staticmethod
    def get_project_details(bid):
        base = os.path.join('instance', bid)
        filename = os.path.join(base,bid + '.csv')
        try:
            with open(filename, 'r') as file:

                text = file.read().replace('ï»¿','')
                first_line = text.split('\n')[0]
                list = first_line.split(',')
                count = 0
                lines = text.split('\n')
                for i in range(len(text.split('\n'))):
                    if lines[i] != '':
                        count+=1

                return {'status':1, 'attributes': list, 'len':count-1}
        except:
            return {'status':0, 'message':'empty file'}

        #
    @staticmethod
    def get_project_rows_len(lens, bid):
        base = os.path.join('instance', bid)
        filename = os.path.join(base, bid + '.csv')
        try:
            with open(filename, 'r') as file:
                text = file.read().replace('ï»¿','')
                df = pd.read_csv(filename)
                first_line = text.split('\n')[0]
                list = first_line.split(',')
                rows = []
                lines = text.split('\n')
                leng = len(lines)
                count = 0
                for i in range(1, leng):
                    if lines[i] != '':
                        row = lines[i].split(',')
                        rowPro = {}
                        for att in range(len(list)):
                            item = df[list[att]][i-1]
                            list[att] = list[att].replace('ï»¿', '')

                            rowPro[list[att]] = str(item)
                        rows.append(rowPro)
                        count+=1
                    if count>1501:
                        break

                return {'status': 1, 'attributes': list, 'len': count, 'rows':rows}
        except Exception:
            traceback.print_exc()
            return {'status': 0, 'message': 'empty file'}

    @staticmethod
    def change_cell (value, column, index, bid):
        base = os.path.join('instance', bid)
        filename = os.path.join(base, bid + '.csv')
        try:
            with open(filename, 'r') as file:
                text = file.read().replace('ï»¿', '')
                df = pd.read_csv(filename)
                df.at[index, column] = value
                df.to_csv(filename, index = False) # No indexing
                return 'success'

        except:
            return 'file deleted', 404

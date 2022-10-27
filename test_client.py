import os
import json
import requests
from glob import glob 
from datetime import datetime
import cv2
import numpy as np
import base64
from app.mod_service.custom_utils import read_json

# damaged location
# top_left : t_l
# top_right : t_r
# bottom_right : b_r
# bottom_left : b_l

part_info = {
            'back_door':['left','right'],
            'front_bumper':['left','right'],
            'front_door_left':['top_left','top_right','bottom_right','bottom_left'],                           
            'front_door_right':['top_left','top_right','bottom_right','bottom_left'],
            'front_fender_left':['left','right'],
            'front_fender_right':['left','right'],
            'front_fog_left':['all'],
            'front_fog_right':['all'],
            'front_lamp_left':['all'],
            'front_lamp_right':['all'],
            'grille_up':['left','right'],
            'hood':['left','right'],
            'rear_bumper':['left','right'],
            'rear_door_left':['top_left','top_right','bottom_right','bottom_left'],
            'rear_door_right':['top_left','top_right','bottom_right','bottom_left'],
            'rear_fender_left':['left','right'],
            'rear_fender_right':['left','right'],
            'rear_lamp_left':['all'],
            'rear_lamp_right':['all'],
            'rear_stop_center':['all'],
            'rear_stop_left':['all'],
            'rear_stop_right':['all'],
            'side_mirror_left':['all'],
            'side_mirror_right':['all'],
            'side_step_left':['all'],
            'side_step_right':['all'],
            'trunk':['left','right'],
            'znumber_plate':['all']
}


class PredictTest():

    def __init__(self, url='localhost', port='8088'):
        self.gateway_url = f"http://{url}:{port}/api/compare/"


    def compare(self, jsonfilepath_1, jsonfilepath_2, save_json_dir=None):

        def save_json(config, config_path):
            """
            dict 형태의 데이터를 받아 json파일로 저장해주는 함수
            """
            now = datetime.now()

            result_output_dir='{}'.format(config_path)
            json_dir = os.path.join(result_output_dir, "json")
            os.makedirs(json_dir, exist_ok=True)
            save_path = os.path.join(json_dir, str(now.date())+ "_"+ str(int(round(now.timestamp(),0)))+".json")
                    
            def default(obj):
                if type(obj).__module__ == np.__name__:
                    if isinstance(obj, np.ndarray):
                        # return obj.tolist()
                        return []
                    else:
                        return []
                # raise TypeError('Unknown type:', type(obj))

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4, default=default)


        json_data_1 = read_json(jsonfilepath_1)
        json_data_2 = read_json(jsonfilepath_2)

        filedata = {"jsondata1":json_data_1,
                    "jsondata2":json_data_2,
                    "partinfo":part_info}

        r = requests.request('POST', self.gateway_url, json=filedata)
        if r.status_code == 200:
            rest = json.loads(r.content)
            if save_json_dir:
                save_json(rest, save_json_dir)
            # print(rest)
            if 'results' in rest.keys() and rest['results'] == 'success':
                print('test ok')
            else:
                r.raise_for_status()
        else:
            print('Failed prediction request ' + str(r.status_code))
            r.raise_for_status()

if __name__ == "__main__":

    from pprint import pprint

    json_file_1 = "./test_json/2022-10-26_1666748273.json"
    json_file_2 = "./test_json/2022-10-26_1666748326.json"

    tester = PredictTest()
    tester.compare(
        jsonfilepath_1=json_file_1,
        jsonfilepath_2=json_file_2,
        save_json_dir="./output/result_json/")
    

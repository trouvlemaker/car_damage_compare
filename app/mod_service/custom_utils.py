import cv2
import json
import numpy as np
from pycocotools.mask import encode, decode

# import matplotlib.pyplot as plt
# from pprint import pprint

def change_polygon(original_shape, new_shape, single_polygon):
    """
    1번 이미지의 shape에 맞춰진 4 point polygon 박스의 좌표를 받아서
    2번 이미지의 shape에 같은 비율의 위치에 맞춰지게 변경해주는 함수

    Input:
        original_shape : 1번 이미지의 shape
        new_shape : 2번 이미지의 shape
        single_polygon : [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], [4,2] shape의 polygon box

    Output:

        new_coord: 2번 이미지에 맞게 변경된 4 point polygon
    """

    y_, x_ = original_shape

    target_y, target_x = new_shape
    x_scale = target_x / x_
    y_scale = target_y / y_

    # original frame as named values

    a, b, c, d = single_polygon

    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    x4, y4 = d

    new_coord = np.array([
        [x1, y1],
        [x2, y2],
        [x3, y3],
        [x4, y4],
    ]) * np.array([x_scale, y_scale])

    return np.array(new_coord)

def decode_mask_to_rle(masksize, maskrles):

    masks = []

    for size, rle in zip(masksize, maskrles):

        decode_string = rle[0]

        rle_dict = {"size":size, "counts":decode_string}
        
        mask = decode(rle_dict)
        masks.append(mask)
    masks = np.array(masks).astype(np.bool_)
    
    return masks.transpose(1,2,0)

def read_json(config_path):
    """
    json 파일을 읽어 dict 형태로 반환해주는 함수
    """
    with open(config_path, encoding="utf-8-sig") as json_file:
        json_data = json.load(json_file)
    return json_data

def save_json(config, config_path):
    """
    dict 형태의 데이터를 받아 json파일로 저장해주는 함수
    """
    with open(config_path, "w", encoding="utf-8-sig") as f:
        json.dump(config, f, ensure_ascii=False)  


def create_damage_info_container(part_info): 
    container = dict()
    
    for part_name, value in part_info.items():
        
        container[part_name] = {
            "damage_type":[],
            "damage_location":[],
            "damage_ratio":[]
        }
        
    return container

def check_damage_location(p_mask, d_box, d_area, d_ratio):
    '''
    damage box의 네 좌표를 part_mask의 center 좌표와 비교해서 
    damage가 part의 4분할 위치에서 어디에 걸쳐있는지 판정
    
    4분면은 top-left 부터 시계방향으로 1,2,3,4 분면으로 정의

    판정 부위가 2부위일 경우 좌우로 return
    
    '''
    loc_re = []
    if len(d_area) == 4:
        A,B,C,D = d_box
        x,y,w,h = cv2.boundingRect(p_mask.astype(np.uint8))
        px, py = (x + w/2, y + h/2)
        loc_re = []
        
        for point in [A,B,C,D]:
            dx,dy = point
            
            if px > dx and py > dy:
                loc = 1
            elif px < dx and py > dy:
                loc = 2
            elif px < dx and py < dy:
                loc = 3
            else:
                loc = 4
            # print(loc)
            loc_re.append(loc)
        if loc_re == [1,2,3,4] and d_ratio >= 0.5:
            loc_re = ["all"]
        elif loc_re == [1,2,3,4] and d_ratio < 0.5:
            loc_re = ["center"]
        else:
            loc_re = list(set([d_area[x-1] for x in loc_re]))

    elif len(d_area) == 2:

        A,B,C,D = d_box
        x,y,w,h = cv2.boundingRect(p_mask.astype(np.uint8))
        px, py = (x + w/2, y + h/2)
        loc_re = []
        
        for point in [A,B,C,D]:
            dx,dy = point
            
            if px > dx and py > dy:
                loc = 1
            elif px < dx and py > dy:
                loc = 2
            elif px < dx and py < dy:
                loc = 2
            else:
                loc = 1
            # print(loc)
            loc_re.append(loc)
        if loc_re == [1,2,2,1] and d_ratio >= 0.5:
            loc_re = ["all"]
        elif loc_re == [1,2,2,1] and d_ratio < 0.5:
            loc_re = ["center"]
        else:
            loc_re = list(set([d_area[x-1] for x in loc_re]))

    else:

        loc_re = ["all"]
    
    return loc_re

def parsing_json(json_data, part_info):
    
    damage_info = create_damage_info_container(part_info)
    
    # loop json_data and gather damage infos
    
    ai_result = json_data["ai_result"]
    
    for re in ai_result:
        part_name = re["part_name"]
        part_damage_type = re["part_damage_type"]
        
        if len(part_damage_type) >= 1:

            masksize = [re["part_mask"]["size"]]
            maskrles = [re["part_mask"]["counts"].encode('utf-8')]
            
            part_mask = decode_mask_to_rle(masksize, [maskrles])[:,:,0]
            damage_box = np.array(re["damage-summary-mask"])[:4]
            
            # damage_box = change_polygon(part_mask.shape, (401,401), damage_box)
            
            damage_area = part_info[part_name]

            damage_ratio = re["damage-summary-ratio"]
            damage_loc = check_damage_location(part_mask, damage_box, damage_area, damage_ratio)
            
            damage_info[part_name]["damage_type"].append(part_damage_type)
            damage_info[part_name]["damage_location"].append(damage_loc)
            damage_info[part_name]["damage_ratio"].append(damage_ratio)
            
    return damage_info
        
def get_damage_info(json_data, part_info):
    
    # json_data = read_json(json_path)
    
    damage_info = parsing_json(json_data, part_info)
    
    return damage_info

def compare_damage(before_damage_json, after_damage_json):
    
    output_dict = {}
    
    for (part_name1, damage_info1), (part_name2, damage_info2) in zip(before_damage_json.items(), after_damage_json.items()):
        
        assert part_name1==part_name2

        # print(a,c)
        # print(b,d)
        
        damage_type1 = damage_info1["damage_type"]
        damage_type2 = damage_info2["damage_type"]
        
        damage_loc1 = damage_info1["damage_location"]
        damage_loc2 = damage_info2["damage_location"]
        
        if (damage_type1 != damage_type2) or (damage_loc1 != damage_loc2):
            # print(a)
            # print(damage_type1, damage_type2)
            # print(damage_loc1, damage_loc2)
            
            output_dict[part_name1] = {"before_damage": damage_type1, "before_loc":    damage_loc1, 
                                        "after_damage": damage_type2,  "after_loc":    damage_loc2}
    
    return output_dict
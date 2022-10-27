import re
import traceback
from sqlalchemy.orm.exc import NoResultFound
from flask_login import login_required, current_user
from urllib.parse import urlparse

# from app.config import cfg
# from app.common.model_service import SodaModelService
from app.common.utils import create_logger
from app.mod_service.custom_utils import get_damage_info, compare_damage

import cv2
import numpy as np

logger = create_logger(__name__)

def service_compare(input_json):

    compared_result = {}
    try:

        part_info = input_json["partinfo"]

        json_data_1 = input_json["jsondata1"]
        json_data_2 = input_json["jsondata2"]

        damage_info_1 = get_damage_info(json_data_1,part_info)
        damage_info_2 = get_damage_info(json_data_2,part_info)

        compared_result = compare_damage(damage_info_1, damage_info_2)

        compared_result["results"] = "success"
    except:
        compared_result["results"] = "failed"
        raise

    return compared_result
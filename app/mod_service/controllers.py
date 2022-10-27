import traceback
from flask import Blueprint, request, jsonify

from app.mod_service import services
from app.common.utils import as_json, create_logger
logger = create_logger(__name__)

# Define the blueprint: 'train', set its url prefix: app.url/test
mod_service = Blueprint('service', __name__, url_prefix='/api')


################################################################################
# Set the route and accepted methods


@mod_service.route('/compare/', methods=['POST'])
@as_json
def compare_damage():
    logger.info("run damage compare with jsons")
    try:
        input_json = request.get_json()
        return services.service_compare(input_json)
    except Exception:
        result = dict()
        result['success'] = False
        result['log'] = traceback.format_exc()
        logger.error(result['log'])
        return result

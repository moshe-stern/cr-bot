from celery import Celery
import base64
import logging
import tempfile

from celery_app import celery
from src.modules.shared.helpers.get_data_frame import get_data_frame
from src.modules.shared.helpers.get_updated_file import get_updated_file
from src.modules.shared.helpers.index import chunk_list
from src.resources import UpdateType
from src.modules.shared.helpers.get_resource_arr import get_resource_arr
from src.modules.authorization.services.schedule.update_schedules import (
    update_schedules,
)
from src.modules.authorization.services.auth_settings.update_auth_settings import (
    update_auth_settings,
)


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery.task(bind=True)
def process_update(self, file_content, update_type_str, instance):
    logger.info(f"Starting process_update with type: {update_type_str}")
    try:
        file_data = base64.b64decode(file_content)
        df = get_data_frame(file_data)
        if update_type_str not in UpdateType:
            raise ValueError("Invalid update type specified.")

        update_type = UpdateType(update_type_str)
        resources = get_resource_arr(update_type, df)
        for chunk in chunk_list(resources, 5):
            if update_type == UpdateType.SCHEDULE:
                updated_schedules = update_schedules(self, chunk, instance)
                updated_file = get_updated_file(df, updated_schedules, "client_id")
            else:
                updated_settings = update_auth_settings(self, chunk, instance)
                updated_file = get_updated_file(df, updated_settings, "resource_id")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                temp_file.write(updated_file.getvalue())
                logger.info(f"File saved to {temp_file.name}")
                return temp_file.name
    except Exception as e:
        self.update_state(state="FAILURE", meta={"reason": str(e)})
        logger.error(f"Error in process_update: {e}")

import os
from pathlib import Path
import logging

from image_capture import ImageCapture
from data_store import PredictionData, PredictionDataStore
from result_formatter import ThreeLevelResultFormatter
from prediction_api_client import LocalPredictApiClient
import mylogger
from app_exception import OheyaObeyaError


logger = logging.getLogger('OheyaObeya')
logger = mylogger.setup(logger, log_level=logging.DEBUG)

# Settings
project_path = Path(os.path.abspath(__file__)).parent.parent
IMAGE_DIR_PATH = str(Path(project_path) / 'images')
DB_DIR_PATH = str(Path(project_path) / 'db')
# MODEL_PATH = str(Path(project_path) / 'model/20190227-234407_mobilenet_aug_oo_best_model.h5')
MODEL_PATH = str(Path(project_path) / 'model/20190227-234407_mobilenet_aug_oo_best_model_saved_model')

def main():

    # Capture and
    image_capture = ImageCapture(dir_path=IMAGE_DIR_PATH, n_camera=2)
    image_capture.capture()

    image_path = image_capture.last_captured_path

    # Predict
    model_path = MODEL_PATH
    client = LocalPredictApiClient(model_path)
    pred_result = client.predict(image_path)

    # Save
    prediction_data = PredictionData(image_path=image_path,
                                     prediction=pred_result['prediction'],
                                     json_result=str(pred_result),
                                     capture_datetime_local=image_capture.capture_datetime_local,
                                     capture_datetime_utc=image_capture.capture_datetime_utc)

    prediction_ds = PredictionDataStore(DB_DIR_PATH)
    prediction_ds.save(prediction_data)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # noqa
        import traceback
        # if args.notify:
        #     notify_slack('予期せぬエラーが発生しました。 ログを確認してください')
        traceback.print_exc()
        logger.error(e)

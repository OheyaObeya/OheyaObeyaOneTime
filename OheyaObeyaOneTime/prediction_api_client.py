import logging
from pathlib import Path
from typing import Tuple

import tensorflow as tf
from tensorflow.python.keras.models import load_model
from tensorflow.python.keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np

from result_formatter import ResultFormatter, ThreeLevelResultFormatter

logger = logging.getLogger('OheyaObeya')


class PredictionApiClient():
    def predict(self, image_path: str) -> dict:
        data = self.predict_core(image_path)
        return data


class WebPredictApiClient(PredictionApiClient):
    def __init__(self, url: str) -> None:
        self.url = url  # ex) http://localhost:5000


    def predict_core(self, image_path: str) -> dict:
        # TODO: use requests package
        # curl -X POST -F image=@now.jpg 'http://localhost:5000/predict_3level'
        api_url = "{}/predict".format(url)
        command_format = "curl -X POST -F 'image=@{}' '{}'"
        p = command_format.format(image_path, api_url)
        result = subprocess.check_output(p, shell=True)
        text = result.decode('utf-8')
        text = text.replace('true', 'True')
        text = text.replace('false', 'False')
        result_dict = eval(text)
        return result_dict


class LocalPredictApiClient(PredictionApiClient):

    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self.model_name = Path(model_path).stem
        self.model = self.load_oheyaobeya_model(str(model_path))

    def load_oheyaobeya_model(self, path: str):  # TODO
        if Path(path).suffix == '.h5':
            model = load_model(path)
        else:
            # SavedModel
            # MobileNetが読み込めないKerasの不具合に対応するための処理
            # https://github.com/tensorflow/tensorflow/issues/22697
            model = tf.contrib.saved_model.load_keras_model(path)
        return model


    def preprocess(self, image, img_shape: Tuple[int]) -> np.ndarray:

        img_size = (img_shape[0], img_shape[1])
        image = image.resize(img_size)
        image = img_to_array(image)
        image = image.astype('float32')
        image /= 255
        logger.debug('image.shape = {}'.format(image.shape))
        # (28, 28, 1) -> (1, 28, 28, 1)
        image = np.expand_dims(image, axis=0)

        return image

    def predict_core(self, image_path: str) -> dict:
        # TODO: load image
        image = Image.open(image_path)

        # Preprocess
        # TODO: 起動時にtraining時のjsonを読み込んで実行するようにすると修正の必要がなくなる
        # TODO: ここは、モデルによって指定するサイズが変わる
        img_shape = (128, 128, 3)
        image = self.preprocess(image, img_shape=img_shape)

        # Predict
        # result sample: array([[0.00529605, 0.99470395]], dtype=float32)
        preds = self.model.predict(image)
        logger.debug(preds)

        # Convert
        rformatter = ThreeLevelResultFormatter()
        data = rformatter.convert(preds)
        logger.debug(data)

        data['model_version'] = self.model_name

        return data

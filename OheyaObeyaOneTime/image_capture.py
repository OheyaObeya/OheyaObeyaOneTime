import datetime
from pathlib import Path
import logging
import cv2


CAMERA_RAW_SIZE = (1080, 1920, 3)
logger = logging.getLogger('OheyaObeya')

class ImageCapture():
    def __init__(self, dir_path: str, n_camera: int) -> None:
        self.camera_raw_size = CAMERA_RAW_SIZE  # TODO
        self.root_dir_path = dir_path
        self._camera_id = self._check_expected_camera_id(n_camera)

        self.last_captured_path = None
        self.last_captured_datetime_local = None
        self.last_captured_datetime_utc = None

    def _check_expected_camera_id(self, n_camera: int) -> int:  # TODO: n_camera

        for i in range(0, n_camera):
            cap = cv2.VideoCapture(i)
            image = cap.read()[1]

            logger.debug('camera {}: {}'.format(i, image.shape))

            # 想定しているUSBカメラで撮影しているかのチェック
            # 多分もっとよい方法はあると思うが、ここではカメラのサイズを見ている
            if image.shape == self.camera_raw_size:
                cap.release()
                return i
            cap.release()
        else:
            message = 'Failed to capture. Not found an expected camera.'
            raise OheyaObeyaError(message)

    def capture(self) -> None:
        cap = cv2.VideoCapture(self._camera_id)
        image = cap.read()[1]

        now_dt_local = datetime.datetime.now()
        now_dt_utc = datetime.datetime.now(datetime.timezone.utc)
        self.capture_datetime_local = now_dt_local
        self.capture_datetime_utc = now_dt_utc

        # Make path
        now_str_local = now_dt_local.strftime("%Y%m%d-%H%M%S")
        now_str_utc = now_dt_utc.strftime("%Y%m%d-%H%M%S")
        file_name = 'local_{}_utc_{}.jpg'.format(now_str_local, now_str_utc)
        date = now_dt_local.strftime("%Y%m%d")

        # Save
        path = Path(self.root_dir_path) / date / file_name
        path.parent.mkdir(exist_ok=True, parents=True)
        cv2.imwrite(str(path), image)
        cap.release()

        self.last_captured_path = str(path)
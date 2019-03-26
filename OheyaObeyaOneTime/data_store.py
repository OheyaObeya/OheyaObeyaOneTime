import sqlite3
import logging
from pathlib import Path


logger = logging.getLogger('OheyaObeya')


class PredictionData():
    # TODO: Python 3.7が使えるようになったら、DataClassに変更する
    def __init__(self,
                 image_path: str,
                 prediction: str,
                 json_result: dict,
                 capture_datetime_local,
                 capture_datetime_utc):
        self.image_path = image_path
        self.prediction = prediction
        self.json_result = str(json_result)
        self.capture_datetime_local = capture_datetime_local
        self.capture_datetime_utc = capture_datetime_utc


class PredictionDataStore():
    def __init__(self, db_dir_path: str):
        self.db_path = str(Path(db_dir_path) / 'OheyaObeyaDB.sqlite')
        Path(self.db_path).parent.mkdir(exist_ok=True, parents=True)
        if not Path(self.db_path).exists():
            self.create()

    def create(self) -> None:
        conn = sqlite3.connect(self.db_path)

        # DBを作成
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE predictions(
                        prediction_id INTEGER NOT NULL PRIMARY KEY,
                        image_path TEXT NOT NULL,
                        prediction TEXT NOT NULL,
                        json_result TEXT NOT NULL,
                        capture_datetime_local datetime NOT NULL,
                        capture_datetime_utc datetime NOT NULL,
                        upload_datetime_local datetime NULL,
                        upload_datetime_utc datetime NULL)
                    """)
        conn.commit()

    def save(self, data: PredictionData):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        data_tuple = (data.image_path,
                      data.prediction,
                      data.json_result,
                      data.capture_datetime_local,
                      data.capture_datetime_utc)

        cur.execute(
        """INSERT INTO predictions (image_path,
                                    prediction,
                                    json_result,
                                    capture_datetime_local,
                                    capture_datetime_utc)
                                    VALUES (?, ?, ?, ?, ?)""",
        data_tuple)
        conn.commit()
        logger.debug('Completed to save data.')

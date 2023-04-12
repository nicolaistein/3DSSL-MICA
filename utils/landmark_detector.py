import face_alignment
import numpy as np
from insightface.app import FaceAnalysis
from loguru import logger


class Detectors:
    def __init__(self):
        self.RETINAFACE = 'RETINAFACE'
        self.FAN = 'FAN'


detectors = Detectors()


class LandmarksDetector:
    def __init__(self, model='retinaface', device='cuda:0'):
        model = model.upper()
        self.predictor = model
        if model == detectors.RETINAFACE:
            self._face_detector = FaceAnalysis(name='antelopev2', providers=['CUDAExecutionProvider'])
            self._face_detector.prepare(ctx_id=0, det_size=(224, 224))
        elif model == detectors.FAN:
            self._face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, device=device)
        else:
            logger.error(f'[ERROR] Landmark predictor not supported {model}')
            exit(-1)

        logger.info(f'[DETECTOR] Selected {model} as landmark detector.')

    def detect(self, img):
        if self.predictor == detectors.RETINAFACE:
            bboxes, kpss = self._face_detector.det_model.detect(img, max_num=0, metric='default')
            return bboxes, kpss

        if self.predictor == detectors.FAN:
            lmks, scores, detected_faces = self._face_detector.get_landmarks_from_image(img, return_landmark_score=True, return_bboxes=True)
            if detected_faces is None:
                return np.empty(0), np.empty(0)
            bboxes = np.stack(detected_faces)
            # https://github.com/Rubikplayer/flame-fitting/blob/master/data/landmarks_51_annotated.png
            kpss = np.stack(lmks)[:, 17:, :][:, [19, 28, 16, 31, 37], :]  # left eye, right eye, nose, left mouth, right mouth
            return bboxes, kpss

        return None, None
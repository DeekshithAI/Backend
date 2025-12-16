# backend/sideview/model.py

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
import json
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')

IMAGE_SIZE = (224, 224)

class SideViewModel:
    def __init__(self):
        self.model_path = "sideview/phase2_best.h5"
        self.mappings_path = "sideview/class_mappings.json"
        self.model = None
        self.part_classes = None
        self.status_classes = None
        self._load_mappings()

    def _load_mappings(self):
        with open(self.mappings_path, "r") as f:
            m = json.load(f)
        self.part_classes = m["part_classes"]
        self.status_classes = m["status_classes"]

    def _ensure_model_loaded(self):
        if self.model is None:
            self.model = tf.keras.models.load_model(self.model_path, compile=False)

    def preprocess(self, image_path):
        img = tf.io.read_file(image_path)
        img = tf.image.decode_image(img, channels=3, expand_animations=False)
        img = tf.image.resize(img, IMAGE_SIZE)
        img = img / 255.0
        img = tf.expand_dims(img, 0)
        return img

    def predict(self, image_path):
        self._ensure_model_loaded()
        img = self.preprocess(image_path)

        part_pred, status_pred = self.model.predict(img, verbose=0)

        part_idx = int(np.argmax(part_pred))
        status_idx = int(np.argmax(status_pred))

        return {
            "part": self.part_classes[part_idx],
            "status": self.status_classes[status_idx],
            "part_confidence": float(np.max(part_pred)),
            "status_confidence": float(np.max(status_pred)),
        }

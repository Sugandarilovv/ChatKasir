from __future__ import annotations

import logging
from typing import Any, List, Optional

import numpy as np

from app.core.config import settings
from app.core.errors import InferenceFailedError, ModelNotLoadedError

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton that loads a Keras model once and exposes a predict method."""

    _model: Optional[Any] = None   # keras.Model

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> "ModelLoader":
        if cls._model is None:
            cls._load_model()
        return cls()

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None

    @classmethod
    def reset(cls) -> None:
        """Release the model (useful for testing or graceful shutdown)."""
        cls._model = None

    # ── Internal ──────────────────────────────────────────────────────────────

    @classmethod
    def _load_model(cls) -> None:
        try:
            import tensorflow as tf  # type: ignore

            logger.info("Loading model from %s …", settings.MODEL_PATH)
            cls._model = tf.keras.models.load_model(settings.MODEL_PATH)
            logger.info("Model loaded successfully.")
        except FileNotFoundError:
            logger.warning(
                "Model file not found at '%s'. "
                "Inference will fail until a model is placed there.",
                settings.MODEL_PATH,
            )
            # Keep _model as None so is_loaded() returns False
        except Exception as exc:
            logger.exception("Unexpected error while loading model: %s", exc)
            raise ModelNotLoadedError(str(exc)) from exc

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict(self, inputs: List[List[float]]) -> List[Any]:
        """Run inference and return a plain-Python list of predictions.

        Parameters
        ----------
        inputs:
            Batch of input vectors (list of lists of floats).

        Returns
        -------
        List of model outputs (class indices or probability arrays).
        """
        if self._model is None:
            raise ModelNotLoadedError()

        try:
            x = np.array(inputs, dtype=np.float32)
            raw = self._model.predict(x)          # shape: (batch, *output_shape)
            # Return argmax for classification, or raw floats for regression
            if raw.ndim == 2 and raw.shape[1] > 1:
                return raw.argmax(axis=1).tolist()
            return raw.flatten().tolist()
        except Exception as exc:
            logger.exception("Inference error: %s", exc)
            raise InferenceFailedError(str(exc)) from exc

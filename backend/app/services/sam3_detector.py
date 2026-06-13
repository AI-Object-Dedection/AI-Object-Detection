"""
Sam3Detector - connects the trained SAM3 LoRA model to the site.

This is the "last step" target. The detection logic below is a faithful port
of SAM3/src/infer.py::run_multiclass_inference, so it is essentially complete.
To go live you only need to:

    1) Install the ML deps in the backend env (or run the backend in SAM3's env):
         pip install torch transformers peft pillow numpy
    2) Make sure the trained LoRA checkpoint exists, e.g.:
         SAM3/checkpoints/mc_epoch_1_lora
    3) Point settings at it (backend/.env or config.py defaults):
         DETECTOR_BACKEND=sam3
         SAM3_REPO_PATH=C:\\Users\\Lenovo\\Desktop\\uygulamalar\\SAM3
         SAM3_CHECKPOINT=checkpoints/mc_epoch_1_lora   (relative to SAM3_REPO_PATH)
         SAM3_MODEL_NAME=facebook/sam3

That's it - no other file in the site needs to change.

Heavy imports (torch/transformers/peft) happen lazily inside _load(), so when
DETECTOR_BACKEND=mock the site runs with zero ML dependencies.
"""
import os
import sys

from app.core.config import settings
from app.services.detector import (
    DAMAGE_CLASSES,
    BaseDetector,
    DetectedClass,
    DetectionResult,
)


class Sam3Detector(BaseDetector):
    """Runs the fine-tuned SAM3 model and maps its masks to DetectionResult."""

    backend_name = "sam3"

    # Loaded once and reused across requests (model load is expensive).
    _model = None
    _processor = None

    def __init__(self):
        self.min_coverage = settings.SAM3_MIN_COVERAGE
        self.threshold = settings.DAMAGE_CONFIDENCE_THRESHOLD

    def _checkpoint_path(self) -> str:
        """Resolve the LoRA checkpoint path (relative paths are under the SAM3 repo)."""
        ckpt = settings.SAM3_CHECKPOINT
        if os.path.isabs(ckpt):
            return ckpt
        return os.path.join(settings.SAM3_REPO_PATH, ckpt)

    def _load(self):
        """
        Load the base SAM3 model + processor and apply the trained LoRA adapter.

        Runs only once; subsequent calls reuse the cached model. This is the
        only place that touches torch/transformers/peft.
        """
        if Sam3Detector._model is not None:
            return

        # Make SAM3's own code importable (src.model, src.config, ...).
        repo = settings.SAM3_REPO_PATH
        if repo and repo not in sys.path:
            sys.path.insert(0, repo)

        # SAM3's Config reads the model name from this env var.
        os.environ.setdefault("SAM3_MODEL_NAME", settings.SAM3_MODEL_NAME)

        from peft import PeftModel
        from src.model import load_model, load_processor

        ckpt = self._checkpoint_path()
        if not os.path.isdir(ckpt):
            raise FileNotFoundError(
                f"SAM3 LoRA checkpoint not found: {ckpt}. "
                f"Train the model or fix SAM3_CHECKPOINT in settings."
            )

        model = load_model()
        model = PeftModel.from_pretrained(model, ckpt)

        # SAM3 loads in float16 (great on GPU). On CPU (e.g. a free Space)
        # half precision is slow/unsupported for many ops, so cast to float32.
        from src.config import Config
        if Config.DEVICE == "cpu":
            model = model.float()

        model.eval()

        Sam3Detector._model = model
        Sam3Detector._processor = load_processor()

    def analyze(self, image_path: str) -> DetectionResult:
        """
        Run per-class inference (one text prompt per DACL10K class) and return
        the classes whose mask covers at least SAM3_MIN_COVERAGE of the image.

        Mirrors SAM3/src/infer.py::run_multiclass_inference.
        """
        import numpy as np
        import torch
        from PIL import Image

        self._load()
        model = Sam3Detector._model
        processor = Sam3Detector._processor

        # SAM3's Config holds the device + mask threshold details.
        from src.config import Config

        image = Image.open(image_path).convert("RGB")

        # Process the image once - the same pixel_values feed every class prompt.
        image_inputs = processor.image_processor(images=image, return_tensors="pt")
        pixel_values = image_inputs["pixel_values"].to(Config.DEVICE)

        classes = []
        with torch.no_grad():
            for label in DAMAGE_CLASSES:
                text_inputs = processor.tokenizer(
                    label,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                )
                input_ids = text_inputs["input_ids"].to(Config.DEVICE)
                attention_mask = text_inputs["attention_mask"].to(Config.DEVICE)

                with torch.amp.autocast("cuda", enabled=(Config.DEVICE == "cuda")):
                    outputs = model(
                        pixel_values=pixel_values,
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                    )

                # semantic_seg: (1, 1, 288, 288) -> probability map (288, 288)
                logits = outputs.semantic_seg.squeeze()
                prob = logits.sigmoid().cpu().numpy()
                binary = prob > self.threshold

                coverage = float(binary.mean())
                if coverage < self.min_coverage:
                    continue

                # Confidence = mean probability inside the predicted region.
                confidence = float(prob[binary].mean()) if binary.any() else float(prob.max())
                classes.append(
                    DetectedClass(
                        label=label,
                        coverage=coverage,
                        confidence=confidence,
                    )
                )

        return DetectionResult(classes=classes, backend=self.backend_name)

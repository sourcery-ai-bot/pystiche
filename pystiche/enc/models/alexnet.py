import warnings
from typing import Any, Dict, List, Optional, Tuple

from torch import nn
from torch.utils import model_zoo
from torchvision.models import alexnet

from pystiche.misc import build_deprecation_message

from ..multi_layer_encoder import MultiLayerEncoder
from ..preprocessing import get_preprocessor

MODEL_URLS = {"torch": "https://download.pytorch.org/models/alexnet-owt-4df8aa71.pth"}


__all__ = ["alexnet_multi_layer_encoder"]


class MultiLayerAlexNetEncoder(MultiLayerEncoder):
    def __init__(
        self, weights: str, internal_preprocessing: bool, allow_inplace: bool
    ) -> None:
        self.weights = weights
        self.internal_preprocessing = internal_preprocessing
        self.allow_inplace = allow_inplace

        super().__init__(self._collect_modules())

    def _collect_modules(self) -> List[Tuple[str, nn.Module]]:
        base_model = alexnet()
        url = MODEL_URLS[self.weights]
        state_dict = model_zoo.load_url(url)
        base_model.load_state_dict(state_dict)
        model = base_model.features

        modules = []
        if self.internal_preprocessing:
            modules.append(("preprocessing", get_preprocessor(self.weights)))
        block = 1
        for module in model.children():
            if isinstance(module, nn.Conv2d):
                name = f"conv{block}"
            elif isinstance(module, nn.ReLU):
                if not self.allow_inplace:
                    module = nn.ReLU(inplace=False)
                name = f"relu{block}"
                if block in (3, 4):
                    # in the third and forth block the ReLU layer marks the end of the
                    # block
                    block += 1
            else:  # isinstance(module, nn.MaxPool2d):
                name = f"pool{block}"
                # each pooling layer marks the end of the current block
                block += 1

            modules.append((name, module))

        return modules

    def _properties(self) -> Dict[str, Any]:
        dct = super()._properties()
        dct["weights"] = self.weights
        if not self.internal_preprocessing:
            dct["internal_preprocessing"] = self.internal_preprocessing
        if self.allow_inplace:
            dct["allow_inplace"] = self.allow_inplace
        return dct


class AlexNetEncoder(MultiLayerAlexNetEncoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        msg = build_deprecation_message(
            "The class AlexNetEncoder",
            "0.4.0",
            info="It was replaced by MultiLayerAlexNetEncoder.",
        )
        warnings.warn(msg)
        super().__init__(*args, **kwargs)


def alexnet_multi_layer_encoder(
    weights: str = "torch",
    preprocessing: Optional[bool] = None,
    internal_preprocessing: bool = True,
    allow_inplace: bool = False,
) -> MultiLayerAlexNetEncoder:
    if preprocessing is not None:
        msg = build_deprecation_message(
            "The parameter preprocessing",
            "0.4.0",
            info="It was replaced by internal_preprocessing.",
        )
        warnings.warn(msg)
        internal_preprocessing = preprocessing
    return MultiLayerAlexNetEncoder(weights, internal_preprocessing, allow_inplace)


def alexnet_encoder(*args: Any, **kwargs: Any) -> MultiLayerAlexNetEncoder:
    msg = build_deprecation_message(
        "The function alexnet_encoder",
        "0.4.0",
        info="It was replaced by alexnet_multi_layer_encoder.",
    )
    warnings.warn(msg)
    return alexnet_multi_layer_encoder(*args, **kwargs)

import warnings
from typing import Dict, Optional, Sequence, Tuple

import torch
from torch import nn

from pystiche.misc import build_deprecation_message

from ._objects import ComplexObject

__all__ = ["Module", "SequentialModule"]


class Module(nn.Module, ComplexObject):
    _buffers: Dict[str, torch.Tensor]
    _modules: Dict[str, nn.Module]

    def __init__(
        self,
        named_children: Optional[Sequence[Tuple[str, nn.Module]]] = None,
        indexed_children: Optional[Sequence[nn.Module]] = None,
    ):
        super().__init__()
        if not (named_children is None or indexed_children is None):
            msg = (
                "named_children and indexed_children "
                "are mutually exclusive parameters."
            )
            raise RuntimeError(msg)
        elif named_children is not None:
            self.add_named_modules(named_children)
        elif indexed_children is not None:
            self.add_indexed_modules(indexed_children)

    def add_named_modules(self, modules: Sequence[Tuple[str, nn.Module]]) -> None:
        if isinstance(modules, dict):
            msg = build_deprecation_message(
                "Adding named_modules from a dictionary",
                "0.4",
                info=(
                    "To achieve the same behavior you can pass "
                    "tuple(modules.items()) instead."
                ),
            )
            warnings.warn(msg)
            modules = tuple(modules.items())
        for name, module in modules:
            self.add_module(name, module)

    def add_indexed_modules(self, modules: Sequence[nn.Module]) -> None:
        self.add_named_modules(
            [(str(idx), module) for idx, module in enumerate(modules)]
        )

    def __repr__(self) -> str:
        return ComplexObject.__repr__(self)

    def torch_repr(self) -> str:
        return nn.Module.__repr__(self)

    def extra_repr(self) -> str:
        return ", ".join([f"{key}={value}" for key, value in self.properties().items()])


class SequentialModule(Module):
    def __init__(self, *modules: nn.Module):
        super().__init__(indexed_children=modules)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for module in self.children():
            x = module(x)
        return x

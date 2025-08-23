"""Configuração centralizada de compatibilidade Torch/Ultralytics.

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas

Responsável por:
- Registrar classes do Ultralytics e módulos PyTorch em safe globals (torch.serialization)
- (Opcional) aplicar fallback unsafe controlado para `torch.load` quando necessário

Executado uma única vez no startup da aplicação para evitar custo repetido
em cada carregamento de modelo.
"""
from __future__ import annotations

import torch
import importlib
from typing import List
from dataclasses import dataclass

_TORCH_CONFIGURED = False


@dataclass
class TorchSetupOptions:
    allow_unsafe_fallback: bool = False  # Se true, aplica patch temporário para weights_only=False
    verbose: bool = True


def _collect_ultralytics_classes() -> List[type]:
    classes: List[type] = []
    try:
        tasks = importlib.import_module('ultralytics.nn.tasks')
        modules = importlib.import_module('ultralytics.nn.modules')
    except Exception:
        return classes

    for name in ['DetectionModel', 'SegmentationModel', 'ClassificationModel', 'PoseModel']:
        if hasattr(tasks, name):
            classes.append(getattr(tasks, name))

    for attr_name in dir(modules):
        attr = getattr(modules, attr_name)
        if hasattr(attr, '__module__') and 'ultralytics' in str(attr.__module__):
            if isinstance(attr, type):
                classes.append(attr)
    return classes


def _collect_torch_core_classes() -> List[type]:
    import torch.nn as nn
    base = [
        nn.Module, nn.Parameter, nn.Sequential, nn.ModuleList, nn.ModuleDict,
        nn.Conv2d, nn.Conv1d, nn.Conv3d, nn.ConvTranspose2d,
        nn.BatchNorm2d, nn.BatchNorm1d, nn.SyncBatchNorm, nn.GroupNorm, nn.LayerNorm,
        nn.ReLU, nn.SiLU, nn.GELU, nn.LeakyReLU, nn.ELU, nn.PReLU,
        nn.MaxPool2d, nn.AvgPool2d, nn.AdaptiveAvgPool2d,
        nn.Linear, nn.Dropout, nn.Dropout2d, nn.Upsample, nn.Flatten, nn.Identity
    ]
    for extra in ['Mish', 'Hardswish', 'Hardsigmoid']:
        if hasattr(nn, extra):
            base.append(getattr(nn, extra))
    return base


def configure_torch_serialization(options: TorchSetupOptions = TorchSetupOptions()) -> None:
    global _TORCH_CONFIGURED
    if _TORCH_CONFIGURED:
        return

    try:
        ul_classes = _collect_ultralytics_classes()
        torch_classes = _collect_torch_core_classes()
        safe_globals = [c for c in (ul_classes + torch_classes) if c is not None]
        torch.serialization.add_safe_globals(safe_globals)
        if options.verbose:
            print(f"🔧 Torch serialization configurado: {len(safe_globals)} classes registradas")
    except Exception as e:
        print(f"⚠️  Falha ao registrar safe globals: {e}")

    if options.allow_unsafe_fallback:
        original_load = torch.load

        def patched_torch_load(*args, **kwargs):  # type: ignore
            kwargs.setdefault('weights_only', False)
            return original_load(*args, **kwargs)

        torch.load = patched_torch_load  # type: ignore
        if options.verbose:
            print("⚠️  Patch temporário de torch.load aplicado (unsafe fallback habilitado)")

    _TORCH_CONFIGURED = True


def configure_for_app(app_config) -> None:
    allow_unsafe = getattr(app_config, 'TORCH_UNSAFE_FALLBACK', False)
    verbose = getattr(app_config, 'TORCH_SETUP_VERBOSE', True)
    configure_torch_serialization(TorchSetupOptions(allow_unsafe_fallback=allow_unsafe, verbose=verbose))

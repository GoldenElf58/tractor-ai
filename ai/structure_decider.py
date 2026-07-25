from typing import override

import torch
from torch import nn

from ai.model import Model


class StructureDecider(Model):
    def __init__(self):
        layers = nn.Sequential(
            nn.Linear(70, 64),
            nn.ReLU(),
            nn.Linear(64, 4),
        )
        super().__init__(layers)
        self.softmax = nn.Softmax(dim=0)

    @override
    def forward(self, x):
        x = self.layers(x)
        assert len(x) == 4
        x = torch.cat([self.softmax(x[:3]), x[3:]])
        return x

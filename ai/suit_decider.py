from torch import nn

from ai.model import Model


class SuitDecider(Model):
    def __init__(self):
        layers = nn.Sequential(
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 6),
            nn.Softmax(dim=0)
        )
        super().__init__(layers)

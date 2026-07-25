from torch import nn

from ai.model import Model


class CardDecider(Model):
    def __init__(self):
        layers = nn.Sequential(
            nn.Linear(74, 64),
            nn.ReLU(),
            nn.Linear(64, 108),
            nn.Sigmoid()
        )
        super().__init__(layers)

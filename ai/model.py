import torch
import torch.nn as nn
from torch import Tensor
from torch.optim import Optimizer


class Model(nn.Module):
    def __init__(self, layers: nn.Sequential, optimizer: Optimizer | None = None,
                 criterion: nn.Module | None = None, create_optimizer: bool = True):
        super().__init__()
        self.flatten = nn.Flatten(end_dim=1)
        self.layers = layers
        self.optimizer: Optimizer | None = torch.optim.Adam(self.parameters(), lr=0.01) if \
            create_optimizer and optimizer is None else optimizer
        self.criterion: nn.Module = nn.CrossEntropyLoss() if criterion is None else criterion

    def forward(self, x):
        if x.ndim > 1:
            x = self.flatten(x)
        x = self.layers(x)
        return x

    def set_optimizer(self, optimizer: Optimizer):
        self.optimizer = optimizer

    def set_criterion(self, criterion: nn.Module):
        self.criterion = criterion

    def get_optimizer(self) -> Optimizer | None:
        return self.optimizer

    def get_criterion(self) -> nn.Module:
        return self.criterion

    def evaluate(self, x: Tensor, y: Tensor) -> tuple[float, float]:
        with torch.no_grad():
            self.eval()
            y_pred = self.forward(x)
            loss: float = self.criterion(y_pred, y).detach().clone()
            correct = 0
            for i, data in enumerate(x):
                y_pred = self.forward(data)
                if y_pred.argmax().item() == y[i]:
                    correct += 1
            accuracy: float = correct / len(x)
            return loss, accuracy

    def learn(self, data: tuple[Tensor, Tensor, Tensor, Tensor], epochs: int) -> tuple[
        list[float], list[float], list[float]]:
        if self.optimizer is None:
            raise ValueError("Optimizer not set")
        x_train, x_test, y_train, y_test = data
        train_losses = []
        test_losses = []
        test_accuracies = []
        for _ in range(epochs):
            loss, accuracy = self.evaluate(x_test, y_test)
            test_losses.append(loss)
            test_accuracies.append(accuracy)
            self.train()
            y_pred = self.forward(x_train)
            loss = self.criterion(y_pred, y_train)
            train_losses.append(loss.detach().clone())
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        return train_losses, test_losses, test_accuracies

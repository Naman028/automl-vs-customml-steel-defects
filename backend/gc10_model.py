"""GC10 model definition and local preprocessing shared by training and inference."""

import torch
from torchvision import models, transforms
from image_preprocessing import resnet_transform

IMAGE_SIZE = 224


def image_transform() -> transforms.Compose:
    return resnet_transform(IMAGE_SIZE)


def create_backbone() -> tuple[torch.nn.Module, int]:
    backbone = models.resnet18(weights=None)
    feature_count = int(backbone.fc.in_features)
    setattr(backbone, "fc", torch.nn.Identity())
    return backbone.eval(), feature_count

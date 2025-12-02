import json
import os
from datetime import datetime
import pickle
import numpy as np
from dotenv import load_dotenv
import torch
import h5py
from PIL import Image
from torchvision import transforms

def parse_datetime(date_str):
    """
    Parse date string to get date and time
    :param date_str: date string in iso format, dataset has YYYY-MM-DD 00:00:00+00:00
    :return: minute of day from [0, 1439], day of year from [1, 366]
    """
    dt = datetime.fromisoformat(date_str)
    #timezone ignored
    if dt.hour==0 and dt.minute==0 and dt.second==0:
        time = None
    else:
        time = dt.hour*60 + dt.minute
    return time, dt.timetuple().tm_yday


def sinusoidal_encoding(value, max_value):
    """
    Encodes value by transforming with sine and cosine.
    Allows representation of cyclical values.
    :param value: the value to be encoded
    :param max_value: max value that value can take before cycling
    :return: (sine, cosine) each between [-1, 1]
    """
    if value is None:
        return None, None
    angle = np.pi * value / max_value
    return np.sin(angle), np.cos(angle)


def image_transform(image_path):
    """
    Transforms image to 224x224 and normalizes for model inference.
    :param image_path: path to image
    :return: a pytorch tensor of transformed image
    """
    image = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        #model pretrained on imagenet so use mean and std values
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
        ])
    image_tensor = transform(image)
    return image_tensor
from Model.inference import classify_species
from model import SpeciesClassifier
import inference
import json

#load trained model
model = SpeciesClassifier(pretrained=True)

#example image of a bison I took at yellowstone
image_path = "bison.jpg"
#and the labels json
with open("labels.json", "r") as f:
    labels = json.load(f)

#pass these three in and get the top 5 species
top5 = classify_species(model, image_path, labels)
print(top5)
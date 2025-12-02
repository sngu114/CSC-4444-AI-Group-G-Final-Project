from Model.inference import classify_species_and_tax, classify_species
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

#need taxonomy level indices
with open("tax_indices.json", "r") as f:
    tax_indices = json.load(f)

#pass these three in and get the top 5 species and taxonomy level
top5withtax = classify_species_and_tax(model, image_path, labels, tax_indices)
print(top5withtax)
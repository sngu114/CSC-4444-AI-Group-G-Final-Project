from flask import Flask, request, jsonify
import tempfile
import os
import json
import torch
from flask_cors import CORS

from inference import classify_species
from model import SpeciesClassifier


app = Flask(__name__)
CORS(app)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Loading SpeciesClassifier...")
model = SpeciesClassifier(pretrained=True)
model.to(DEVICE)
model.eval()
print("Model Loaded.")

print("Loading labels...")
with open("labels.json", "r") as f:
    LABELS = json.load(f)
print(f"Loaded {len(LABELS)} species labels.")

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file included"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No filename"}), 400

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp_path = tmp.name
            file.save(tmp_path)

        top5 = classify_species(model, tmp_path, LABELS)

        best = top5[0]
        species_name = best["taxonomy"][0]
        confidence = float(best["prob"])

        return jsonify({
            "prediction": species_name,
            "confidence": confidence,
            "top5": [
                {"species": x["taxonomy"][0], "prob": float(x["prob"])}
                for x in top5
            ]
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": "Prediction failed"}), 500

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

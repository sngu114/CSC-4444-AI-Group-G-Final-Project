from flask import Flask, request, jsonify
import tempfile
import os
import json
import torch
import requests
from flask_cors import CORS

# Import your new function instead
from inference import classify_species_and_tax
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

print("Loading taxonomy indices...")
with open("tax_indices.json", "r") as f:
    TAX_INDICES = json.load(f)
print("Taxonomy indices loaded.")


def fetch_wikipedia_summary(species_name):
    """
    Fetch Wikipedia summary for a species using the Wikipedia API.
    return: dict with 'summary', 'url', and 'thumbnail' if available.
    """
    try:
        #wikipedia summary endpoint
        api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        
        #must clean species name for url
        species_url = species_name.replace(" ", "_")

        #have to add header so api knows were nice
        headers = {
            'User-Agent': 'SpeciesClassifier/1.0 (graybaseball77@gmail.com)'
        }

        response = requests.get(f"{api_url}{species_url}", timeout=5, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return {
                "summary": data.get("extract", "No summary available."),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumbnail": data.get("thumbnail", {}).get("source", None),
                "title": data.get("title", species_name)
            }
        else:
            return {
                "summary": "Wikipedia article not found for this species.",
                "url": "",
                "thumbnail": None,
                "title": species_name
            }
    except Exception as e:
        print(f"Wikipedia fetch error for '{species_name}':", e)
        return {
            "summary": "Unable to fetch Wikipedia information.",
            "url": "",
            "thumbnail": None,
            "title": species_name
        }


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

        tax_level_dict, top5_results = classify_species_and_tax(model, tmp_path, LABELS, TAX_INDICES)

        #tensors mess everything up so convert it all to floats
        def to_float(value):
            if isinstance(value, torch.Tensor):
                return float(value.item())
            return float(value)

        #get top 1
        best = top5_results[0]
        species_name = best["taxonomy"][0]
        confidence = to_float(best["prob"])
        
        #get wiki summary
        wiki_info = fetch_wikipedia_summary(species_name)

        # Format the response - convert all tensors to floats
        response_data = {
            "taxonomy_level": {
                "tax_level": tax_level_dict.get("tax_level", "species"),
                "name": tax_level_dict.get("name", ""),
                "confidence": to_float(tax_level_dict.get("confidence", 0))
            },
            "prediction": species_name,
            "confidence": confidence,
            "wikipedia": wiki_info,
            "top5": [
                {
                    "species": x["taxonomy"][0],
                    "prob": to_float(x["prob"]),
                    "wiki_image": fetch_wikipedia_summary(x["taxonomy"][0]).get("thumbnail", None),
                }
                for x in top5_results
            ]
        }

        return jsonify(response_data)

    except Exception as e:
        print("Prediction error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
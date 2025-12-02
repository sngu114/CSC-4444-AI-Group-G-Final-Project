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
from preprocess import parse_datetime


def create_subset_dataset(json_path, output_dir, supercategories, partition):
    """
    Takes original inaturalist mini dataset and makes a subset.
    Creates a label list json of species in chosen supercategories.
    This list includes name and all other taxonomy info.
    It is then ordered alphanumerically from the highest taxonomy level to lowest.
    Creates the input data as a list of paths to images and list of metadata (location, date, time).
    Creates the ground truth output data as a list of indices to the correct label in the label list.
    :param json_path: path to inaturalist mini dataset annotations json file
    :param output_dir: directory to save the all the made files
    :return:
    """
    target_supercategories = supercategories

    print("Loading original dataset json file")
    with open(json_path, 'r') as f:
        data = json.load(f)


    X_image_paths = []
    X_metadata = []
    Y_labels = []

    label_idx = [1, 10, 9, 8, 7, 6, 5, 4]

    print("filtering supercategories")
    filtered_categories = {}
    label_taxonomy = []
    for cat in data['categories']:
        if cat['supercategory'] in target_supercategories:
            filtered_categories[cat['id']] = cat
            #creates list of taxonomy info
            #[species name, epithet, genus, family, order, class, phylum, kingdom]
            tax_list = list(map(list(cat.values()).__getitem__, label_idx))
            label_taxonomy.append(tax_list)

    sorted_labels = sorted(label_taxonomy, key=lambda x: x[::-1])

    print("saving json of labels")
    #make this so it checks if exist and doesnt save if it does
    with open(os.path.join(output_dir, 'labels.json'), 'w') as f:
        json.dump(sorted_labels, f)

    #maps every label to an index for lookup
    label_to_idx = {tuple(label): idx for idx, label in enumerate(sorted_labels)}

    print("filtering images by supercategories")
    img_cat_ids = {}
    for ann in data['annotations']:
        if ann['category_id'] in filtered_categories:
            img_cat_ids[ann['image_id']] = ann['category_id']

    print("loading and processing images")
    for idx, img in enumerate(data['images']):
        if img['id'] in img_cat_ids:
            category = filtered_categories[img_cat_ids[img['id']]]
            img_path = img['file_name'] #file_mini/imagename.jpg
            X_image_paths.append(img_path)

            # Metadata
            lat = img['latitude']
            lon = img['longitude']
            minute, day_of_year = parse_datetime(img['date'])
            X_metadata.append((lat, lon, day_of_year, minute))
            #create dataset function for metadata
            #get item will sinusoidally encode all of these
            #and if any are None, will ignore datapoint

            #creates corresponding label for image
            tax_list = list(map(list(category.values()).__getitem__, label_idx))
            #looks up corresponding index for label
            label_idx_val = label_to_idx[tuple(tax_list)]
            #appends index to Y list
            Y_labels.append(label_idx_val)

        #check progress
        if (idx + 1) % 1000 == 0:
            print(f"processed {idx + 1} images") #should be 500,000 by end

    os.makedirs(output_dir, exist_ok=True)

    #save as numpy arrays
    print("saving data")
    np.save(os.path.join(output_dir, f'{partition}_image_paths.npy'), X_image_paths)
    np.save(os.path.join(output_dir, f'{partition}_metadata.npy'), X_metadata)
    np.save(os.path.join(output_dir, f'{partition}_labels.npy'), Y_labels)
    print("save successful")


if __name__ == "__main__":
    #using env variables since paths specific to my machine
    load_dotenv()
    json_path = os.getenv('JSON_PATH')
    output_dir = os.getenv('OUTPUT_DIR')

    #can change if we want to, but kinda a hassle to trim the dataset again
    supercategories = {'Animalia', 'Mammals', 'Arachnids', 'Reptiles'}

    #training data
    train_json_path = "C:/Users/grayb/OneDrive - Louisiana State University/LSU yr4sem1/CSC4444 AI/train_mini.json/train_mini.json"
    train_output_dir = "C:/Users/grayb/Downloads/train_mini"
    create_subset_dataset(train_json_path, train_output_dir, supercategories, "train")


    val_json_path = "C:/Users/grayb/Downloads/val.json/val.json"
    val_output_dir = "C:/Users/grayb/Downloads/val"
    create_subset_dataset(val_json_path, val_output_dir, supercategories, "val")
    #will save X_imagepaths, X_metadat, and Y_labels in outputdir
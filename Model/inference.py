from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import torch
import numpy as np
import timm

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
    angle = np.pi*value/max_value
    return np.sin(angle), np.cos(angle)

def extract_gps_info(exif_data):
    """
    extract gps coordinates from exif data
    returns: (latitude, longitude) or (None, None)
    """
    gps_info = {}
    if 'GPSInfo' in exif_data:
        for key, val in exif_data['GPSInfo'].items():
            decode = GPSTAGS.get(key, key)
            gps_info[decode] = val
    if not gps_info:
        return None, None
    lat = None
    lon = None
    if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
        lat_data = gps_info['GPSLatitude']
        lat_ref = gps_info['GPSLatitudeRef']
        # convert to floats
        lat = float(lat_data[0]) + float(lat_data[1]) / 60 + float(lat_data[2]) / 3600
        if lat_ref == 'S':
            lat = -lat
    if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
        lon_data = gps_info['GPSLongitude']
        lon_ref = gps_info['GPSLongitudeRef']
        # convert to floats
        lon = float(lon_data[0]) + float(lon_data[1]) / 60 + float(lon_data[2]) / 3600
        if lon_ref == 'W':
            lon = -lon
    return lat, lon


def extract_datetime_info(exif_data):
    """
    extract date and time from exif metadata
    returns: (day_of_year, minute_of_day) or (None, None)
    """
    # common exif datetime tags
    datetime_tags = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
    dt_str = None
    for tag in datetime_tags:
        if tag in exif_data:
            dt_str = exif_data[tag]
            break
    if not dt_str:
        return None, None
    try:
        # try standard exif format YYYY:MM:DD HH:MM:SS
        dt = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        try:
            # try iso format YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS
            dt = datetime.fromisoformat(dt_str.replace(' ', 'T'))
        except ValueError:
            print(f"Could not parse datetime string: {dt_str}")
            return None, None
    day_of_year = dt.timetuple().tm_yday
    minute_of_day = dt.hour * 60 + dt.minute
    return day_of_year, minute_of_day


def classify_species(model, image_path, labels, return_prob=False):
    """
    labels should be the opened labels.json, its a list of species taxonomy info
    returns: if return_prob is true, returns probability distribution over all classes
    list of top 5 species as dict
    [ {'index':index_in_labels_list,
       'taxonomy' : [species, specific_epithet, genus, ... , kingdom],
       'prob' : probability_image_is_this_species
      }, ... 5 times
    ]
    """
    # get image
    try:
        image = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Could not open image at {image_path}: {str(e)}")

    # extract exif metadata
    exif_data = {}
    exif_raw = image._getexif()
    if exif_raw:
        for tag_id, value in exif_raw.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_data[tag] = value

    # get metadata
    lat, lon = extract_gps_info(exif_data)
    day_of_year, minute_of_day = extract_datetime_info(exif_data)

    # no metadata
    if lat is None or lon is None or day_of_year is None or minute_of_day is None:
        md_tensor = torch.zeros(8, dtype=torch.float32)
        has_md = torch.tensor(0, dtype=torch.float32)
        print("Insufficient metadata. Using image only.")
    # yes metadata, encode
    else:
        lat_sin, lat_cos = sinusoidal_encoding(lat, 90)
        lon_sin, lon_cos = sinusoidal_encoding(lon, 180)
        day_sin, day_cos = sinusoidal_encoding(day_of_year, 366)
        min_sin, min_cos = sinusoidal_encoding(minute_of_day, 1440)
        md_tensor = torch.tensor([lat_sin, lat_cos, lon_sin, lon_cos, day_sin, day_cos, min_sin, min_cos],
                                 dtype=torch.float32)
        has_md = torch.tensor(1, dtype=torch.float32)

    # transform image
    data_config = timm.data.resolve_model_data_config(model)
    val_transforms = timm.data.create_transform(**data_config, is_training=False)
    image_tensor = val_transforms(image.convert('RGB'))

    # add batch dim and move to device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    image_tensor = image_tensor.unsqueeze(0).to(device)
    md_tensor = md_tensor.unsqueeze(0).to(device)
    has_md = has_md.unsqueeze(0).to(device)
    model = model.to(device)

    # inference
    model.eval()
    with torch.no_grad():
        logits = model(image_tensor, md_tensor, has_md).squeeze(0)  # eliminate batch dim
    probs = torch.softmax(logits, 0)
    if return_prob:
        return probs
    # label probabilities, indices in labels
    top5_probs, top5_indices = torch.topk(probs, k=5)
    # turn pred to top 5 species
    results = []
    for idx, prob in zip(top5_indices.tolist(), top5_probs.tolist()):
        entry = {
            "index": idx,
            "taxonomy": labels[idx],
            "prob": prob
        }
        results.append(entry)
    return results


#NEED TO FINISH ALL THIS BELOW
def sum_over_index_list(original_list, index_tuple_list):
    """
    Sums over a list of values using tuples of intervals to return
    a list of sums the size of the tuple list.
    This is used to sum the prop for a higher taxonomy level if species
    classification confidence is too low. When a confidence threshold is reached,
    the index of the largest element corresponds to the index of the name of
    the element in the taxonomy level where confidence was reached.
    :param original_list: a list of logits for every species
    :param index_tuple_list: a list of tuples [start, end] inclusive of each name
    where the difference is the number of species withing that taxonomy level name
    corresponds to the dict.keys() of the taxonomy level of interest
    :return:
    """
    sum_list = []
    for indices in index_tuple_list:
        sum_list.append(sum(original_list[indices[0]:indices[1] + 1]))
    return sum_list


def classify_species_or_tax(model, image_path, labels, tax_indices, threshold=0.2):
    # do normal inference
    probs = classify_species(model, image_path, labels, return_prob=True)
    # if above threshold, do as normal
    if max(probs) > threshold:
        # do normal inference
        top5_probs, top5_indices = torch.topk(probs, k=5)
        # turn pred to top 5 species
        results = []
        for idx, prob in zip(top5_indices.tolist(), top5_probs.tolist()):
            entry = {
                "index": idx,
                "taxonomy": labels[idx],
                "prob": prob
            }
            results.append(entry)
        return results
    # else, sum over higher levels until threshold reached
    else:
        tax_levels = ['genus', 'family', 'order', 'class', 'phylum', 'kingdon']
        for t in tax_levels:
            original_list = probs
            index_tuple_list = tax_indices[t][0]
            name_list = tax_indices[t][1]
            sum_list = sum_over_index_list(original_list, index_tuple_list)
            max_value = max(sum_list)
            if max_value > threshold:
                index_of_max = sum_list.index(max_value)
                name = name_list[index_of_max]
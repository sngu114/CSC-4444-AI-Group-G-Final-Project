import numpy as np
import shutil
import os
from pathlib import Path

# Configuration
NPZ_FILE = "image_paths.npy"
OUTPUT_DIR = "C:/Users/grayb/Downloads/selected_images/train_mini"
ORIGINAL_DIR = "C:/Users/grayb/Downloads/train_mini/train_mini"

def move_images_from_npz(npy_path, output_dir, original_dir, partition):
    """
    Move images from paths stored in an npz file to an output directory.
    Processes one image at a time to avoid memory issues.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the npz file
    print(f"Loading paths from {npy_path}")
    data = np.load(npy_path)
    #
    # # Get the array (adjust the key if needed - common keys are 'arr_0', 'paths', etc.)
    # # List available keys if uncertain
    # print(f"Available keys in npz file: {list(data.keys())}")
    #
    # # Replace 'arr_0' with the actual key containing your paths
    # key = list(data.keys())[0]  # Use first key by default
    # paths = data[key]
    #
    # print(f"Found {len(paths)} image paths")

    # Process each image one by one
    moved_count = 0
    skipped_count = 0
    error_count = 0

    for i, path in enumerate(data):
        # Convert to string if it's a numpy bytes object
        if isinstance(path, bytes):
            path = path.decode('utf-8')
        else:
            path = str(path)

        # Get the filename
        filename = os.path.basename(path)
        cutoff = 4 if partition=='val' else 11
        origin = os.path.join(original_dir, path[cutoff:])
        destination = os.path.join(output_dir, filename)

        # Check if source file exists
        if not os.path.exists(origin):
            print(f"[{i + 1}/{len(data)}] Skipped (not found): {origin}")
            skipped_count += 1
            continue

        # Check if destination already exists
        if os.path.exists(destination):
            print(f"[{i + 1}/{len(data)}] Skipped (already exists): {filename}")
            skipped_count += 1
            continue

        try:
            # Move the file
            shutil.move(origin, destination)
            moved_count += 1

            # Print progress every 100 images
            if (i + 1) % 100 == 0:
                print(
                    f"Progress: {i + 1}/{len(data)} processed ({moved_count} moved, {skipped_count} skipped, {error_count} errors)")

        except Exception as e:
            print(f"[{i + 1}/{len(data)}] Error moving {origin}: {str(e)}")
            error_count += 1

    # Final summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total images processed: {len(data)}")
    print(f"Successfully moved: {moved_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors: {error_count}")
    print("=" * 50)


import numpy as np
import os

# Configuration
INPUT_NPZ = "image_paths.npz"  # Replace with your npz file path
OUTPUT_NPZ = "image_paths_modified.npz"  # Output file with modified paths


def modify_paths_in_npz(input_npy):
    """
    Modify paths in npz file to remove middle directory.
    Changes: train_mini/04712_..._angustirostris/filename.jpg
    To: train_mini/filename.jpg
    """
    # Load the npz file
    print(f"Loading paths from {input_npy}")
    data = np.load(input_npy)


    # Modify each path
    modified_paths = []

    for path in data:
        # Convert to string if it's a numpy bytes object
        if isinstance(path, bytes):
            path_str = path.decode('utf-8')
        else:
            path_str = str(path)

        # Split the path into parts
        parts = path_str.split('/')

        # Keep the first part (train_mini) and last part (filename.jpg)
        if len(parts) >= 2:
            modified_path = f"{parts[0]}/{parts[-1]}"
        else:
            # If path doesn't match expected format, keep as is
            modified_path = path_str

        modified_paths.append(modified_path)

    # Convert back to numpy array
    modified_array = np.array(modified_paths)

    print(f"Example modified path: {modified_paths[0]}")

    # Save to new npz file
    print("Saving modified paths")
    np.save(input_npy, modified_array)

    print(f"Successfully saved {len(modified_paths)} modified paths")



if __name__ == "__main__":
    #train
    move_images_from_npz("C:/Users/grayb/Downloads/train_mini/train_image_paths.npy",
                         "C:/Users/grayb/Downloads/train_selected_images/train_mini",
                         "C:/Users/grayb/Downloads/train_mini/train_mini",
                         'train')
    modify_paths_in_npz("C:/Users/grayb/Downloads/train_mini/train_image_paths.npy")

    #val
    move_images_from_npz("C:/Users/grayb/Downloads/val/val_image_paths.npy",
                          "C:/Users/grayb/Downloads/val_selected_images/val",
                          "C:/Users/grayb/Downloads/val/val",
                         'val')
    modify_paths_in_npz("C:/Users/grayb/Downloads/val/val_image_paths.npy")
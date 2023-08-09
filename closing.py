import os
import json
from datetime import datetime
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from skimage import morphology
from scipy.ndimage import binary_fill_holes

# Create argparse
import argparse
parser = argparse.ArgumentParser(description='Closing')
parser.add_argument('--configs_json', type=str, default="configs/default.json", help='Path to configs json file')
args = parser.parse_args()

# Read configs json from argparse
with open(args.configs_json, "r") as f:
    configs = json.load(f)


# Create experiment directory
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
experiment_dir = os.path.join(configs["output_dir"], timestamp)
if not os.path.exists(experiment_dir):
    os.makedirs(experiment_dir)

# Filling original mesh
start_fill_time = datetime.now()
if "filled_mesh" not in configs["input_mesh"]:
    print("Filling in mesh")
    configs['input_mesh']['remeshed'] = os.path.join(experiment_dir, "remeshed_original_mesh.mgz")
    os.system(f"mris_remesh -i {configs['input_mesh']['path']} -o {configs['input_mesh']['remeshed']} --nvert {configs['input_mesh']['resample_nverts']}")

    configs['input_mesh']['filled_mesh'] = os.path.join(experiment_dir, "filled_mesh.mgz")
    os.system(f"mris_fill -r {configs['input_mesh']['resolution']} {configs['input_mesh']['remeshed']} {configs['input_mesh']['filled_mesh']}")

end_fill_time = datetime.now()
print("Filling time: ", end_fill_time - start_fill_time)

# Closing filled mesh
start_close_time = datetime.now()
pad = configs["closing"]["pad"]
mri = nib.load(configs['input_mesh']['filled_mesh'])
data = np.zeros(np.asarray(mri.get_fdata().shape) +2*pad)
data[pad:-pad, pad:-pad, pad:-pad] = mri.get_fdata()>0.5

if configs["closing"]["visualization"]:
    max_slices = data.shape[1] - 1
    fig, ax = plt.subplots()
    ax.imshow(data[:,max_slices//2,:], cmap="gray", aspect='equal')
    ax.set_title("Original Central Slice")
    ax.axis("off")

radius = configs["closing"]["radius"]
data = morphology.closing(
    data, 
    morphology.ball(radius/configs['input_mesh']['resolution'])
)

if configs["closing"]["visualization"]:
    max_slices = data.shape[1] - 1
    fig, ax = plt.subplots()
    ax.imshow(data[:,max_slices//2,:], cmap="gray", aspect='equal')
    ax.set_title("Closed Central Slice")
    ax.axis("off")

if configs["closing"]["fill_holes"]:
    data = binary_fill_holes(data)

    if configs["closing"]["visualization"]:
        max_slices = data.shape[1] - 1
        fig, ax = plt.subplots()
        ax.imshow(data[:,max_slices//2,:], cmap="gray", aspect='equal')
        ax.set_title("Filled Closed Central Slice")
        ax.axis("off")

data = data[pad:-pad, pad:-pad, pad:-pad]

# Save closed mesh
nib.save(
    nib.MGHImage(data, mri.affine, mri.header),
    os.path.join(experiment_dir, "closed_mesh.mgz")
)

end_close_time = datetime.now()
print("Closing time: ", end_close_time - start_close_time)

# Save configs json
with open(os.path.join(experiment_dir, "configs.json"), "w") as f:
    json.dump(configs, f, indent=4)


#Create Surfaces
if configs["create_surfaces"]:
    # Meshing/Remeshing
    os.system(f"mri_mc {os.path.join(experiment_dir, 'closed_mesh.mgz')} 1 {os.path.join(experiment_dir, 'surf_closed')}")
    os.system(f"mris_remesh -i {os.path.join(experiment_dir, 'surf_closed')} -o {os.path.join(experiment_dir, 'remeshed_surf_closed')} --nvert {configs['input_mesh']['resample_nverts']}")

    # Convert original surf to scanner
    os.system(f"mris_convert --to-scanner {configs['input_mesh']['remeshed']} {os.path.join(experiment_dir, 'original.surf')}")

    # Convert closed surf to scanner
    os.system(f"mris_convert --to-scanner {os.path.join(experiment_dir, 'remeshed_surf_closed')} {os.path.join(experiment_dir, 'closed.surf')}")

if configs["closing"]["visualization"]:
    plt.show()

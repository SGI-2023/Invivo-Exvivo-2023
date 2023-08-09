# Exvivo surface mesh reconstruction from in-vivo FreeSurfer meshes

This project aims to reconstruct the exvivo surface meshes of the brain from in-vivo FreeSurfer meshes. 

Our approach consists of:
1. Filling in mesh at high resolution into a 3D Volume
2. Closing the deep sulci of the brain
3. Meshing/Remeshing the 3D Volume using Marching Cubes

---

## Requirements

:warning: Warning: This installation was only tested on `Linux` 

1. [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)
2. `pip`

---

## Setup

```sh
pip install -r requirements.txt
```

---

## Usage

```sh
python closing.py <path-to-configs-file>
```


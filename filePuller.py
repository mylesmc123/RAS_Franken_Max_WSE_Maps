# This script will pull the "WSE (Max).Terrain.cudem_ft.tif" files from each plan and rename is based on the parent folder.
# each file will have a filepath like: "V:\projects\p00659_dec_glo_phase3\02_analysis\HECRASV6.5_BaseModel\010yr_Atlas_14\WSE (Max).Terrain.cudem_ft.tif"
# Where 010yr_Atlas_14 is the parent folder and the file will be renamed to "010yr_Atlas_14_WSE_Max.tif"
# each file will be copied to a new folder based on the event name.
# For ecample, the filepath above will be copied to ".\data\010yr\010yr_Atlas_14_WSE_Max.tif"
# %%
import os
import shutil
import glob

# %%
# find all the "WSE (Max).Terrain.cudem_ft.tif" files in the project directory
prj_dir = r"V:\projects\p00659_dec_glo_phase3\02_analysis\HECRASV6.5_BaseModel"
max_wse_files = glob.glob(os.path.join(prj_dir, "**", "WSE (Max).Terrain.cudem_ft.tif"), recursive=True)
max_wse_files
# %%
# for each file, copy it to the new directory and rename it
for file in max_wse_files:
    # get the parent folder name
    parent_folder = os.path.basename(os.path.dirname(file))
    # create the new file name
    new_file_name = f"{parent_folder}_WSE_Max.tif"
    # get the event name
    event_name = parent_folder.split("_")[0]
    # create the new file path
    new_file_path = os.path.join(f".\data\{event_name}", new_file_name)
    print("\n", file)
    print(new_file_path, "\n")
    # make sure the directory exists
    if not os.path.exists(os.path.dirname(new_file_path)):
        os.makedirs(os.path.dirname(new_file_path))
    # copy the file
    shutil.copy(file, new_file_path)
# %%
if not os.path.exists(os.path.dirname(new_file_path)):
    print (os.path.dirname(new_file_path))
    # make dir
    os.makedirs(os.path.dirname(new_file_path))
# %%

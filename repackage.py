import os
import sys
import shutil
import zipfile
import re


def repackage_wheel(original_wheel_path, suffix="+cpu"):
    # Extract the base name and directory of the original wheel
    base_name = os.path.basename(original_wheel_path)
    dir_name = os.path.dirname(original_wheel_path) or "."

    # Generate the new wheel name by inserting the suffix before the extension
    name_parts = base_name.split("-")
    if len(name_parts) < 5:
        print("Error: Unexpected wheel file name format.")
        sys.exit(1)

    version_index = 1  # Assuming the version is always the second part
    name_parts[version_index] += suffix  # Append the suffix to the version
    new_wheel_name = "-".join(name_parts)

    # Create a temporary directory for unpacking and repacking
    temp_dir = "temp_wheel_unpack"
    os.makedirs(temp_dir, exist_ok=True)

    # Unpack the wheel
    with zipfile.ZipFile(original_wheel_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Update the version in METADATA
    dist_info_dirs = [d for d in os.listdir(temp_dir) if d.endswith(".dist-info")]
    if not dist_info_dirs:
        print("Error: .dist-info directory not found in the wheel.")
        sys.exit(1)

    metadata_file = os.path.join(temp_dir, dist_info_dirs[0], "METADATA")
    with open(metadata_file, "r") as f:
        metadata = f.read()

    print(metadata[:100])
    new_metadata = re.sub(
        r"(?m)^Version: (.+)", lambda m: f"Version: {m.group(1)}{suffix}", metadata
    )
    print(new_metadata[:100])
    with open(metadata_file, "w") as f:
        f.write(new_metadata)

    # Repackage the wheel
    new_wheel_path = os.path.join(dir_name, new_wheel_name)
    shutil.make_archive(
        base_name=os.path.splitext(new_wheel_path)[0], format="zip", root_dir=temp_dir
    )
    os.rename(f"{os.path.splitext(new_wheel_path)[0]}.zip", new_wheel_path)

    # Cleanup
    shutil.rmtree(temp_dir)

    print(f"New wheel created: {new_wheel_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python repackage_wheel.py <path_to_wheel>")
        sys.exit(1)

    wheel_path = sys.argv[1]
    repackage_wheel(wheel_path)

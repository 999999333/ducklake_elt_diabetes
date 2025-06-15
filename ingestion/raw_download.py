import os
import requests
import zipfile
import shutil


def download_and_unzip(url, raw_folder, unzipped_folder):
    """
    Downloads a zip file from the given URL and unzips it to the given folder.

    :param url: URL of the zip file to download
    :param raw_folder: Folder to store the downloaded zip file
    :param unzipped_folder: Folder to store the unzipped files
    """
    if url is None or raw_folder is None or unzipped_folder is None:
        raise ValueError("url, raw_folder, and unzipped_folder must not be None")

    file_name = url.split("/")[-1]
    if file_name is None or file_name == "":
        raise ValueError("url must contain a valid file name")

    destination_path = os.path.join(raw_folder, file_name)

    os.makedirs(raw_folder, exist_ok=True)
    os.makedirs(unzipped_folder, exist_ok=True)

    # Remove existing zip file if present
    if os.path.exists(destination_path):
        try:
            os.remove(destination_path)
        except OSError as e:
            raise IOError(f"Failed to remove existing file at {destination_path}. {e}")

    # Clear the unzipped folder if it has any content
    for filename in os.listdir(unzipped_folder):
        file_path = os.path.join(unzipped_folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            try:
                os.unlink(file_path)
            except OSError as e:
                raise IOError(f"Failed to remove existing file at {file_path}. {e}")
        elif os.path.isdir(file_path):
            try:
                shutil.rmtree(file_path)
            except OSError as e:
                raise IOError(f"Failed to remove existing directory at {file_path}. {e}")

    print(f"Downloading from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise IOError(f"Failed to download file from {url}. {e}")

    if response.status_code == 200:
        try:
            with open(destination_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        except IOError as e:
            raise IOError(f"Failed to write file to {destination_path}. {e}")
        print(f"Download completed: {destination_path}")

        try:
            with zipfile.ZipFile(destination_path, 'r') as zip_ref:
                zip_ref.extractall(unzipped_folder)
        except zipfile.BadZipfile as e:
            raise IOError(f"Failed to unzip file {destination_path}. {e}")
        print(f"Files unzipped to: {unzipped_folder}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


# Download diabetes dataset
diabetes_url = "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"
diabetes_raw_folder = "lakehouse/diabetes/raw"
diabetes_unzipped_folder = "lakehouse/diabetes/unzipped"
download_and_unzip(diabetes_url, diabetes_raw_folder, diabetes_unzipped_folder)

# Download ICD-9 dataset
icd9_url = "https://www.cms.gov/medicare/coding/icd9providerdiagnosticcodes/downloads/icd-9-cm-v32-master-descriptions.zip"
icd9_raw_folder = "lakehouse/icd_9/raw"
icd9_unzipped_folder = "lakehouse/icd_9/unzipped"
download_and_unzip(icd9_url, icd9_raw_folder, icd9_unzipped_folder)

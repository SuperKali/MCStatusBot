import os
import sys
import requests
import json
import zipfile
import io
import shutil
from colorama import init, Fore, Style

init(autoreset=True)

REPO_API_URL = "https://api.github.com/repos/superkali/MCStatusBot/releases/latest"
TEMP_DIR = "temp_update"


with open('VERSION', 'r') as version_file:
    CURRENT_VERSION = version_file.read().strip()

def check_for_update():
    print(f"{Fore.CYAN}[MCStatusBot Update] Checking for updates...")
    
    try:
        response = requests.get(REPO_API_URL)
        
        if response.status_code != 200:
            print(f"{Fore.RED}[MCStatusBot Update] Failed to check for updates! Status code: {response.status_code}")
            return False, None
            
        data = response.json()
        latest_version = data["tag_name"]
        
        if latest_version == CURRENT_VERSION:
            print(f"{Fore.GREEN}[MCStatusBot Update] You are running the latest version: {CURRENT_VERSION}")
            return False, None
        
        print(f"{Fore.YELLOW}[MCStatusBot Update] Update available: {CURRENT_VERSION} → {latest_version}")
        result_data = {
            "current_version": CURRENT_VERSION,
            "latest_version": latest_version,
            "zipball_url": data["zipball_url"],
            "tag_name": data["tag_name"]
        }
        return True, result_data
    
    except Exception as e:
        print(f"{Fore.RED}[MCStatusBot Update] Error checking for updates: {e}")
        return False, None

def download_and_install_update(data):
    download_url = data["zipball_url"]
    print(f"{Fore.CYAN}[MCStatusBot Update] Downloading update from {download_url}...")
    
    try:
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"{Fore.RED}[MCStatusBot Update] Failed to download update!")
            return False
            
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR)
        
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(TEMP_DIR)
        
        extracted_dir = os.path.join(TEMP_DIR, os.listdir(TEMP_DIR)[0])
        
        print(f"{Fore.CYAN}[MCStatusBot Update] Backing up configuration files...")
        if os.path.exists("config.json"):
            shutil.copy("config.json", "config.json.bak")
        if os.path.exists("data.json"):
            shutil.copy("data.json", "data.json.bak")
            
        print(f"{Fore.CYAN}[MCStatusBot Update] Installing new files...")
        for item in os.listdir(extracted_dir):
            source = os.path.join(extracted_dir, item)
            destination = os.path.join(".", item)
            
            if item in ["config.json", "data.json"]:
                continue
                
            if os.path.isdir(source):
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        
        with open("VERSION", "w") as version_file:
            version_file.write(data["latest_version"])
                
        shutil.rmtree(TEMP_DIR)
        
        print(f"{Fore.GREEN}[MCStatusBot Update] Update to {data['tag_name']} completed successfully!")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}[MCStatusBot Update] Error installing update: {e}")
        return False

if __name__ == "__main__":
    update_available, data = check_for_update()
    
    if update_available:
        response = input(f"{Fore.YELLOW}Do you want to install the update? (y/n): ")
        if response.lower() == "y":
            success = download_and_install_update(data)
            
            if success:
                print(f"{Fore.GREEN}[MCStatusBot Update] Please restart the bot to apply the update.")
            else:
                print(f"{Fore.RED}[MCStatusBot Update] Update failed. Please try again or update manually.")
    
    sys.exit(0)
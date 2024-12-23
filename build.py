import logging
import subprocess
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_hailo_package():
    try:
        import hailo
    except ImportError:
        logger.error("Hailo python package not found. Please make sure you're in the Hailo virtual environment. Run 'source setup_env.sh' and try again.")
        sys.exit(1)

def run_shell_command(command, error_message):
    logger.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        logger.error(f"{error_message}. Exit code: {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"{command} succeeded")

def get_downloaded_files():
    resource_dir = os.path.join(os.path.dirname(__file__), 'hailo_apps_infra', 'resources')
    downloaded_files = []
    for root, _, files in os.walk(resource_dir):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), 'hailo_apps_infra')
            downloaded_files.append(relative_path)
    return downloaded_files

def main():
    check_hailo_package()
    logger.info("Compiling C++ code...")
    run_shell_command("./compile_postprocess.sh", "Failed to compile C++ code")
    logger.info("Downloading Resources...")
    run_shell_command("./download_resources.sh ", "Failed to download resources")

if __name__ == "__main__":
    main()

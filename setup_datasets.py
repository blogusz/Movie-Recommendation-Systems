"""
Automatic Dataset Downloader and Setup Script
==============================================

This script automatically downloads and sets up all required datasets for the
Movie Recommendation Systems project.

Datasets:
- MovieLens (1M, 25M) - Direct download from GroupLens
- Netflix Shows - Kaggle (requires API key)
- Netflix Prize - Kaggle (requires API key)
- TMDB Movies - Kaggle (requires API key)
- MyAnimeList - Kaggle (requires API key)

Usage:
    python setup_datasets.py

For Kaggle datasets, you need to:
1. Create a Kaggle account at https://www.kaggle.com
2. Go to Account Settings -> API -> Create New API Token
3. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\<username>\.kaggle\ (Windows)
"""

import sys
import urllib.request
import zipfile
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}\n")


def print_success(text):
    """Print success message."""
    print(f"[OK] {text}")


def print_info(text):
    """Print info message."""
    print(f"[INFO] {text}")


def print_warning(text):
    """Print warning message."""
    print(f"[WARNING] {text}")


def print_error(text):
    """Print error message."""
    print(f"[ERROR] {text}")


def download_file(url, destination, description):
    """Download a file with progress indication."""
    print_info(f"Downloading {description}...")
    try:

        def reporthook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\r  Progress: {percent}% ")
            sys.stdout.flush()

        urllib.request.urlretrieve(url, destination, reporthook)
        print()  # New line after progress
        print_success(f"Downloaded {description}")
        return True
    except Exception as e:
        print_error(f"Failed to download {description}: {e}")
        return False


def extract_zip(zip_path, extract_to, description):
    """Extract a ZIP file."""
    print_info(f"Extracting {description}...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        print_success(f"Extracted {description}")
        return True
    except Exception as e:
        print_error(f"Failed to extract {description}: {e}")
        return False


def setup_movielens():
    """Download and setup MovieLens datasets."""
    print_header("MovieLens Datasets")

    datasets_dir = Path("datasets/MovieLens")
    datasets_dir.mkdir(parents=True, exist_ok=True)

    movielens_datasets = [
        {
            "name": "MovieLens 1M",
            "url": "https://files.grouplens.org/datasets/movielens/ml-1m.zip",
            "filename": "ml-1m.zip",
            "extract_dir": "ml-1m",
        },
        {
            "name": "MovieLens 25M",
            "url": "https://files.grouplens.org/datasets/movielens/ml-25m.zip",
            "filename": "ml-25m.zip",
            "extract_dir": "ml-25m",
        },
    ]

    for dataset in movielens_datasets:
        extract_path = datasets_dir / dataset["extract_dir"]

        # Check if already exists
        if extract_path.exists() and any(extract_path.iterdir()):
            print_warning(f"{dataset['name']} already exists. Skipping...")
            continue

        # Download
        zip_path = datasets_dir / dataset["filename"]
        if not download_file(dataset["url"], zip_path, dataset["name"]):
            continue

        # Extract
        if extract_zip(zip_path, datasets_dir, dataset["name"]):
            # Clean up ZIP file
            zip_path.unlink()
            print_success(f"{dataset['name']} setup complete")


def check_kaggle_api():
    """Check if Kaggle API is available."""
    try:
        import kaggle

        print_success("Kaggle API is configured")
        return True
    except OSError:
        print_error("Kaggle API credentials not found")
        return False
    except ImportError:
        print_error("Kaggle package not installed")
        return False


def check_dataset_exists(path, dataset_name):
    """Check if a dataset already exists."""
    dataset_path = Path(path)
    if dataset_path.exists() and any(dataset_path.iterdir()):
        print_success(f"{dataset_name}: Already exists")
        return True
    return False


def setup_kaggle_dataset(dataset_id, extract_to, dataset_name):
    """Download and setup a Kaggle dataset."""
    try:
        import kaggle

        extract_path = Path(extract_to)
        extract_path.mkdir(parents=True, exist_ok=True)

        print_info(f"Downloading {dataset_name} from Kaggle...")
        kaggle.api.dataset_download_files(dataset_id, path=extract_to, unzip=True)
        print_success(f"{dataset_name} downloaded and extracted")
        return True

    except Exception as e:
        print_error(f"Failed to download {dataset_name}: {e}")
        return False


def setup_netflix_datasets(has_kaggle):
    """Setup Netflix datasets."""
    print_header("Netflix Datasets")

    # Check if datasets already exist
    netflix_shows_exists = check_dataset_exists(
        "datasets/Netflix/netflix", "Netflix Shows"
    )
    netflix_prize_exists = check_dataset_exists(
        "datasets/Netflix/netflix_prize", "Netflix Prize"
    )

    # If both exist, skip
    if netflix_shows_exists and netflix_prize_exists:
        return

    # If Kaggle API not configured, show manual instructions
    if not has_kaggle:
        print_warning("Kaggle API not configured - Manual download required")
        if not netflix_shows_exists:
            print_info("Netflix Shows:")
            print("  1. Go to: https://www.kaggle.com/datasets/shivamb/netflix-shows")
            print("  2. Click 'Download' button (requires Kaggle login)")
            print("  3. Extract netflix_titles.csv to: datasets/Netflix/netflix/")
            print()
        if not netflix_prize_exists:
            print_info("Netflix Prize:")
            print(
                "  1. Go to: https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data"
            )
            print("  2. Click 'Download' button (requires Kaggle login)")
            print("  3. Extract all files to: datasets/Netflix/netflix_prize/")
        return

    # Download missing datasets
    if not netflix_shows_exists:
        setup_kaggle_dataset(
            "shivamb/netflix-shows", "datasets/Netflix/netflix", "Netflix Shows"
        )

    if not netflix_prize_exists:
        setup_kaggle_dataset(
            "netflix-inc/netflix-prize-data",
            "datasets/Netflix/netflix_prize",
            "Netflix Prize",
        )


def setup_tmdb_dataset(has_kaggle):
    """Setup TMDB dataset."""
    print_header("TMDB Dataset")

    # Check if dataset already exists
    if check_dataset_exists("datasets/TMDB", "TMDB Movies"):
        return

    # If Kaggle API not configured, show manual instructions
    if not has_kaggle:
        print_warning("Kaggle API not configured - Manual download required")
        print_info("TMDB Movies:")
        print(
            "  1. Go to: https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies"
        )
        print("  2. Click 'Download' button (requires Kaggle login)")
        print("  3. Extract TMDB_movie_dataset_v11.csv to: datasets/TMDB/")
        return

    # Download dataset
    setup_kaggle_dataset(
        "asaniczka/tmdb-movies-dataset-2023-930k-movies", "datasets/TMDB", "TMDB Movies"
    )


def setup_anime_dataset(has_kaggle):
    """Setup MyAnimeList dataset."""
    print_header("MyAnimeList Dataset")

    # Check if dataset already exists
    if check_dataset_exists("datasets/anime", "MyAnimeList"):
        return

    # If Kaggle API not configured, show manual instructions
    if not has_kaggle:
        print_warning("Kaggle API not configured - Manual download required")
        print_info("MyAnimeList:")
        print(
            "  1. Go to: https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020"
        )
        print("  2. Click 'Download' button (requires Kaggle login)")
        print("  3. Extract all CSV files to: datasets/anime/")
        return

    # Download dataset
    setup_kaggle_dataset(
        "hernan4444/anime-recommendation-database-2020", "datasets/anime", "MyAnimeList"
    )


def verify_datasets():
    """Verify that all required datasets are present."""
    print_header("Verification")

    required_files = {
        "MovieLens 1M": "datasets/MovieLens/ml-1m/ratings.dat",
        "MovieLens 25M": "datasets/MovieLens/ml-25m/ratings.csv",
        "Netflix Shows": "datasets/Netflix/netflix/netflix_titles.csv",
        "Netflix Prize": "datasets/Netflix/netflix_prize",
        "TMDB": "datasets/TMDB/TMDB_movie_dataset_v11.csv",
        "MyAnimeList": "datasets/anime/anime.csv",
    }

    all_present = True
    for name, path in required_files.items():
        if Path(path).exists():
            print_success(f"{name}: Found")
        else:
            print_error(f"{name}: Missing")
            all_present = False

    return all_present


def print_kaggle_setup_instructions():
    """Print detailed Kaggle API setup instructions."""
    print_header("Kaggle API Setup (Optional)")
    print("To enable automatic downloads from Kaggle:")
    print()
    print("1. Create a Kaggle account at https://www.kaggle.com")
    print("2. Go to your Account Settings (click on profile picture)")
    print("3. Scroll to 'API' section")
    print("4. Click 'Create New API Token'")
    print("5. This downloads kaggle.json file")
    print("6. Place kaggle.json in:")
    print("   - Windows: C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json")
    print("   - Linux/Mac: ~/.kaggle/kaggle.json")
    print("7. Install kaggle package: pip install kaggle")
    print()
    print_info(
        "Alternatively, you can download datasets manually (see instructions above)"
    )
    print()


def main():
    """Main setup function."""
    print_header("Movie Recommendation Systems - Dataset Setup")
    print("This script will download and setup all required datasets.")
    print()

    # Create datasets directory
    Path("datasets").mkdir(exist_ok=True)

    # Check Kaggle API
    has_kaggle = check_kaggle_api()

    if not has_kaggle:
        print()
        print_kaggle_setup_instructions()

    print()

    # Setup datasets
    setup_movielens()
    setup_netflix_datasets(has_kaggle)
    setup_tmdb_dataset(has_kaggle)
    setup_anime_dataset(has_kaggle)

    # Verify
    print()
    all_present = verify_datasets()

    # Final message
    print_header("Setup Complete")
    if all_present:
        print_success("All datasets are ready!")
        print_info(
            "You can now run the Jupyter notebooks in recommendation_techniques/"
        )
    else:
        print_warning("Some datasets are missing.")
        if not has_kaggle:
            print_info("For Kaggle datasets, you can:")
            print("  Option 1: Setup Kaggle API and run this script again")
            print("  Option 2: Download manually from the URLs shown above")
        print_info(
            "Place downloaded files in the correct folders and run this script again to verify."
        )

    print()


if __name__ == "__main__":
    main()

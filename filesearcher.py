import os
import zipfile
import rarfile
import tarfile
import py7zr
import pandas as pd
import colorama
import logging
from logging.handlers import RotatingFileHandler
from colorama import Fore
from tqdm.asyncio import tqdm
from concurrent.futures import ThreadPoolExecutor
import re
import time
import asyncio

colorama.init(autoreset=True)

# Rotating log file setup
log_handler = RotatingFileHandler('filesearch_log.txt', maxBytes=5 * 1024 * 1024, backupCount=3)  # 5MB logs, 3 backups
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

matches = []

# Predefined terms
predefined_terms = {
    "snapchat": ["cache_controller.db", "SCContent", "arroyo.db", "scdb-27.sqlite3"],
    "protonmail": ["proton", "protonmail"],
    "torbrowser": ["tor.browser", "torbrowser", "tor-browser", ".onion"],
    "wickr": ["wickr", "wickr pro", "wickrpro", "wickr me", "wickrme", "mywickr"],
    "whatsapp": ["whatsapp", "messages.db", "com.whatsapp.conversation", "msgstore.db.crypt12", "msgstore.db.crypt14"],
    "sqlite databases": [".sqlite", ".db"],
    "video": [".mp4", ".mov", ".avi", ".wmv", ".flv", ".mkv"],
    "pictures": [".jpg", ".jpeg", ".gif", ".bmp", ".tiff"]
}

interesting_file_types = {
    "SQLite Databases": [".sqlite", ".db"],
    "Plist Files": [".plist"],
    "Image and Media Files": [".jpg", ".heic", ".mp4", ".mov"],
    "Backup Files": [".bak", ".backup"],
    "Application Cache and Log Files": [".log", ".cache"],
    "Browser Data": [".db", ".plist", ".txt"],
    "Keychain Files": [".db"],
    "Text and Document Files": [".txt", ".pdf", ".docx"],
    "Email Data": [".eml"],
    "Health and Fitness Data": [".db", ".json"],
}

encrypted_file_types = {
    "Keychain Database": ["keychain-2.db"],
    "WhatsApp Backup": ["msgstore.db.crypt12", "msgstore.db.crypt14"],
    "iTunes Backup": ["Manifest.db", "Manifest.plist", "Manifest.mbdb"],
    "Apple Wallet": ["pass.pkpass", ".dat"],
    "Encrypted SQLite Databases": [".sqlite", ".db"],
    "iCloud Data": [".enc"],
    "Media Files (Encrypted Apps)": ["snapmedia.db", "snapmedia2.db"],
    "Health and Fitness Data (Encrypted)": ["healthdb_secure.sqlite"],
    "iOS System Files": [".keybag"]
}

# Memory-efficient async file search
async def async_search_term_in_file(file_data, file_name, search_terms, archive_path, regex=False, case_sensitive=False, max_size_kb=None):
    try:
        read_size = max_size_kb * 1024 if max_size_kb else -1
        content = await asyncio.to_thread(file_data.read, read_size)

        if not regex:
            content_decoded = content.decode('utf-8', errors='ignore').lower() if not case_sensitive else content.decode('utf-8', errors='ignore')
        else:
            content_decoded = content.decode('utf-8', errors='ignore')

        for term in search_terms:
            if regex:
                if re.search(term, content_decoded, re.IGNORECASE):
                    matches.append({
                        "Path+Filename": os.path.join(archive_path, file_name),
                        "Archive Path": archive_path,
                        "Search Term Found": term
                    })
                    return True
            else:
                if term.lower() in content_decoded or term.lower() in file_name.lower():
                    matches.append({
                        "Path+Filename": os.path.join(archive_path, file_name),
                        "Archive Path": archive_path,
                        "Search Term Found": term
                    })
                    return True
    except Exception as e:
        logging.error(f"Error reading file {file_name} in archive {archive_path}: {e}")
    return False


async def process_archive_with_progress(archive_path, search_terms, file_extensions, regex, case_sensitive, max_size_kb, pbar):
    handlers = {
        ".zip": (zipfile.ZipFile, lambda archive: archive.namelist()),
        ".rar": (rarfile.RarFile, lambda archive: [file.filename for file in archive.infolist()]),
        ".tar": (tarfile.open, lambda archive: [file.name for file in archive.getmembers() if file.isfile()]),
        ".7z": (py7zr.SevenZipFile, lambda archive: archive.getnames()),
    }
    ext = os.path.splitext(archive_path)[1].lower()
    handler, get_file_list = handlers.get(ext, (None, None))

    if not handler:
        logging.warning(f"Unsupported archive format: {ext}")
        return

    try:
        with handler(archive_path, 'r') as archive:
            file_list = get_file_list(archive)
            tasks = []

            for file_name in file_list:
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_extensions and file_ext not in file_extensions:
                    continue  # Skip files that don't match the selected extensions

                try:
                    file_data = archive.open(file_name)
                    # Wrap the async function to include progress bar update after completion
                    tasks.append(
                        update_progress_after_task(
                            async_search_term_in_file(file_data, file_name, search_terms, archive_path, regex, case_sensitive, max_size_kb),
                            pbar
                        )
                    )
                except Exception as e:
                    logging.error(f"Error opening file {file_name} in archive {archive_path}: {e}")

            if tasks:
                await asyncio.gather(*tasks)  # Ensure all file tasks complete

    except Exception as e:
        logging.error(f"Error processing {archive_path}: {e}")

async def update_progress_after_task(task, pbar):
    result = await task  # Wait for the task to finish
    pbar.update(1)  # Update the progress bar
    return result

# Display summary
def display_summary(total_files, matches_found, time_taken):
    print(Fore.CYAN + "-" * 40)
    print(Fore.GREEN + "Processing Complete!")
    print(Fore.YELLOW + f"Total Archives Processed: {total_files}")
    print(Fore.YELLOW + f"Total Matches Found: {matches_found}")
    print(Fore.YELLOW + f"Time Taken: {time_taken:.2f} seconds")
    print(Fore.CYAN + "-" * 40)

# Pretty print options
def pretty_print_options(title, options):
    print(Fore.CYAN + f"{title}:")
    print(Fore.CYAN + "-" * 40)
    for key, values in options.items():
        print(f"{Fore.YELLOW}{key:<25}{Fore.WHITE}{', '.join(values)}")
    print(Fore.CYAN + "-" * 40)

# Main function
def main():
    print(Fore.MAGENTA + 'Filesearcher v1.0')
    term_choice = input("Use predefined terms or custom terms? (Enter 'predefined' or 'custom'): ").strip().lower()

    search_terms = []
    regex, case_sensitive = False, False

    if term_choice == 'predefined':
        pretty_print_options("Predefined Search Term Groups", predefined_terms)
        choice = input("Enter the name(s) of predefined term groups to use (comma-separated): ").strip().lower()
        selected_groups = [group.strip() for group in choice.split(",")]
        for group in selected_groups:
            if group in predefined_terms:
                search_terms.extend(predefined_terms[group])
    elif term_choice == 'custom':
        search_terms = input("Enter custom search terms, separated by commas: ").strip().split(",")
        search_terms = [term.strip() for term in search_terms if term.strip()]
        regex = input("Use regex? (Y/N): ").strip().lower() == 'y'
        case_sensitive = input("Case-sensitive search? (Y/N): ").strip().lower() == 'y'

    pretty_print_options("File Type Options", interesting_file_types)
    limit_types = input("Do you want to limit the search to specific file types? (Y/N): ").strip().lower()

    file_extensions = None
    if limit_types == 'y':
        print("Enter the categories you want to limit to (e.g., 'Image and Media Files, Text and Document Files').")
        selected_categories = input("Enter categories (comma-separated): ").strip().split(",")
        selected_categories = [category.strip() for category in selected_categories if category.strip()]
        file_extensions = [ext for category in selected_categories if category in interesting_file_types
                           for ext in interesting_file_types[category]]

    if file_extensions:
        print(Fore.GREEN + f"Limiting search to file types: {', '.join(file_extensions)}")

    input_path = input("Enter path to a file or directory: ").strip()
    if not os.path.exists(input_path):
        print(Fore.RED + "Invalid path.")
        return

    max_size_kb = 5120 if input("Skip files larger than 5MB? (Y/N): ").strip().lower() == 'y' else None

    archive_paths = []
    if os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            archive_paths.extend([os.path.join(root, file) for file in files if file.endswith(('.zip', '.rar', '.tar', '.7z'))])
    else:
        archive_paths = [input_path]

    if not archive_paths:
        print(Fore.RED + "No valid archives found.")
        return

    start_time = time.time()

    # Process archives asynchronously with progress bar
    asyncio.run(process_all_archives(archive_paths, search_terms, file_extensions, regex, case_sensitive, max_size_kb))

    end_time = time.time()
    display_summary(len(archive_paths), len(matches), end_time - start_time)

    if matches:
        df = pd.DataFrame(matches, columns=["Path+Filename", "Archive Path", "Search Term Found"])
        df.to_excel("search_results.xlsx", index=False)
        print(Fore.GREEN + "Results saved to 'search_results.xlsx'.")

async def process_all_archives(archive_paths, search_terms, file_extensions, regex, case_sensitive, max_size_kb):
    # Count total files across all archives for progress tracking
    total_files = 0
    handlers = {
        ".zip": (zipfile.ZipFile, lambda archive: archive.namelist()),
        ".rar": (rarfile.RarFile, lambda archive: [file.filename for file in archive.infolist()]),
        ".tar": (tarfile.open, lambda archive: [file.name for file in archive.getmembers() if file.isfile()]),
        ".7z": (py7zr.SevenZipFile, lambda archive: archive.getnames()),
    }

    for archive_path in archive_paths:
        ext = os.path.splitext(archive_path)[1].lower()
        handler, get_file_list = handlers.get(ext, (None, None))
        if handler:
            try:
                with handler(archive_path, 'r') as archive:
                    total_files += len(get_file_list(archive))
            except Exception as e:
                logging.error(f"Error accessing {archive_path}: {e}")

    # Unified progress bar for all files
    with tqdm(total=total_files, desc="Processing All Archives") as pbar:
        tasks = [
            process_archive_with_progress(archive_path, search_terms, file_extensions, regex, case_sensitive, max_size_kb, pbar)
            for archive_path in archive_paths
        ]
        await asyncio.gather(*tasks)  # Ensure all tasks complete before proceeding
        pbar.close()  # Explicitly close the progress bar

if __name__ == "__main__":
    main()

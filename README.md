# File-searcher

Filesearcher is a Python-based tool designed for efficient and customizable archive file searching. It supports multiple archive formats, including .zip, .rar, .tar, and .7z, allowing users to search inside compressed files for specific terms or patterns.

Key Features:
*  Predefined and Custom Search Terms: Includes predefined groups for commonly        
   searched items (e.g., Snapchat, WhatsApp, Tor Browser) and allows custom term or 
   regex-based     searches.
*  Search by File Type: Supports filtering by specific file types, such as images,    
   SQLite databases, or encrypted files.
*  Asynchronous Processing: Uses asyncio and multithreading for fast, memory-efficient 
   searching.
*  Progress Tracking: Displays a unified progress bar for all files being processed.
*  Export Results: Outputs search results to an Excel file with details like file 
   paths, archive names, and matched terms.
*  File Size Control: Option to skip files larger than 5MB for faster processing.
*  Error Logging: Handles errors gracefully and logs them for troubleshooting.

Whether you're a digital forensic analyst or need an efficient way to search within archives, Filesearcher provides a versatile solution with advanced customization options.

Dependencies:
* os - Standard library for file and directory operations.
* zipfile - Standard library for handling .zip archives.
* rarfile - External library for handling .rar archives.
* tarfile - Standard library for handling .tar archives.
* py7zr - External library for handling .7z archives.
* pandas - External library for data manipulation and exporting results to Excel.
* colorama - External library for colored terminal text output.
* logging - Standard library for logging errors and events.
* logging.handlers - For handling rotating log files.
* tqdm - External library for progress bars.
* concurrent.futures - Standard library for multithreading support.
* re - Standard library for regular expression handling.
* time - Standard library for timing execution.
* asyncio - Standard library for asynchronous operations.

Use pip to install all dependencies:
pip install rarfile py7zr pandas colorama tqdm

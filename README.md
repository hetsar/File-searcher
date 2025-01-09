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

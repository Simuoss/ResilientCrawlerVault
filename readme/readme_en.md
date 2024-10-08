
<div align="center">
    <h1> ResilientCrawlerVault | 灵犀爬虫 </h1>
</div>

<div align="center">  
    <img src="https://img.shields.io/badge/Version-1.2.0-blue.svg" alt="Version">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">

【[简体中文](../README.md)】         【[English](./readme_en.md)】  
</div>  

## 📖 Introduction

**ResilientCrawlerVault** is a highly intelligent and stable web crawler program designed for large-scale data collection and processing. It efficiently iterates through all web pages under a specific domain and offers a powerful set of features:

- **Real-Time Progress and Statistics Display**: The program provides real-time updates on crawling progress and statistics, helping users monitor the process and adjust their strategy as needed.

- **Two-Level Deduplication Mechanism**: It implements real-time deduplication at both the URL and content levels, ensuring that the same web page is not crawled multiple times and that pages with similar content are not stored redundantly. This ensures data uniqueness and accuracy.

- **Customizable HTML Tag Filtering**: Users can define rules to exclude unnecessary HTML tags or content, ensuring that the collected data is cleaner and more structured, meeting the needs of subsequent processing and analysis.

- **Automatic Markdown Conversion**: The content of the crawled web pages is automatically converted into Markdown format, which is easy to edit, store, process, analyze, and display. This is especially useful for input into vector databases.

- **Robust Breakpoint Resumption**: In the event of an unexpected power outage or interruption, the program seamlessly resumes the crawling task. This mechanism ensures continuous data collection without having to restart from the beginning, improving task stability and reliability.

- **Comprehensive Redirection Handling**: The program intelligently handles webpage redirections, ensuring that every redirected URL is checked and doesn't lead outside the domain or to URLs prohibited by user rules.

- **File-to-Webpage Mapping**: It establishes a mapping relationship between each crawled file and the original webpage, allowing users to easily trace the data's origin, facilitating subsequent verification, management, and analysis.

**ResilientCrawlerVault** provides a comprehensive and reliable data collection solution, particularly suited for long-running tasks and scenarios involving complex web structures. Its intelligent features and high stability meet a wide range of data collection and processing needs.

### 📜 Changelog

- [2024/8/31] v1.2.0 Added **multi-threading support** for web crawling while retaining all previous features

### 🧰 Feature List

- [x] Supports iterative crawling of all web pages under a specific domain
- [x] Real-time progress and statistics display
- [x] Two-level deduplication (URL + content) to ensure data uniqueness
- [x] Supports customizable HTML tag filtering to improve data cleaning
- [x] Automatically converts web page content to Markdown format
- [x] Robust breakpoint resumption mechanism, seamlessly recovers even after power outages
- [x] Comprehensive redirection handling to ensure complete data capture
- [x] Establishes a mapping between crawled files and original web pages
- [ ] Customizable crawl depth and rules
- [ ] Enhanced data cleaning and formatting options with LLM integration
- [x] Multi-threading support to improve crawl efficiency
- [ ] Proxy support for IP pool rotation
- [ ] Improved Selenium support for dynamic web page crawling

## ✨ Quick Start

### Usage
1. Clone or download the repository locally:
    ```shell
    git clone https://github.com/Simuoss/ResilientCrawlerVault.git
    ```
2. Open a command line in the directory and install dependencies:
    ```shell
    pip install -r requirements.txt
    ```
3. Open and edit the `globle_var.py` file:
    - `domain`: Set the domain scope, so that only web pages within this domain are crawled
    - `start_url`: Set the starting URL for the crawl, from which the program will begin iterative crawling
    - `trans_md`: Set whether to enable Markdown conversion
    - Additional detailed configurations (e.g., request headers, exclusions, etc.) can be found in the comments of the `globle_var.py` file
4. After configuration, run the `main.py` file to start crawling:
    ```shell
    python main.py
    ```
    Crawled HTML files directory: `./html/{domain}/`  
    Cleaned Markdown files directory: `./md/{domain}/`  
    Files contained within web pages directory: `./files/{domain}/`  
    File-to-webpage mapping: `./files_mapping.jsonl` (the structure of this jsonl file is mentioned in `globle_var.py`)

### Development
1. Clone the project locally:
    ```shell
    git clone https://github.com/Simuoss/ResilientCrawlerVault.git
    ```
2. Open a command line in the directory and install dependencies:
    ```shell
    pip install -r requirements.txt
    ```
3. Open the project for development using your IDE.  
    > **main.py** : The main program entry point (creates thread pool)  
    >> **config.py** : Configuration file (does not involve multithreading)  
    >> **global_var.py** : Global variables (does not involve multithreading)  
    >> **get_resource.py** : All operations related to accessing the internet, such as saving webpages and downloading files (adds only one layer of lock to variables to ensure thread safety and prevent deadlock)  
    >> **text_processor.py** : All functions related to text processing. Can be executed independently to clean HTML files and convert them to MD files (does not involve multithreading)  
    >> **file_operator.py** : All classes and objects related to file operations (thread-safe)  
    >> **logger_setup.py** : Logger setup (does not involve multithreading)  

    > **get_links_only.py** : A standalone tool that only retrieves links. It iterates to get all links starting with a specific string and outputs them to a TXT file, but does not save the page content.


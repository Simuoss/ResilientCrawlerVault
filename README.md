<div align= "center">
    <h1> ResilientCrawlerVault | 灵犀爬虫 </h1>
</div>

<div align= "center">  
    <img src="https://img.shields.io/badge/Version-1.1.3-blue.svg" alt="Version">
    <img src="https://img.shields.io/badge/Build-Passing-green.svg" alt="Build">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">

【[简体中文](./readme.md)】         【[English](./readme_en.md)】  
</div>  

## 📖 介绍

**ResilientCrawlerVault** 是一款智能且高稳定性的网络爬虫程序，专为大规模数据收集与处理而设计。它能够高效地迭代式爬取特定域名下的所有网页，并提供了一系列强大的功能：

- **实时进度与统计信息显示**：程序提供实时的爬取进度和统计信息，可以帮助用户实时监控爬取过程，及时调整策略。

- **双层去重机制**：实现了URL和文件两级实时去重，确保同一网页不会被多次访问，且具有相似内容的网页不会重复保存，避免了内容重复存储，保证了数据的唯一性和准确性。

- **自定义HTML标签过滤**：用户可以设置过滤规则，排除不需要的HTML标签或内容，确保采集到的数据更加干净、结构化，符合后续处理和分析的需求。

- **自动Markdown转换**：爬取的网页内容会自动转换为Markdown格式，这种格式便于后续编辑、存储、处理、分析和展示，尤其便于输入向量数据库。

- **强大断点重续机制**：即使在意外断电或其他中断情况下，程序也能无缝恢复爬取任务。这种机制保证了数据采集的连续性，避免了从头开始的麻烦，提高了任务的稳定性和可靠性。

- **完善的重定向处理**：程序能够智能处理网页重定向问题，确保每次定向后的url都经过检测，不会流向站外或被用户设置禁止规则的url。

- **文件与网页映射**：为每个爬取的文件建立与原网页的映射关系。这一功能使得用户可以轻松追溯数据来源，方便进行后续的验证、管理和分析。

**ResilientCrawlerVault** 提供了一个全面、可靠的数据采集解决方案，特别适合需要长时间运行和处理复杂网络结构的场景。它的智能化功能和高稳定性能够满足各种数据收集和处理需求。

### 🧰 特性列表

- [x] 支持迭代式爬取特定域名下的所有网页
- [x] 实时进度和统计信息显示
- [x] URL+文件两级实时去重，确保数据唯一性
- [x] 支持自定义HTML标签过滤，提高数据清洗效果
- [x] 自动将网页内容转换为Markdown格式
- [x] 强大的断点重续机制，即使意外断电也能无缝恢复
- [x] 完善的重定向处理，保证完整数据抓取
- [x] 爬取的文件与原网页建立映射关系
- [ ] 自定义爬取深度和规则
- [ ] 借助LLM实现增强的数据清洗和格式化选项
- [ ] 多线程支持，提高爬取效率
- [ ] 添加代理功能以实现IP池轮换
- [ ] 完善Selenium支持，实现动态网页爬取

## ✨ 快速开始

### 使用
1. 克隆或直接下载仓库到本地：
    ```shell
    git clone https://github.com/Simuoss/ResilientCrawlerVault.git
    ```
2. 在目录打开命令行，安装依赖：
    ```shell
    pip install -r requirements.txt
    ```
3. 打开并编辑`globle_var.py`文件：
    - `domain`：设置域名界限，只爬取该域名下的网页
    - `start_url`：设置爬取的起始URL，程序将从该URL开始迭代式爬取
    - `trans_md`：设置是否开启Markdown格式转换功能
    - 其他详细配置（如请求头、排除项等等）请参考`globle_var.py`文件中的注释
4. 配置完成后，运行`main.py`文件即可开始爬取：
    ```shell
    python main.py
    ```
    爬取下的HTML文件目录：`./html/{domain}/`  
    清洗后的Markdown文件目录：`./md/{domain}/`  
    网页中包含的文件目录：`./files/{domain}/`  
    爬取的文件与原网页的映射关系：`./files_mappping.jsonl`（该jsonl文件的结构在`globle_var.py`文件中有提到）  

### 开发
1. 克隆项目到本地：
    ```shell
    git clone https://github.com/Simuoss/ResilientCrawlerVault.git
    ```
2. 在目录打开命令行，安装依赖：
    ```shell
    pip install -r requirements.txt
    ```
3. 使用你的IDE打开项目开发即可。
    > **main.py** : 主程序入口  
    >> **globle_var.py** : 配置文件与一些全局变量  
    >> **get_resource.py** : 访问互联网的操作都在这里，如保存网页、下载文件等  
    >> **text_processor.py** : 所有涉及处理文本的函数。可以单独执行，效果是将html文件清洗并转换为md文件  
    >> **file_operator.py** : 所有涉及文件操作的函数  
    >> **logger_setup.py** : 日志记录器设置  
 


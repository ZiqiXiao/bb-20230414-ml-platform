#!/bin/bash

# 在此定义你要清理的目录和文件
LOG_DIR="data/logs/"
LOG_FILE_PATTERN="*.log.*"  

# 删除匹配的文件
find "$LOG_DIR" -type f -name "$LOG_FILE_PATTERN" -mtime +2 -exec rm -f {} \;

# 在此定义你要清理的目录和文件
PR_DIR="data/predict_result/"
PR_FILE_PATTERN="*.csv"

# 删除匹配的文件
find "$PR_DIR" -type f -name "$PR_FILE_PATTERN" -mtime +0 -exec rm -f {} \;

# 在此定义你要清理的目录和文件
UL_DIR="data/uploads/"
UL_FILE_PATTERN="*.csv"

# 删除匹配的文件
find "$UL_DIR" -type f -name "$UL_FILE_PATTERN" -mtime +0 -exec rm -f {} \;
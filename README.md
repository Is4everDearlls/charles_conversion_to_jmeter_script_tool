# charles_conversion_to_jmeter_script_tool

# 1. Jenkins项目
### 1.1 新增文件参数，文件名称与项目目录下的 bar文件名称一致
### 1.2 构建时进入工作目录执行conversion.py即可
### 1.3 添加归档文件


# 2. 使用
2.1 Charles抓包后选择需要的Http请求并导出为 .har文件
2.2 上传 .har文件构建Jenkins项目或手动将文件替换掉项目目录下的 charles.har文件后执行conversion.py

<!--
 * @Author: Radon
 * @Date: 2021-08-25 14:18:15
 * @LastEditors: Radon
 * @LastEditTime: 2021-10-31 16:47:18
 * @Description: Hi, say something
-->
# fuzzing-tool-14

Fuzzing tool for the 14th institute

### server
* 负责插装
### client
* 生成种子文件
* 变异测试用例
* 计算校验码
### pack
打包为exe文件
```
pip install pyinstaller
pyinstaller -D -w -i server.ico Ui_window_server.py
pyinstaller -D -w -i client.ico Ui_window_client.py
```
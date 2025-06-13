@echo off 
cd /d "%~dp0"        :: 切换到脚本所在目录 
call myenv\Scripts\activate.bat   :: 激活虚拟环境 
python main.py        :: 执行Python脚本 
pause                :: 可选：执行后暂停窗口（调试用）
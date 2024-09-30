set CONDAPATH=C:\ProgramData\Miniconda3
set ENVPATH=C:\Users\JYuan\.conda\envs\xkcd-desktop
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%
cd /D C:\Code\XKCDaily
python xkcd-downloader.py
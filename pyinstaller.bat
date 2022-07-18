cd .env\Scripts\

pyinstaller --onefile  ../../run.py --distpath ../../dist/ --workpath ../../build/ --specpath ../../

cd ../../dist
ren run.exe hashgen.exe
cd ../
python release.py

PAUSE
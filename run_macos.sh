python3 -m venv venv
source venv/bin/activate
pip3 install playwright
playwright install
python3 main.py
open messages
rm -r ~/Library/Caches/ms-playwright
rm -r venv
sudo apt install python3.10-venv
sudo apt install -y portaudio19-dev python3-pyaudio
python3 -m venv .venv
. .venv/bin/activate
sudo apt install python3.10-venv
pip install -r requirements.txt
python agent.py download-files

# VECTORCLOUD
### A web interface for controlling Anki's Vector Robot

### CURRENT STATUS: DEVELOPER PREVIEW
WARNING: this is not a finished product and is being made available for testing purposes only. At this time, I am not providing any support regarding installation/setup any further than the instructions below.

### Installation
### Docker
```bash
docker create \
  --name=vectorcloud \
  -p 5000:5000 \
  -v path/to/data:/vectorcloud/vectorcloud/user_data \
  --restart unless-stopped \
  rmountjoy/vectorcloud:latest
```
### Python
Instructions are for linux. Windows not tested or officially supported.
```bash
virtualenv --python=python3.7.5 VectorCloudEnv
cd VectorCloudEnv && source bin/activate
git clone https://github.com/rmountjoy92/VectorCloud2.git
cd VectorCloud2 && pip install -r requirements.txt
python3 run.py
```
Then open a web browser and go to localhost:5000
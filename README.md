# rplace_timelapse
A cobbled together script to create focused (cropped and upscaled) timelapses of the r/place event. Based on 2023 event.
### Features:
- Graphical cropping - Pick the area from the full canvas.
- Auto-timestamp - Start from when your area appeared in the event.
- Calculates closest scalable 16:9 (or 9:16) resolution.
- Pixel-by-Pixel upscale - Through imagemagicks `convert -filter point resize`.
### The less good:
- cobbled together tools with no solid end user in mind.
- when the image-processing started - if you want to abort, kill the terminal.

## Prerequisites
Have a directory with the raw images in the resolution 3000x2000. 
Raw files can be obtained here [place-atlas-2023-scraped-canvas](https://archive.org/details/place-atlas-2023-scraped-canvas) which has to be processed.
- First unpack the files
    - either with this oneliner: `for file in *tar; do dir=$(basename "$file" .tar); mkdir "$dir"; tar -xvf "$file" -C "$dir" ; done`
    - or with the mini-script [unpacker.sh](https://github.com/mag37/rplace_timelapse/blob/main/unpacker.sh)
- Then run the [montage_all.sh](https://github.com/mag37/rplace_timelapse/blob/main/montage_all.sh) script, takes quite a while (need to test, seems slow).

### Installed packages:
- ffmpeg
- imagemagick
- python3


## How To Use

- Get the script and requirements file.
- Create a python virtual environment
    - `python3 -m venv venv`
- Activate virtual environment
    - `source venv/bin/activate`
- Install required packages
    - `pip install -r requirements.txt`
- Edit the script and set your directory of raw images
    - Example: `raw_images = "ALL/"`


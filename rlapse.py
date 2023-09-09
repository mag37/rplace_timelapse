import sys
import glob
import os
import locale
from datetime import datetime
import calendar
import climage
import cv2

## USER DEFINED VARIABLES:
raw_images = "ALL/" # location of raw images
canvas_temp = "canvas.png" # template canvas file
clip_length=30 # length of the output clip in seconds

def clean_dirname(sourcestring, removestring=" %:/,.\\[]<>*?"):
    return ''.join([c for c in sourcestring if c not in removestring])

def image_to_ratio(w, h):
    user_width= w
    user_height= h
    while True:
        base = w//16 if w/h < 16/9 else h//9
        base_resolution = ((base * 16), (base * 9))
        # if the suggested resolution is smaller than the user defined, pad with 4 pixels and retry
        if base_resolution[0] < user_width or base_resolution[1] < user_height: 
            w+=4
            h+=4
        else:
            if user_width > user_height: # portrait or landscape
                return base * 16, base * 9, (1080 / (base * 9)) * 100
            else:
                return base * 9, base * 16, int((1080 / (base * 9)) * 100)

def cd(dir): # TODO: look at a context manager?
    if os.path.exists(dir):
        os.chdir(dir)
    else:
        print(f"{dir} does not exist, exiting.")
        exit()

def uniq_dir(dir):
    counter = 1
    dir_name = dir
    while os.path.exists(dir):
        dir = f"{dir_name}_{counter}"
        counter += 1
    return dir

def progress_counter(current, total):
    percentage = round(100.0 * current/float(total),1)
    sys.stdout.write(f"{current}/{total} images processed, {percentage}% complete \r")
    sys.stdout.flush()

def mark_crop(action, x, y, flags, params):
  global start_coords, stop_coords
  if action == cv2.EVENT_LBUTTONDOWN:
    start_coords = [x,y]
  elif action == cv2.EVENT_LBUTTONUP:
    stop_coords = [x,y]    
    cv2.rectangle(img, start_coords, stop_coords, (0,255,0),2, 8)
    cv2.imshow(window,img)

def pointInField(point,area):
    x1, y1, x2, y2 = area
    x, y = point
    if (x1 < x and x < x2):
        if (y1 < y and y < y2):
            return True
    return False

# TODO: Rewrite with new_start + ratio? Not important
def autoTimestamp():
    # calculate center point of cropped rectangle
    center_point = (int((start[0]+stop[0])/2),int((start[1]+stop[1])/2))
    # check in which period the chosen point appears
    for period in periods:
        area = periods[period][0:4]
        if pointInField(center_point,area):
            timestamp = periods[period][4]
            print(timestamp)
            return timestamp

# TODO: find a way to break the loop with keyboard interaction. Threading?
def process_all_images(file_list):
    que_number = 0
    for file in file_list:
        que_number += 1
        new_filename = file.replace(".png", "-cropscale.png")
        convert_run = f"convert {file} {crop_arguments} {work_dir}/{new_filename}"
        os.system(convert_run)
        progress_counter(que_number, image_count)

# TODO: add a few different canvas templates?
# Graphical picker or not
coord_picker = input("Pick coordinates from image? [y/n] \n(if 'no' - type them manually with the help of https://2023.place-atlas.stefanocoding.me ): ")
if (coord_picker.lower() == "yes" or coord_picker.lower() == "y") :
    # load image:
    img = cv2.imread(canvas_temp, 1)
    start_coords=[]
    stop_coords=[]
    # create window to apply settings
    window = "preview"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    # draw double text for fake outline
    cv2.putText(img, f"Click+Hold to mark a rectangle, top left to bottom right. Press any key when done.", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 20)
    cv2.putText(img, f"Click+Hold to mark a rectangle, top left to bottom right. Press any key when done.", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
    cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # displaying the image
    cv2.imshow(window, img)
    cv2.setMouseCallback(window, mark_crop) # run the function to mark area
    # exit on keypress
    cv2.waitKey(0)
    if len(start_coords) != 0:
        start = [start_coords[0],start_coords[1]]
        stop = [stop_coords[0],stop_coords[1]]
        print(start)
        print(stop)
    # close the window
    cv2.destroyAllWindows()

else:
    start = list(int(x.strip()) for x in input("Start coordinates, format -123,456 :").split(','))
    stop = list(int(x.strip()) for x in input("Stop coordinates, format -456,789 :").split(','))
    # Adjust for negative coordinates by 2023.place-atlas.stefanocoding.me , w-1500,h-1000
    start[0] += 1500
    start[1] += 1000
    stop[0] += 1500
    stop[1] += 1000


# User input to choose project name - output dir+file will be based on this
while True:
  project_name = clean_dirname(input("Name of Community/Artwork: "))
  if project_name.strip() != '':
      break

# calculate resolution based o coordinates
user_resolution = ((stop[0]-start[0]), (stop[1]-start[1]))
print(user_resolution)

# calculate 16:9 aspect ratio and scale percentage
ratio = image_to_ratio(user_resolution[0], user_resolution[1])

# new starting coordinates based on resize of cropped area
new_start = [start[0]-int((ratio[0]-user_resolution[0])/2), start[1]-int((ratio[1]-user_resolution[1])/2)]
# logic to stay within the canvas max resolution
for i, s in enumerate(new_start):
    new_start[i] = max(0, new_start[i])
if (new_start[0]+ratio[0]) > 3000:
    new_start[0] = new_start[0] - ((new_start[0]+ratio[0]) - 3000)
if (new_start[1]+ratio[1]) > 2000:
    new_start[1] = new_start[1] - ((new_start[1]+ratio[1]) - 2000)

## Fix locale-settings breaking the date
previous_locale = locale.getlocale()
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

# logic to auto-set timestamp depending on chosen coordinates
# coordinates adjusted (x:+1500,y:+1000)
periods = {
        "zero": [1000, 500, 2000, 1500, "Thu, 20 Jul 2023 13:01:20 GMT"],
        "one":  [1000, 500, 2500, 1500, "Fri, 21 Jul 2023 16:30:00 GMT"],
        "two":  [2500, 500, 2500, 1500, "Sat, 22 Jul 2023 08:30:00 GMT"],
        "three": [2500, 0, 2500, 1500, "Sat, 22 Jul 2023 23:30:00 GMT"],
        "four":  [2500, 0, 2500, 2000, "Sun, 23 Jul 2023 18:30:00 GMT"],
        "five":  [0, 0, 2500, 2000, "Mon, 24 Jul 2023 02:30:00 GMT"],
        "six":  [0, 0, 3000, 2000, "Mon, 24 Jul 2023 18:00:00 GMT"],
    }

## TODO: allow custom timestamp?
# timestamp = input("Atlas Timestamp for starting: ")
timestamp = input("Atlas Timestamp for starting point - leave blank for auto (based on area): ") or autoTimestamp()
# timestamp = autoTimestamp()

# create preview-image with imagemagick
if not os.path.exists("previews"):
    os.makedirs("previews")
os.system(f"\nconvert {canvas_temp} -crop {ratio[0]}x{ratio[1]}+{new_start[0]}+{new_start[1]} -filter point -resize {ratio[2]}% previews/{project_name}.png")

print("Preview of the cropped area, will look very pixelated due to the terminal:")
## Climage - show image in terminal:
preview = climage.convert(f"previews/{project_name}.png", is_unicode=True, is_truecolor=True, is_256color=False, is_16color=False, is_8color=False, width=120, palette="default")
print(preview)

# TODO: Change to Continue/Restart/Quit
user_choice = input("Looks good! Continue with the convertion? (can take a while, uninterruptable) [y/n]: ")
if not (user_choice.lower() == "yes" or user_choice.lower() == "y") :
    exit()

# Set arguments from variables to use with the image processing 
crop_arguments = f"-crop {ratio[0]}x{ratio[1]}+{new_start[0]}+{new_start[1]} -filter point -resize {ratio[2]}%"
# Create epoch timestamp
epoch = calendar.timegm(datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z").utctimetuple())

origin_dir = os.getcwd() # Get current dir to return later
raw_images = raw_images.removesuffix("/")
cd(raw_images) # CD to raw images

# Make list of all pngs:
file_list = glob.glob("*.png")
file_list.append(f"{epoch}.png") 
file_list.sort() # Sort list
fake_index = file_list.index(f"{epoch}.png") + 1
clean_list = file_list[fake_index:] # Grab only images after timestamp

# count frames to calculate length
image_count = len(clean_list)
frames = image_count / clip_length

# define name and create dir
work_dir = uniq_dir(project_name)
os.mkdir(work_dir)
print(f"Output directory: {work_dir}")

# iterate all the images in the array, crop+scale
process_all_images(clean_list)

cd(work_dir) # CD to the processed images
# stitch together the clip from the cropped images
ffmpeg_run = f"ffmpeg -loglevel error -stats -framerate {frames} -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -filter:v fps=fps=60 {project_name}.mp4"
os.system(ffmpeg_run)
# return to starting directory
cd(origin_dir)

print(f"All done! Timelapse at {raw_images}/{work_dir}/{project_name}.mp4")
exit()

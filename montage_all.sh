#!/usr/bin/env bash
# Should be placed and run in the same dir as all unpacked images
# images should be in subdirs images[2-5] 

# Create output dir
mkdir -p ALL
starting_dir=$(pwd) # to get full path
for dir in images2 images3 images4 images5 # iterate over subdirectories
do
  echo "Currently processing directory: $dir"
  cd "${starting_dir}/${dir}" || { echo "No $dir directory, exiting." ; exit 1 ; }
  if [[ $dir == "images2" ]] ; then  # different naming scheme for images2 - collection
    ls -1 *.png | sed 's/^..//;s/....$//' | uniq > ${dir}.list
  else 
    ls -1 *.png | sed 's/......$//' | uniq > ${dir}.list
  fi
  while read -r line
  do
    for num in {0..5}
    do
      if [[ $dir == "images2" ]] ; then # different naming scheme for images2 - collection
        [[ -f ./${num}-${line}.png ]] && declare canvas_${num}="./${num}-${line}.png" || declare canvas_${num}="xc:white"
      else
        [[ -f ./${line}-${num}.png ]] && declare canvas_${num}="./${line}-${num}.png" || declare canvas_${num}="xc:white"
      fi
    done
    # create the montaged full canvas file
    montage ${canvas_0} ${canvas_1} ${canvas_2} ${canvas_3} ${canvas_4} ${canvas_5} -geometry 1000x1000+0+0 ${starting_dir}/ALL/${line}.png
  done < ${dir}.list # read the list of files
done
cd ${starting_dir} # return to base directory

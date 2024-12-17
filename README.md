Contains code for CrowdHydrology Data Visualizer/Scraper:
Link to CrowdHydrology: http://www.crowdhydrology.com/

. Developed Python script that parses up to 13,000 messages leveraging Twilio’s REST API and sorts them into folders according to their station ID. Each folder contains all recorded images from that site, which are timestamped aiding examination of environmental change
. Implemented a GUI using tkinter that acts as a slideshow for each station, allowing for users to view all recorded images for that site and change to be closely monitored
. yolov4 people-detector model used to filter out images with people present in them to preserve data quality. Can be found here: https://github.com/AlexeyAB/darknet

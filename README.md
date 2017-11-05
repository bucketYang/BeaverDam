gemfield/video_annotation_cv
=========

Video annotation tool for deep learning training labels

## About
With the easist installation you can:
- Draw bounding boxes in videos
- Draw bounding boxes in images
- Add additional attributes in bounding boxes
- Use a custom keyframe scheduler instead of user-scheduled keyframes


## Installation

 1. Make sure you are on a Linux system with docker-ce installed.
 2. Clone this repository to directory xxxxxx, e.g. /home/gemfield/BeaverDam.
 3. Launch the annotation server by following command:
```bash
docker run -d -p 80:80 -v xxxxxx:/home/gemfield/BeaverDam gemfield/video_annotation_cv
```
 4. Now you can access the annotation system on your Chrome by http://<your_ip>

## Support

For help setting up BeaverDam for your application/company, please contact Gemfield or leave an issue.

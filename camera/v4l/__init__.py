if __name__ == "__main__":
   from grabImage import *

   image = grab_image("/dev/video0", 384, 240)

   for x in range(10):
      print image[x]

   free_image(image)
   

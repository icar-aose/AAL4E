from pickletools import uint8
import cv2, numpy
'''
    Script for the recognition of a state of idling or the presence of motion in a scene. The video used can be real live captured using "dev/video0" source 
'''

#Initialization of the stream
def video_init():
    #Capturing video from /dev/video0 source
    try:
        video_input = cv2.VideoCapture(0)
    except RuntimeError:#Notice if there's no possibility to open the stream due to it being busy or unaccessible
        raise RuntimeError("Unable to open video stream")
    
    #Gets source resolution
    video_height = int(video_input.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_width = int(video_input.get(cv2.CAP_PROP_FRAME_WIDTH))

    #Returning the source and its resolution
    return video_input, video_height, video_width

#This method recognise if there's a change in the scene and exits, otherwise it loops indefinitely
def motion_recognition():

        #Definition of a static background
        static_back = None
        
        #Video source
        video_input, video_height, video_width = video_init()

        #Until the exit condition inside this block is verified, it loops indefinitely
        while True:
            
            #Gets the frame of the video source
            check, image = video_input.read()


            #Switching the color space to Grayscale to ease of use 
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #Using a Gaussian Blur to even more improve ease of use
            blurred_gray = cv2.GaussianBlur( gray_image , (21, 21), 0)

            #This "if" statement has its condition verified only if we are looking at the first frame of the scene
            if static_back is None:
                #Sets the static background to the first frame of the scene, then exit this block
                static_back = blurred_gray 
                continue

            #Gets the absolute difference between the static background and the current analysed frame
            frame_difference = cv2.absdiff(numpy.array(static_back), blurred_gray)

            #Thresholds the frame in order to recognise foreground and background, then appies morphological operations in order to show the foreground as bigger
            threshold_frame = cv2.dilate(cv2.threshold(frame_difference, 30, 255, cv2.THRESH_BINARY)[1] , None, iterations = 2)

            #Finds the countours of the foreground
            contours,_ = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            #For each countour
            for contour in contours:
                #The area is checked and if it is not so relevant (the area is less than 10000), the next area is checked
                if cv2.contourArea(contour) < 10000:
                    continue
                return 1 #If an area with relevant area is found a motion is detected

#STILL NOT PROPERLY WORKING
#This method recognise if there's no change in the scene for a fixed number of frames and exits, otherwise it loops indefinitely
def idle_recognition():

        #Definition of a static background
        static_back = None

        #Variable that counts how many consecutive idle frames are detected
        idle_frame_check = 0

        #Gets the video source and its resolution
        video_input, video_height, video_width = video_init()

        #Gets a black image of the same resolution of the video stream and its area
        black_img = numpy.zeros([video_height , video_width], numpy.uint8)
        black_img_area = video_height * video_width

        #Until 10 consecutive idling frames are found, it keeps looping
        while idle_frame_check < 10:
            
            #Gets the frame of the video source
            check, image = video_input.read()

            #Switching the color space to Grayscale to ease of use 
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #Using a Gaussian Blur to even more improve ease of use
            blurred_gray = cv2.GaussianBlur( gray_image , (21, 21), 0)

            #This "if" statement has its condition verified only if we are looking at the first frame of the scene
            if static_back is None:
                #Sets the static background to the first frame of the scene, then exit this block
                static_back = blurred_gray
                continue

            #Gets the absolute difference between the static background and the current analysed frame
            frame_difference = cv2.absdiff(numpy.array(static_back), blurred_gray)

            #Thresholds the frame in order to recognise foreground and background, then appies morphological operations in order to show the foreground as bigger
            threshold_frame = cv2.dilate(cv2.threshold(frame_difference, 30, 255, cv2.THRESH_BINARY)[1] , None, iterations = 2)
            

            #---------------------------------------------------------------------------------
            #This is the part of code that does not work

            #Calculates the norm distance between the two images
            norm =  cv2.norm(threshold_frame, black_img, cv2.NORM_L2)
            #Checks how similar the two images are
            similarity = 1 - norm/ black_img_area

            #If the two images are equal...
            if similarity == 1.0:
                 #... increment the number of idling frame analysed
                idle_frame_check = idle_frame_check + 1
            else:
                #If not, resets the counter to zero
                idle_frame_check = 0
        
        return 1
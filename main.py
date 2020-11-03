from videocaptureasync import VideoCaptureAsync
from background import change_bg
import numpy as np
from bot import ScenarioParser
import threading
import speech_recognition as sr
import time
import cv2



cam = VideoCaptureAsync(3)

cam.start()

cv2.namedWindow("preview")

bg_path_lock = threading.Lock()
bg_path = ""

def cam_thread():
    while True:
        key = cv2.waitKey(1)

        ret, frame = cam.read()
        stream_img_size = frame.shape[1], frame.shape[0]
        # print(type(frame))
        if frame is not None:   
            # print(type(frame))
            with bg_path_lock:
                cv2.imshow("preview", np.array(change_bg(frame, bg_path)))

        # print(stream_img_size)

        if key == 27: # ESC
            break

# t1 = threading.Thread(target=cam_thread)
# t1.start()



def my_callback(recognizer, audio):
    text = ''
    try:
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google could not understand audio")
    except sr.RequestError as e:
        print("Google error; {0}".format(e))
    return text


def my_listen_in_background(recognizer,
                            source,
                            text_parser,
                            phrase_time_limit=None,
                            # listen for this time, then check again if the stop function has been called
                            need_print_text = True,  # if the recognized text should be printed to stdout
                            file_name=None):
    # this function open a new thread for listening in background
    # it works without any intervention and store the corresponding NLP results into the text parser.
    running = [True]

    def threaded_listen():
        fw = None
        if file_name is not None:
            fw = open(file_name, 'w')
        with source as s:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            if need_print_text:
                print('\nSPEAK NOW\n')
            while running[0]:
                try:
                    audio = recognizer.listen(s, timeout=None, phrase_time_limit=phrase_time_limit)
                except WaitTimeoutError:
                    pass  # listening timed out, just try again
                else:
                    if running[0]:
                        text = my_callback(recognizer, audio)
                        text_parser.parse(text)
                        if need_print_text:
                            print("TEXT IS: ", text)
                        if fw is not None:
                            fw.write(text + '\n')
        if fw is not None:
            fw.close()

    def stopper(wait_for_stop=True):
        running[0] = False
        if wait_for_stop:
            listener_thread.join()

    listener_thread = threading.Thread(target=threaded_listen)
    listener_thread.daemon = True
    listener_thread.start()
    return stopper



def voice_thread():
    sp = ScenarioParser()
    sp.add_scenario('lecture', ['homework', 'assignment', 'assessment', 'lecture', 'teaching' 'assistant', 'student', 'group', 'team', 'overview'])
    sp.add_scenario('meeting', ['meeting', 'agenda', 'actions', 'item', 'work', 'proposal', 'project'])
    sp.add_scenario('birthday', ['birthday'])
    sp.add_scenario('happy', ['happy'])

    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
    r = sr.Recognizer()
    m = sr.Microphone()

    # transcribe_file = path.join(path.dirname(path.realpath(__file__)), 'temp.txt')
    stop_listening = my_listen_in_background(r, m, sp, phrase_time_limit=3)

    # do some computations
    pre_scenario_name = ''
    img = None
    while True:
        if sp.scenario_name and sp.scenario_name != pre_scenario_name:
            if img:
                img.close()
            image_file = './images/' + sp.scenario_name + '.png'
            try:
                global bg_path
                with bg_path_lock:
                    bg_path = image_file
            except IOError:
                print ("IO processing.")
            else:
                pre_scenario_name = sp.scenario_name

    # calling this function requests that the background listener stop listening
    # it's unreachable in this example but should be called sometimes
    stop_listening(wait_for_stop=False)


t2 = threading.Thread(target=voice_thread)
t2.start()
# t1.join()


cam_thread()
# t2.join()
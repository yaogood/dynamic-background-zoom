import speech_recognition as sr
import threading
import re
from PIL import Image



class WaitTimeoutError(Exception):
    pass


class ScenarioParser:
    # Used to handle easy text and check if there are matched words in the setences.
    def __init__(self):
        # dic, the stored scenarios and corresponding words
        # scenario_name, is current detected scenario name
        self.dic = {}
        self.scenario_name = None

    def add_scenario(self, name, word_list):
        # used to add new scenarios to the parser
        for word in word_list:
            self.dic[word] = name

    def parse(self, sentence):
        # parse the text and give the scenarios, if there is no corresponding scenario of the text then return False
        word_list = self.remove_punctuation(sentence)
        word_list = self.trim_stemming(word_list)
        res = self.classifier(word_list)
        if res:
            self.scenario_name = res

    def classifier(self, word_list):
        for word in word_list:
            if word in self.dic.keys():
                return self.dic[word]
        return False

    @staticmethod
    def remove_punctuation(sentence):
        # removing capitalization
        return re.split(r'[;,!\.\?\s]+\s*', sentence.lower())

    @staticmethod
    def trim_stemming(word_list):
        # trim useless words' endings
        result = []
        for i in range(len(word_list)):
            word = word_list[i]
            if word.endswith("sses"):
                result.append(word[:-2])
            elif word.endswith("ing"):
                result.append(word[:-3])
            elif word.endswith("ies"):
                result.append(word[:-2])
            elif word.endswith("ss"):
                result.append(word[:-2])
            elif word.endswith("ment"):
                result.append(word[:-4])
            elif word.endswith("s"):
                result.append(word[:-1])
            else:
                result.append(word)
        return result


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
            r.adjust_for_ambient_noise(source, duration=1)
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


if __name__ == "__main__":
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
                img = Image.open(image_file)
                img.show()
            except IOError:
                print ("IO processing.")
            else:
                pre_scenario_name = sp.scenario_name

    # calling this function requests that the background listener stop listening
    # it's unreachable in this example but should be called sometimes
    stop_listening(wait_for_stop=False)

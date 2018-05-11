import copy

import config
import random as r


class Object:
    def __init__(self, name, question, path, is_loaded=False, data=None):
        self.name = name
        self.question = question  # вопрос например: найди столицу у...
        self.path = path
        self.is_loaded = is_loaded
        self.data = data  # варианты ответов например: ["-бег-", "-бегем-", "-бегемот-"]


def get_objects(file):
    objects = []
    conf = config.Read(file)
    data = conf.getVars('data')

    for i in range(len(data)):
        obj = Object(data[i]["name"], data[i]["question"], data[i]["path"])
        objects.append(obj)

    return objects


def get_object(objects, name):
    for object in objects:
        if object.name == name:
            return object


def get_question(obj):
    if obj.is_loaded == False:
        obj.data = copy.deepcopy(config.Read(obj.path).getDict())
        obj.is_loaded = True

    questions = copy.deepcopy(obj.data)

    keys = r.choice(list(questions.keys()))
    answers = questions[keys]
    true_answer = answers[len(answers) - 1]
    r.shuffle(answers)
    return [true_answer, answers, keys]

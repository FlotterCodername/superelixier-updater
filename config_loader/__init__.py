import json
import os.path
from types import NoneType
from typing import Dict, List, Union
from urllib.parse import urlparse

DICT_OPT = (dict, type(None))
INT_OPT = (int, type(None))
LIST_OPT = (list, type(None))
LIST_STR_OPT = (list, str, type(None))
STR_OPT = (str, type(None))


class Matcher:
    def match(self, filename, parent, arg):
        pass


class Choices(Matcher):
    def __init__(self, *args):
        self.__choices = tuple((arg for arg in args))

    def match(self, filename, parent, arg):
        if arg in self.__choices:
            return True
        else:
            if arg is None:
                print("%s: Missing value at %s. Choices: %s" % (filename, parent, self.__choices))
            else:
                print("%s: Incorrect value '%s' at %s. Choices: %s" % (filename, arg, parent, self.__choices))
            return False


class Types(Matcher):
    def __init__(self, *args):
        self.__types = tuple((arg for arg in args))

    def match(self, filename, parent, arg):
        if isinstance(arg, self.__types):
            print('%s: Correct type at %s.' % (filename, parent))
            return True
        else:
            t_repr = ', '.join([str(t) for t in self.__types if t is not NoneType])
            if NoneType in self.__types:
                t_repr += " (optional element)"
            print('%s: Incorrect type at %s. Choices: %s' % (filename, parent, t_repr))
            return False


class Regex(Matcher):
    def __init__(self, *args, optional=False):
        self.__groups = (arg for arg in args)
        self.__optional = optional

    def match(self, filename, parent, arg):
        if arg is None and self.__optional:
            return True
        elif arg is None:
            return False
        for group in self.__groups:
            if group != '(.*)':
                if f'(?P<{group}>' not in arg:
                    return False
            else:
                if group not in arg:
                    return False
        return True


class LocalDir(Matcher):

    def match(self, filename, parent, arg):
        if os.path.exists(arg):
            if os.path.isdir(arg):
                return True
            else:
                print('%s: Incorrect path at %s. Path is a file: %s' % (filename, parent, arg))
                return False
        else:
            return True


class Url(Matcher):

    def match(self, filename, parent, arg):
        try:
            return urlparse(arg).scheme and urlparse(arg).netloc
        except ValueError:
            return False


CFG_AUTH = {
    "appveyor_token": Types(STR_OPT),
    "github_token": Types(STR_OPT)
}

LOCAL = {
    LocalDir(): Types(LIST_STR_OPT),
}

DEFINITION = {
    "info": {
        "gist": Types(STR_OPT),
        "category": Types(LIST_STR_OPT),
    },
    "name": Types(str),
    "url": Url(),
    "version_scheme": {
        "is_type": Choices('id', 'integer', 'tuple', 'appveyor', 'github'),
        "spec": Types(INT_OPT),
        "version_re": Regex('.*?', optional=True)
    },
    "blob_permalink": Types(STR_OPT),
    "blob_re": Regex('ver', 'url'),
    "blob_unwanted": Types(LIST_STR_OPT),
    "appdatas": Types(LIST_STR_OPT),
    "repo": Choices('appveyor', 'github', 'html')
}


def validate(obj: Union[List, Dict], model: Union[Dict, Matcher], filename: str, parent=None, recursions=-1):
    recursions += 1
    if recursions > 10:
        raise ValueError('Too many recursions.')
    if parent is None:
        parent = ''
    if not isinstance(model, Matcher):
        # Structure
        if type(obj) != type(model):
            print('%s: Incorrect structure at %s: Got %s, received %s' % (filename, parent, type(obj), type(model)))
            return False
        if isinstance(model, dict):
            for key in obj:
                if key not in model:
                    print('%s: Unexpected key at %s: %s' % (filename, parent, key))
            bools = []
            for key in model:
                if isinstance(key, Matcher):
                    bools += [key.match(filename=filename, parent=parent, arg=obj_key) for obj_key in obj]
                else:
                    if key not in obj:
                        obj[key] = None
                    bools.append(validate(obj[key], model[key], filename=filename, parent=parent + '.' + key, recursions=recursions))
            return all(bools)
    else:
        return model.match(filename=filename, parent=parent, arg=obj)


with open('C:\\Users\\fabia\\PycharmProjects\\superelixier-updater\\definitions-wip\\winscp.json', 'r') as fd:
    cfg = json.load(fd)
print(validate(cfg, DEFINITION, 'winscp.json'))

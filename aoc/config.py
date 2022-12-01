from configparser import ConfigParser


def read_config(path):
    parser = ConfigParser()
    parser.read(path)
    return parser

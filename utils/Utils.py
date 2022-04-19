# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import logging
import re
import subprocess
import os
import chardet
import yaml


def run_shell_command(command):
    """
    run command and return output or error message
    :param command:
    :return:  run command result
    """
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output = p.stdout.read()
        error = p.stderr.read()
        encoding = chardet.detect(output if output else error)['encoding']
        data = str(output if output else error, encoding)
        return re.sub(r'[\n\r]', ' ', data)
    except Exception as e:
        logging.error(e)
        return ''


def run_shell_with_callback(command, callback):
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for line in iter(p.stdout.readline, b''):
            callback(str(line, 'utf-8'))
        for line in iter(p.stderr.readline, b''):
            callback(str(line, 'utf-8'))
    except Exception as e:
        logging.error(e)
    finally:
        p.stdout.close()
        p.stderr.close()
        p.wait()


def resize_window(window, width=None, height=None):
    window.update()
    curWidth = width if width else window.winfo_reqwidth()
    curHeight = height if height else window.winfo_reqheight()
    scnWidth, scnHeight = window.maxsize()
    newGeometry = f'{curWidth}x{curHeight}+{(scnWidth - curWidth) // 2}+{(scnHeight - curHeight) // 2}'
    window.geometry(newGeometry)


def conv_time(time):
    second = time % 60
    minute = time // 60 % 60
    hour = time // 3600
    if time // 3600:
        return f'{hour}h {minute}m {second}s'
    elif time // 60:
        return f'{minute}m {second}s'
    else:
        return f'{second}s'


def realpath():
    # When your program is not bundled,
    # the Python variable __file__ refers to the current path of the module it is contained in.
    # When importing a module from a bundled script,
    # the PyInstaller bootloader will set the module’s __file__ attribute to the correct path relative to the bundle folder.
    return Path(__file__).parents[1].resolve()


def load_config():
    name = 'config.yaml'
    if os.path.exists(f'/tmp/{name}'):
        print('load from tmp')
        path = f'/tmp/{name}'
    else:
        print('load from local')
        path = f'{realpath()}/{name}'
    print(f'config path is {path}')
    if not os.path.exists(path):
        return None
    with open(path, mode='rb') as f:
        return yaml.load(f.read(), Loader=yaml.SafeLoader)

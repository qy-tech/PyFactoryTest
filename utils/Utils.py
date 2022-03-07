# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import re

import logging
import chardet


def run_shell_command(command):
    """
    run command and return output or error message
    :param command:
    :return:  run command result
    """
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output = p.stdout.read()
        error = p.stderr.read()
        encoding = chardet.detect(output if output else error)['encoding']
        data = str(output if output else error, encoding)
        return re.sub(r'[\n\r]', ' ', data)
    except Exception as e:
        logging.error(e)
        return ''

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import re
import shutil
import sys
import threading
import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox as msg
from tkinter import ttk
import time
import yaml

from utils import Utils

# set chardet log only show error
logging.getLogger('chardet').setLevel(logging.ERROR)
logging.basicConfig(level=logging.DEBUG)  # , filename="/tmp/FactoryTest.log")


class FactoryTest(tk.Tk):
    """
    Debian 生产测试工具
    """

    def __init__(self):
        super().__init__()

        self.real_path = getattr(
            sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        self.menu = None
        self.autotest_menu = None
        self.test_status_view = None
        self.canvas_frame = None
        self.scrollbar = None
        self.text_frame = None
        self.tasks_frame = None
        self.tasks_canvas = None
        self.task_views = []

        self.all_testcases = []
        self.agingtest = []
        self.selected_testcases = []
        self.test_result = True
        self.result_dicts = {}
        # View的状态
        self.colour_schemes = {
            'default': {'bg': 'lightgrey', 'fg': 'black'},
            'success': {'bg': 'green', 'fg': 'white'},
            'error': {'bg': '#C26860', 'fg': 'white'}
        }

        self.load_config()
        self.init_run_script()

        self.title('FactoryTest')

        self.init_menu()
        self.init_listview()
        self.init_status_view()

        for testcase in self.selected_testcases:
            self.add_testcase(testcase)

        Utils.resize_window(self, 480, 640)

    def load_config(self):
        """
        加载配置文件中的测试项
        """
        # logging.debug('load config file')
        if os.path.exists('/tmp/config.yaml'):
            config_file = '/tmp/config.yaml'
        else:
            config_file = os.path.join(self.real_path, 'config.yaml')
        with open(config_file, 'rb') as f:
            config = yaml.load(f.read(), Loader=yaml.SafeLoader)
        self.all_testcases = config['factorytest']['testcase']
        self.selected_testcases = config['factorytest']['selected']
        self.agingtest = config['agingtest']
        # logging.debug(f'config: {config}')

    def init_menu(self):
        """
        初始化菜单栏
        自动测试和重置测试项
        """
        self.menu = tk.Menu(self, bg='lightgrey', fg='black')
        self.menu.add_command(label='AutoTest', command=self.start_auto_test)
        self.menu.add_command(label='Reset', command=self.reset_test_status)
        self.menu.add_command(label='AgingTest', command=self.run_aging_test)
        self.config(menu=self.menu)

    def init_listview(self):
        self.tasks_canvas = tk.Canvas(self)

        self.tasks_frame = tk.Frame(self.tasks_canvas)
        self.text_frame = tk.Frame(self)

        self.scrollbar = tk.Scrollbar(
            self.tasks_canvas, orient="vertical", command=self.tasks_canvas.yview)

        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.tasks_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_frame = self.tasks_canvas.create_window(
            (0, 0), window=self.tasks_frame, anchor="n")
        self.bind_all("<MouseWheel>", self.mouse_scroll)
        self.bind_all("<Button-4>", self.mouse_scroll)
        self.bind_all("<Button-5>", self.mouse_scroll)
        self.bind("<Configure>", self.on_frame_configure)
        self.tasks_canvas.bind("<Configure>", self.task_width)

    def init_run_script(self):
        if sys.platform.startswith("win"):
            return
        script_dir = os.path.join(self.real_path, 'bin')
        data_dir = os.path.join(self.real_path, 'data')
        if os.path.exists(script_dir) and os.path.isdir(script_dir):
            for script in os.listdir(script_dir):
                src = os.path.join(script_dir, script)
                dist = os.path.join('/tmp/', script)
                shutil.copyfile(src, dist)
                os.system(f'chmod 777 {dist}')

        if os.path.exists(data_dir) and os.path.isdir(data_dir):
            for data in os.listdir(data_dir):
                src = os.path.join(data_dir, data)
                dist = os.path.join('/tmp/', data)
                shutil.copyfile(src, dist)
                os.system(f'chmod 777 {dist}')

    def start_auto_test(self):
        """
        开始自动测试
        """
        self.reset_test_status()

        for index, task in enumerate(self.task_views):
            testcase = next(
                (item for item in self.all_testcases if item["name"] == task.cget('text')), None)
            if 'automatic' == testcase['type']:
                self.after(3000 * index, self.run_testcase_command, task)

    def reset_test_status(self):
        """
        重置测试状态
        """
        logging.debug('reset_test_status')

        self.test_result = True
        self.result_dicts.clear()

        for task in self.task_views:
            task.config(self.colour_schemes['default'])
        self.test_status_view.config(self.colour_schemes['default'])
        self.test_status_view.config(text='All Test Result')

    def init_status_view(self):
        """
        初始化测试结果
        """
        self.test_status_view = tk.Label(
            self.text_frame, text='All Test Result', padx=10, pady=10)
        self.test_status_view.config(self.colour_schemes['default'])
        self.test_status_view.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_frame.pack(side=tk.BOTTOM, fill=tk.X)

    def add_testcase(self, testcase):
        """
        从配置文件中加载测试用例
        """
        new_case_view = tk.Label(
            self.tasks_frame, text=testcase, padx=10, pady=10)
        new_case_view.pack(side=tk.TOP, fill=tk.X)
        new_case_view.config(self.colour_schemes['default'])
        new_case_view.bind('<Button-1>', self.on_testcase_click)
        separator = ttk.Separator(self.tasks_frame, orient='horizontal')
        separator.pack(side=tk.TOP, fill=tk.X)
        self.task_views.append(new_case_view)

    def on_testcase_click(self, event=None):
        task_view = event.widget
        self.run_testcase_command(task_view)

    def run_testcase_command(self, task):
        task_name = task.cget('text')
        # testcase = list(filter(lambda item: item['name'] == task_name, self.config['testcase']))
        testcase = next(
            (item for item in self.all_testcases if item["name"] == task_name), None)
        logging.debug(f'run test case command {testcase}')
        result = Utils.run_shell_command(testcase['command'])
        logging.debug(f'test {task_name} result {result}')
        # 判断是否测试成功，部分需要手动判断测试结果
        if 'manual' == testcase['type']:
            logging.debug('please checkout this item manual')
            success = msg.askyesno('TestCase success?', f'Is {task_name} OK？')
        else:
            # success = testcase['result'] in result
            pattern = re.compile(testcase['result'], re.S)
            find_result = re.findall(pattern, result)
            logging.debug(f'test result {find_result}')
            success = len(find_result) > 0
        self.result_dicts[task_name] = success
        self.test_result = all(self.result_dicts.values())
        logging.debug(
            f'{testcase["command"]} result is {result} success {success} all test success {self.test_result}')

        task.config(self.colour_schemes['success']
                    if success else self.colour_schemes['error'])
        self.test_status_view.config(
            self.colour_schemes['success'] if self.test_result else self.colour_schemes['error'])
        self.test_status_view.config(
            text='Success' if self.test_result else 'Error')

    def on_frame_configure(self, event=None):
        self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))

    def task_width(self, event):
        canvas_width = event.width
        self.tasks_canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def mouse_scroll(self, event):
        if event.delta:
            self.tasks_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 5:
                move = 1
            else:
                move = -1

            self.tasks_canvas.yview_scroll(move, "units")

    def run_aging_test(self):
        AgingTestWindow(self, self.agingtest)


class AgingTestWindow(tk.Toplevel):
    """
    CPU老化                   cpu 温度 cpu频率 CPU型号 CPU核心数 CPU使用率
    GPU老化                   播放GPU动画
    VPU老化                   播放视频
    memory老化                压力测试
    """

    def __init__(self, master, agingtest):
        super().__init__(master)
        self.title("AgingTest")
        self.testcase = agingtest['testcase']
        self.time = agingtest['time']
        if not self.time:
            self.time = 4
        self.grids = {}
        self.test_methods = {
            "cpu": self.cpu_test,
            "gpu": self.gpu_test,
            "vpu": self.vpu_test,
            "memory": self.memory_test,
        }
        self.threads = []

        self.add_testcases()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        Utils.resize_window(self)
        # 老化4个小时后自动结束
        self.after(self.time*60*60*1000, self.on_closing)

    def add_testcases(self):
        try:
            for index, testcase in enumerate(self.testcase):
                if testcase['enable']:
                    text = Text(self, width=44, height=14, background="#CCC")
                    text.grid(row=index // 2, column=index % 2, padx=2, pady=2)
                    self.grids[testcase['id']] = text

                    self.update_test_info(
                        testcase['id'], f'{testcase["name"]}\n')

                    self.test_methods[testcase['name']](testcase)
        except Exception as e:
            logging.error(f'error run case {e}')

        for i in range(len(self.testcase)//2):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)

    def on_closing(self):
        for thread in self.threads:
            thread.force_quit = True
            thread.join()

        self.after(10, self.destroy)

    def start_test_thread(self, testcase):
        if not testcase['command']:
            return
        thread = AgingTestThread(self, testcase)
        self.threads.append(thread)
        thread.start()

    def cpu_test(self, testcase):
        logging.debug(f'cpu test {testcase}')
        self.start_test_thread(testcase)

    def memory_test(self, testcase):
        logging.debug(f'memory test {testcase}')
        self.start_test_thread(testcase)

    def vpu_test(self, testcase):
        logging.debug(f'vpu test {testcase}')
        self.start_test_thread(testcase)

    def gpu_test(self, testcase):
        logging.debug(f'gpu test {testcase}')
        self.start_test_thread(testcase)

    def update_test_info(self, id, text):
        self.grids[id].insert(tk.END, text)
        self.grids[id].see(tk.END)


class AgingTestThread(threading.Thread):
    def __init__(self, master, testcase):
        super().__init__()
        self.force_quit = False
        self.master = master
        self.testcase = testcase
        self.last_time = time.time()

    def run(self):
        while True:
            if self.force_quit:
                return
            self.main_loop()

    def format_output(self, message):
        try:
            if self.testcase['name'] == 'cpu':
                temp = message.split(' ')
                time_format = Utils.conv_time(int(time.time() - self.last_time))
                if len(temp) > 1:
                    message = f'{time_format} CPU temp: {int(temp[0])//1000}℃, CPU freq {int(temp[1])//1000}M\n'
        except Exception as e:
            logging.error(e)
        return message

    def callback(self, message):
        self.master.update_test_info(
            self.testcase['id'],
            self.format_output(message)
        )

    def main_loop(self):
        if self.testcase['command'] and not self.force_quit:
            cmd = self.testcase['command']
            Utils.run_shell_with_callback(cmd, self.callback)
        time.sleep(3)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--agingtest',
                        action='store_true', help="run aging test")
    args = parser.parse_args()

    factory_test = FactoryTest()

    if args.agingtest:
        factory_test.run_aging_test()

    factory_test.mainloop()


if __name__ == '__main__':
    main()

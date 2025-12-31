#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Display detailed system information in graph format.
It provides a display of CPU, memory, disk utilization, temperature, and network traffic.

Needs psutil (+ dependencies) installed::

  $ sudo apt-get install python-dev
  $ sudo -H pip install psutil
"""

import time
from pathlib import Path
from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont
import psutil
import subprocess as sp


def get_temp():
    temp = float(sp.getoutput("vcgencmd measure_temp").split("=")[1].split("'")[0])
    return temp


def get_cpu():
    return psutil.cpu_percent()

def get_mem():
    return psutil.virtual_memory().percent

def get_disk_usage():
    usage = psutil.disk_usage("/")
    return usage.used / usage.total * 100

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return f"{n}B"

def network(iface):
    try:
        stat = psutil.net_io_counters(pernic=True)[iface]
        return "Tx%s, Rx%s" % \
               (bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))
    except KeyError:
        return f"{iface}: Not found"

def format_percent(percent):
    return "%5.1f" % (percent)

def draw_text(draw, margin_x, line_num, text):
    y = (margin_y_line[line_num] + scroll_offset) % device.height
    draw.text((margin_x, y), text, font=font_default, fill="white")
    if y + font_size >= device.height:
        draw.text((margin_x, y - device.height), text, font=font_default, fill="white")

def draw_histogram(draw, line_num, data_history):
    y = (margin_y_line[line_num] + bar_margin_top + scroll_offset) % device.height

    def _draw(top_y):
        bottom_y = top_y + bar_height
        draw.rectangle((margin_x_bar, top_y, margin_x_bar + bar_width, bottom_y), outline="white")
        for i, val in enumerate(data_history):
            height = int(val / 100.0 * bar_height)
            x = margin_x_bar + i
            if height > 0:
                draw.line((x, bottom_y, x, bottom_y - height), fill="white")

    _draw(y)
    if y + bar_height >= device.height:
        _draw(y - device.height)

def stats(device):
    global cpu_history, mem_history
    with canvas(device) as draw:
        temp = get_temp()
        draw_text(draw, 0, 0, "Temp")
        draw_text(draw, margin_x_figure, 0, "%s'C" % (format_percent(temp)))

        cpu = get_cpu()
        cpu_history.append(cpu)
        if len(cpu_history) > bar_width:
            cpu_history.pop(0)

        draw_text(draw, 0, 1, "CPU")
        draw_text(draw, margin_x_figure, 1, "%s %%" % (format_percent(cpu)))
        draw_histogram(draw, 1, cpu_history)

        mem = get_mem()
        mem_history.append(mem)
        if len(mem_history) > bar_width:
            mem_history.pop(0)

        draw_text(draw, 0, 2, "Mem")
        draw_text(draw, margin_x_figure, 2, "%s %%" % (format_percent(mem)))
        draw_histogram(draw, 2, mem_history)

        disk = get_disk_usage()
        draw_text(draw, 0, 3, "Disk")
        draw_text(draw, margin_x_figure, 3, "%s %%" % (format_percent(disk)))

        draw_text(draw, 0, 4, network('eth0'))


font_size = 12
font_size_full = 10
margin_y_line = [0, 13, 25, 38, 51]
margin_x_figure = 78
margin_x_bar = 31
bar_width = 52
bar_width_full = 95
bar_height = 8
bar_margin_top = 3

cpu_history = []
mem_history = []
scroll_offset = 0

device = get_device()
font_default = ImageFont.truetype(str(Path(__file__).resolve().parent.joinpath("fonts", "DejaVuSansMono.ttf")), font_size)
font_full = ImageFont.truetype(str(Path(__file__).resolve().parent.joinpath("fonts", "DejaVuSansMono.ttf")), font_size_full)


while True:
    stats(device)
    time.sleep(0.5)
    scroll_offset = (scroll_offset + 1) % device.height

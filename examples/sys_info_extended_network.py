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
import random
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

last_net_stats = {}

def network(iface):
    global last_net_stats
    try:
        stat = psutil.net_io_counters(pernic=True)[iface]
        now = time.time()
        tx = stat.bytes_sent
        rx = stat.bytes_recv

        tx_rate = 0
        rx_rate = 0
        if iface in last_net_stats:
            dt = now - last_net_stats[iface]['time']
            if dt > 0:
                tx_rate = (tx - last_net_stats[iface]['tx']) / dt
                rx_rate = (rx - last_net_stats[iface]['rx']) / dt

        last_net_stats[iface] = {'tx': tx, 'rx': rx, 'time': now}

        return "Tx%s/s, Rx%s/s" % \
               (bytes2human(int(tx_rate)), bytes2human(int(rx_rate)))
    except KeyError:
        return f"{iface}: Not found"

def format_percent(percent):
    return "%5.1f" % (percent)

def draw_text(draw, margin_x, line_num, text):
    draw.text((margin_x + shift_x, margin_y_line[line_num] + shift_y), text, font=font_default, fill="white")

def draw_histogram(draw, line_num, data_history):
    top_y = margin_y_line[line_num] + bar_margin_top + shift_y
    bottom_y = top_y + bar_height
    x_start = margin_x_bar + shift_x
    draw.rectangle((x_start, top_y, x_start + bar_width, bottom_y), outline="white")
    for i, val in enumerate(data_history):
        height = int(val / 100.0 * bar_height)
        x = x_start + i
        if height > 0:
            draw.line((x, bottom_y, x, bottom_y - height), fill="white")

def stats(device):
    global cpu_history, mem_history
    with canvas(device) as draw:
        # Item 0: Temp
        line = (0 + row_offset) % 5
        temp = get_temp()
        draw_text(draw, 0, line, "Temp")
        draw_text(draw, margin_x_figure, line, "%s'C" % (format_percent(temp)))

        # Item 1: CPU
        line = (1 + row_offset) % 5
        cpu = get_cpu()
        cpu_history.append(cpu)
        if len(cpu_history) > bar_width:
            cpu_history.pop(0)

        draw_text(draw, 0, line, "CPU")
        draw_text(draw, margin_x_figure, line, "%s %%" % (format_percent(cpu)))
        draw_histogram(draw, line, cpu_history)

        # Item 2: Mem
        line = (2 + row_offset) % 5
        mem = get_mem()
        mem_history.append(mem)
        if len(mem_history) > bar_width:
            mem_history.pop(0)

        draw_text(draw, 0, line, "Mem")
        draw_text(draw, margin_x_figure, line, "%s %%" % (format_percent(mem)))
        draw_histogram(draw, line, mem_history)

        # Item 3: Disk
        line = (3 + row_offset) % 5
        disk = get_disk_usage()
        draw_text(draw, 0, line, "Disk")
        draw_text(draw, margin_x_figure, line, "%s %%" % (format_percent(disk)))

        # Item 4: Network
        line = (4 + row_offset) % 5
        draw_text(draw, 0, line, network('eth0'))


font_size = 12
font_size_full = 10
margin_y_line = [0, 13, 25, 38, 51]
margin_x_figure = 78
margin_x_bar = 31
bar_width = 52
bar_width_full = 95
bar_height = 8
bar_margin_top = 3
line_height = 13

cpu_history = []
mem_history = []
row_offset = 0
shift_x = 0
shift_y = 0

device = get_device()
device.contrast(25)
font_default = ImageFont.truetype(str(Path(__file__).resolve().parent.joinpath("fonts", "DejaVuSansMono.ttf")), font_size)
font_full = ImageFont.truetype(str(Path(__file__).resolve().parent.joinpath("fonts", "DejaVuSansMono.ttf")), font_size_full)


while True:
    shift_x = random.randint(0, 2)
    shift_y = random.randint(0, 2)
    stats(device)
    time.sleep(5.0)
    row_offset = (row_offset + 1) % 5

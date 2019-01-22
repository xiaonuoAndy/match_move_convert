#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'yangzhuo'

import re


class StandardData(object):
    def __init__(self):

        self.name = ''
        self.index = None
        self.key_start = None
        self.key_end = None
        self.frames = []
        self.values = []

    def __iter__(self):
        for index, f in enumerate(self.frames):
            yield f, self.values[index]


class BaseTracker(object):

    _track_type = None
    _track_data = None

    def load(self, *args):
        '''
        必须重载，用来读取公共格式的文件
        :param args: path , width , height
        :return: 读取后的数据
        '''
        raise NotImplementedError()

    def save(self, *args):
        '''
        必须重载，以各个软件内特有的格式导出，存储为txt文件
        :param args: path , width , height
        :return:
        '''
        raise NotImplementedError()

    def eval(self, time, interop='cubic'):
        '''
        向前或者向后延长X帧数
        :param time: 帧数长度
        :param interop:
        :return:
        '''
        pass


class PFTrackTracker(BaseTracker):
    def __init__(self):
        self.data = []

    def load(self, *args):
        '''
        pftrack 文件数据格式 frame, xpos, ypos, similarity(相似点，结算时会用到)
        坐标:左下(0, 0), 右上(1920, 1080)
        :param path:
        :return:
        '''
        track_data = None
        for index, line in enumerate(open(args[0], 'r')):
            line_info = [r.strip() for r in line.split(' ')]
            if re.match(re.compile(r'"(.*)"'), line_info[0]):
                track_data = StandardData()
                track_data.name = re.findall(re.compile(r'"(.*)"'), line)[0]
                track_data.index = index
                self.data.append(track_data)
                continue
            if not track_data:
                continue
            if index - track_data.index == 1:
                track_data.key_start = line_info[0]
                continue
            if index - track_data.index == 2:
                track_data.key_end = line_info[0]
                continue
            if index - track_data.index > 2:
                if line.startswith('#') or len(line_info) < 3:
                    continue
                track_data.frames.append(line_info[0])
                print line_info
                track_data.values.append([float(line_info[1]),
                                          float(line_info[2]),
                                          float(line_info[3])])
        return self.data

    def save(self, *args):
        with open(args[0], 'w') as wf:
            for tracker in self.data:
                wf.write('\n"{}"\n'.format(tracker.name))
                wf.write('{}\n'.format(tracker.key_start))
                wf.write('{}\n'.format(tracker.key_end))
                for frame, value in tracker:
                    wf.write('{frame} {x_pos} {y_pos} {similarity}\n'.format(
                              frame=frame,
                              x_pos=value[0],
                              y_pos=value[1],
                              similarity=value[2]))


class SynthEyesTracker(BaseTracker):
    def __init__(self):
        self.data = []

    def load(self, *args):
        '''
        syntheyes 文件数据格式 tracker name,  frame, xpos, ypos, key_frame(15代表是关键帧， 7代表不是关键帧)
        坐标: 左下(-1, 1), 右上(1, -1)
        :param path:
        :param w: with
        :param h: height
        :return:
        '''
        path, w, h = args[0], args[1], args[2]
        tracker_name_list = []
        for index, line in enumerate(open(path, 'r')):
            line_info = [r.strip() for r in line.split(' ')]
            if len(line_info) < 3:
                continue
            tracker_name = line_info[0]
            track_in_list = tracker_name in tracker_name_list

            tracker_name_list.append(tracker_name) if not track_in_list else None
            track_data = StandardData() if not track_in_list else self.data[-1]
            self.data.append(track_data) if not track_in_list else None
            track_data.name = tracker_name
            track_data.index = index
            track_data.key_start = 1
            track_data.key_end = len(track_data.frames) + 1
            track_data.frames.append(line_info[1])
            x, y = self.remap_xy(float(line_info[2]), float(line_info[3]), w, h)
            track_data.values.append([x, y, 1])

        return self.data

    def save(self, *args):
        path, w, h = args[0], args[1], args[2]
        with open(path, 'w') as wf:
            for tracker in self.data:
                for frame, value in tracker:
                    x, y = self.remap_uv(float(value[0]), float(value[1]), w, h)
                    wf.write('{tracker_name} {frame} {x_pos} {y_pos} {is_key_frame}\n'.format(
                              tracker_name=tracker.name,
                              frame=frame,
                              x_pos=x,
                              y_pos=y,
                              is_key_frame=7))

    @staticmethod
    def remap_xy(u, v, w, h):
        x = w*u/2 + w/2
        y = -h*v/2 + h/2
        return x, y

    @staticmethod
    def remap_uv(x, y, w, h):
        u = (2*x-w)/w
        v = (h-2*y)/h
        return u, v


class ThreeDeTracker(BaseTracker):
    def __init__(self):
        self.data = []

    def load(self, *args):
        '''
        3DE文件数据格式: frame, xpos, ypos
        坐标:左下(0, 0), 右上(1920, 1080)
        :param path:
        :return:
        '''
        flag_list = ['name', 'key_start', 'key_end']
        flag = 0
        track_data = StandardData()
        self.data.append(track_data)
        for index, line in enumerate(open(args[0], 'r')):
            line_info = [r.strip() for r in line.split(' ')]
            if index == 0:
                continue
            if len(line_info) == 1 and flag > 2:
                track_data = StandardData()
                flag = 0
                self.data.append(track_data)
            if len(line_info) == 1:
                value = 'Tracker{}'.format(
                    line_info[0]) if flag == 0 else line_info[0]
                value = 1 if flag == 1 else value
                setattr(track_data, flag_list[flag], value)
            else:
                track_data.frames.append(line_info[0])
                # 原数据小数点后有15位, float 只会精确到小数点后12位， 所以会导致数据有一些小偏差
                track_data.values.append([float(line_info[1]),
                                          float(line_info[2]),
                                          1])
            flag += 1

        return self.data

    def save(self, *args):
        with open(args[0], 'w') as wf:
            wf.write('{}\n'.format(len(self.data)))
            for tracker in self.data:
                track_name = re.findall(
                    re.compile(r'Tracker(\d*)'), tracker.name)[0]
                wf.write('{}\n'.format(track_name))
                wf.write('0' + '\n')
                wf.write('{}\n'.format(len(tracker.frames)))
                for frame, value in tracker:
                    wf.write('{frame} {x_pos} {y_pos}\n'.format(
                              frame=frame,
                              x_pos=value[0],
                              y_pos=value[1]))

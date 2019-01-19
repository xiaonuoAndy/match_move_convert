#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'yangzhuo'

import os

DEFAULT_USER_PATH = r'{}/{}'.format(os.path.expanduser('~'), 'Documents')

SOFTWARE_LIST = ('3DE', 'PFTrack', 'SynthEyes')

RESOLUTION_LIST = (	" 640 x 480", " 720 x 486", " 720 x 576",
                    " 768 x 576", "1024 x 576", "1280 x 720", "1920 x 1080",
                    "2048 x 1152", "2048 x 1556", "2048 x 2048", "4096 x 3112")

SOFTWARE_BUTTON_DATA = [{'data': 'PFTrackTracker', 'name': u'PFTrack', 'icon': ''},
                        {'data': 'SynthEyesTracker', 'name': u'SysthEyes', 'icon': ''},
                        {'data': 'ThreeDeTracker', 'name': u'3DE', 'icon': ''}]


#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Instance Notifier
# Copyright (C) 2010-2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.


import argparse
import logging
import os
import sys
import thread


LOG_FILE = "/var/log/instance-notifier/instance-notifier.log"


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--debug", "-d", default=False,
                            action="store_true", help="debug")
    args = arg_parser.parse_args()

    from instance_notifier.poller import local_settings
    handler = logging.FileHandler(LOG_FILE)
    LOG = logging.getLogger()
    LOG.addHandler(handler)
    log_level = (logging.DEBUG if args.debug
                 else logging.getLevelName(local_settings.LOG_LEVEL))
    if not isinstance(log_level, int):
        log_level = logging.WARNING
    LOG.setLevel(log_level)

    from instance_notifier.poller import poller_thread
    poller_thread()


if __name__ == "__main__":
    main()

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


LOG_LEVEL = "DEBUG"
FPING_POLLING_INTERVAL = 120

HYSTERESES = {
    "DEAD": 180,
    "ALIVE": 180,
    "BUILD": 240,
    "REBUILD": 240,
    "MIGRATING": 600,
    "RESIZE": 600,
    "REVERT_RESIZE": 600,
}

ADMIN_EMAIL = ""

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "altai-test@griddynamics.com"
MAIL_PASSWORD = ""
DEFAULT_MAIL_SENDER = ("robot", MAIL_USERNAME)

KEYSTONE_CONF = {
    "username": "admin",
    "password": "",
    "auth_uri": "http://:5000/v2.0",
    "tenant_name": "systenant",
}

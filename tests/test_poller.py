# -*- coding: utf-8 -*-

# Zabbix Notifier
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


"""
Tests for instance_notifier.poller
"""

import os
import sys
import json
import datetime
import unittest
import stubout

import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tests

# for importing local_settings from project's etc
sys.path.append("%s/etc" %
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instance_notifier import poller


class TestCase(tests.TestCase):

    def test_must_notify(self):
        test_data = self.json_load_from_file("test_poller_must_notify.in.js")
        all_answers = []
        for test_unit in test_data:
            srv_state = {}
            unit_answers = []
            for curr_status, now in test_unit["changes"]:
                unit_answers.append({
                    "notify": poller.must_notify(
                        curr_status, now,
                        srv_state,
                        test_unit["hysteresis"])
                })
            all_answers.append(unit_answers)
        self.json_check_with_file(
            all_answers,
            "test_poller_must_notify.out.js")

    def test_alarm_handler(self):
        from openstackclient_base.nova import fping
        from novaclient.v1_1 import servers
        from keystoneclient.v2_0 import users

        all_mail_lists = []

        def fake_servers_list(*args, **kwargs):
            return [
                servers.Server(
                    poller.openstack_client.compute.servers,
                    {"id": "1", "name": "server 1", "status": "ACTIVE"}),
                servers.Server(
                    poller.openstack_client.compute.servers,
                    {"id": "2", "name": "server 2", "status": "ACTIVE"})
            ]

        def fake_fping_list(*args, **kwargs):
            return [
                fping.Fping(
                    poller.openstack_client.compute.fping,
                    {"id": "1", "project_id": "11", "alive": True}),
                fping.Fping(
                    poller.openstack_client.compute.fping,
                    {"id": "2", "project_id": "22", "alive": False})
            ]

        def fake_users_list(*args, **kwargs):
            tenant_id = kwargs.get("tenant_id", "None")
            return [
                users.User(
                    poller.openstack_client.identity_admin.users,
                    {"id": "id-%s" % tenant_id,
                     "name": "name-%s" % tenant_id,
                     "email": "mail-%s@users.com" % tenant_id})]

        def fake_tenants_list(*args, **kwargs):
            return []

        def fake_send_mails(mail_list):
            for mail in mail_list:
                all_mail_lists.append(mail[1])

        def fake_must_notify(curr_status, now, srv_state, hysteresis):
            return (poller.NOTIFY_ACTIVE
                    if curr_status in ("ALIVE", "DEAD")
                    else poller.NOTIFY_INACTIVE)

        self.stubs.Set(
            poller.openstack_client.compute.servers,
            "list",
            fake_servers_list)
        self.stubs.Set(
            poller.openstack_client.compute.fping,
            "list",
            fake_fping_list)
        self.stubs.Set(
            poller.openstack_client.identity_admin.users,
            "list",
            fake_users_list)
        self.stubs.Set(
            poller.openstack_client.identity_admin.tenants,
            "list",
            fake_tenants_list)
        fake_time = 0
        self.stubs.Set(time, "time", lambda: fake_time)
        self.stubs.Set(
            poller, "TEMPLATE_DIR",
            "%s/etc" % os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))

        self.stubs.Set(poller, "send_mails", fake_send_mails)
        self.stubs.Set(poller, "must_notify", fake_must_notify)

        poller.alarm_handler()
        self.assertEqual(all_mail_lists,
                         [['mail-11@users.com'],
                          ['mail-22@users.com']])
        self.stubs.UnsetAll()

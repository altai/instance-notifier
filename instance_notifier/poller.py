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

import itertools
import json
import logging
import time
import os
import sys

import jinja2
import smtplib
from email.mime.text import MIMEText

from openstackclient_base import client_set


LOG = logging.getLogger(__name__)

SRV_STATE_FILENAME = "/var/lib/instance-notifier/srv_state.json"


local_settings = object()
SETTINGS_DIR = "/etc/instance-notifier"

sys.path.append(SETTINGS_DIR)

try:
    import local_settings
except:
    LOG.exception("cannot load local_settings")
    sys.exit(1)

openstack_client = client_set.ClientSet(**local_settings.KEYSTONE_CONF)


def notify_active_letters(srv_active):
    template_filename = "/etc/instance-notifier/notification_active.txt"
    template = jinja2.Template(open(template_filename, "r").read())
    tenant_list = openstack_client.identity_admin.tenants.list()
    tenant_by_id = dict(((i.id, i) for i in tenant_list))

    for project_id, srv_list in srv_active.iteritems():
        if not srv_list:
            continue
        try:
            tenant_name = tenant_by_id[project_id].name
        except:
            tenant_name = project_id

        try:
            user_list = openstack_client.identity_admin.users.list(
                tenant_id=project_id)
        except:
            recipients = None
        else:
            recipients = [user.email for user in user_list if user.email]
        if not recipients:
            recipients = [local_settings.ADMIN_EMAIL]
        try:
            yield (
                "Instance Notification for Project %s" % tenant_name,
                recipients,
                template.render(
                    tenant_name=tenant_name,
                    srv_alive=[srv for srv in srv_list if srv.alive],
                    srv_dead=[srv for srv in srv_list if not srv.alive]),
            )
        except:
            LOG.exception("unable to prepare an email")


def notify_inactive_letters(srv_inactive):
    if srv_inactive:
        template_filename = "/etc/instance-notifier/notification_inactive.txt"
        template = jinja2.Template(open(template_filename, "r").read())
        try:
            yield (
                "Instance Inactive State Notification",
                [local_settings.ADMIN_EMAIL],
                template.render(
                    srv_build=srv_inactive),
            )
        except:
            LOG.exception("unable to prepare an email")


def send_mails(mail_list):
    host_args = (local_settings.MAIL_SERVER, local_settings.MAIL_PORT)
    if local_settings.MAIL_USE_SSL:
        host = smtplib.SMTP_SSL(*host_args)
    else:
        host = smtplib.SMTP(*host_args)
    if local_settings.MAIL_USE_TLS:
        host.starttls()
    host.login(local_settings.MAIL_USERNAME, local_settings.MAIL_PASSWORD)

    for mail in mail_list:
        subject, recipients, msg_text = mail
        msg = MIMEText(msg_text)
        msg["Subject"] = subject
        msg["From"] = "%s <%s>" % local_settings.DEFAULT_MAIL_SENDER
        msg["To"] = ", ".join(recipients)
        try:
            host.sendmail(local_settings.MAIL_USERNAME,
                          recipients,
                          msg.as_string())
        except:
            LOG.exception("unable to send an email")
    host.quit()


# stored data:
#    - status
#    - at
#    - sent
# VM status can be ALIVE/DEAD (marked as ACTIVE in nova),
#    the others are inactive (BUILD etc)
def alarm_handler():
    LOG.debug("polling nova for new fpings")
    now = time.time()

    try:
        state_list = json.load(open(SRV_STATE_FILENAME, "r"))
    except:
        state_list = {}
    else:
        if not isinstance(state_list, dict):
            state_list = {}

    server_list = openstack_client.compute.servers.list(
        detailed=True, search_opts={"all_tenants": True})
    fping_list = openstack_client.compute.fping.list(all_tenants=True)
    server_by_id = dict(((i.id, i) for i in server_list))
    srv_active = {}
    srv_inactive = []
    for srv in fping_list:
        try:
            srv.name = server_by_id[srv.id].name
            curr_status = server_by_id[srv.id].status
        except:
            continue
        if curr_status == "ACTIVE":
            curr_status = "ALIVE" if srv.alive else "DEAD"
        srv.status = curr_status
        srv_state = state_list.setdefault(srv.id, {})
        prev_status = srv_state.get("status", "BUILD")
        prev_at = srv_state.get("at", now)
        if curr_status != prev_status:
            srv_state["at"] = now
            srv_state["prev_status"] = prev_status
            srv_state["status"] = curr_status
            srv_state["sent"] = False
        if srv_state.get("sent", False):
            continue
        hysteresis = local_settings.HYSTERESES.get(curr_status, -1)
        if now - prev_at < hysteresis or hysteresis < 0:
            continue
        srv_state["sent"] = True
        if curr_status in ("ALIVE", "DEAD"):
            if not (curr_status == "ALIVE" and
                    srv_state.get("prev_status", "BUILD") != "DEAD"):
                srv_active.setdefault(srv.project_id, []).append(srv)
        else:
            srv_inactive.append(srv)

    try:
        send_mails(itertools.chain(notify_active_letters(srv_active),
                                   notify_inactive_letters(srv_inactive)))
    except:
        LOG.exception("cannot send mail")

    try:
        with open(SRV_STATE_FILENAME, "w") as f:
            json.dump(state_list, f)
    except:
        LOG.exception("cannot save server state to %s" % SRV_STATE_FILENAME)


def poller_thread():
    interval = getattr(local_settings, "FPING_POLLING_INTERVAL", 120)
    while True:
        start = time.time()
        alarm_handler()
        to_sleep = interval + start - time.time()
        if to_sleep > 0:
            time.sleep(to_sleep)

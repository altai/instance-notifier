Configuration
=============
* LOG_LEVEL - a string, e.g., "DEBUG"
* FPING_POLLING_INTERVAL - interval for polling nova-fping, in seconds; must be more than its fping_interval
* HYSTERESES - a dictionary of hystereses for different states ("DEAD", "ALIVE", "BUILD" etc.), in seconds. The notification is sent if a servers spends at least `hysteresis` seconds in current state.
* ADMIN_EMAIL - an email of system administrator who receives notifications about, e.g., in BUILD state.
* *MAIL_* - mail settings
* KEYSTONE_CONF - keystone coordinates and credentials


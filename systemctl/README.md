# Systemd Service Setup

This directory contains a systemd unit file to run the `sys_info_extended_network.py` script automatically at boot as a user service.

## Installation

1.  **Create the systemd user directory** (if it doesn't exist):
    ```bash
    mkdir -p ~/.config/systemd/user/
    ```

2.  **Copy the service file**:
    ```bash
    cp luma_sys_info.service ~/.config/systemd/user/
    ```

3.  **Enable and start the service**:
    ```bash
    systemctl --user daemon-reload
    systemctl --user enable --now luma_sys_info.service
    ```

4.  **Enable Linger (Optional)**:
    To ensure the service starts at boot even if you haven't logged in yet:
    ```bash
    loginctl enable-linger $USER
    ```

## Troubleshooting

View the logs for the service:
```bash
journalctl --user -u luma_sys_info.service -f
```
#!/bin/bash
# Custom Odoo entrypoint to initialize database and install custom modules

set -e

# Original Odoo entrypoint
if [ -f /entrypoint.sh ]; then
    # Check if we need to initialize the database
    if [ "$1" == "odoo" ] && [ -n "$ODOO_DB_NAME" ]; then
        # Start Odoo in background to initialize
        /entrypoint.sh odoo -d "$ODOO_DB_NAME" -i base --stop-after-init &
        PID=$!
        wait $PID || true
        
        # Install custom modules if they exist
        if [ -d /mnt/extra-addons ]; then
            for addon in /mnt/extra-addons/*/; do
                addon_name=$(basename "$addon")
                echo "Installing addon: $addon_name"
                /entrypoint.sh odoo -d "$ODOO_DB_NAME" -i "$addon_name" --stop-after-init &
                wait $! || true
            done
        fi
    fi
fi

# Run the main Odoo server
exec /entrypoint.sh "$@"


---
title: 
cascade:
  type: docs
weight: 4
---

# Command Line Installer

It's recommended to run the command line as your system's web user. You will need to know what the web user is for your system. For example:
- **Ubuntu/Debian**: `www-data`
- **CentOS**: `apache`

## Example of Using the Command Line (as root)

Substitute `www-data` with your system's web user. Follow these steps:

```bash
# Change the ownership of the Moodle directory to the web user
chown www-data /path/to/moodle

# Navigate to the Moodle CLI directory
cd /path/to/moodle/admin/cli

# Run the installation script using the web user
sudo -u www-data /usr/bin/php install.php

# Change the ownership back to root for security
chown -R root /path/to/moodle

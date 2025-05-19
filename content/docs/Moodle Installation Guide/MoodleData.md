---
title: 
cascade:
  type: docs
weight: 3
---

# Create the `moodledata` Directory

Moodle requires a directory to store all of its files, including uploaded files, temporary data, cache, session data, and more. The web server needs to have write access to this directory. When allocating space for this directory, especially on larger systems, consider how much free space you'll need.

{{< callout type="warning" >}}
  - This directory **must not** be accessible directly via the web. Allowing web access would create a serious security risk.
- Do not place it inside your web root or inside the Moodle program files directory.
- Moodle will not install if this condition is not met.
- It can be placed anywhere convenient outside of the web root and Moodle program files directory.

{{< /callout >}}


## Example (Unix/Linux):

To create the `moodledata` directory and set the correct permissions for the web server user, follow these steps:

```bash
# Create the moodledata directory
mkdir /path/to/moodledata

# Set the permissions so anyone on the server can write to the directory
chmod 0777 /path/to/moodledata

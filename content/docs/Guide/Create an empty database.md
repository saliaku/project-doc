---
title: Create an Empty Database
cascade:
  type: docs
weight: 2
---


Next, create a new, empty database for your installation. You need to find and make a note of the following information for use during the final installation stage:

- **dbhost** - the database server hostname. Probably `localhost` if the database and web server are the same machine, otherwise the name of the database server.
- **dbname** - the database name. Whatever you called it, e.g., `moodle`.
- **dbuser** - the username for the database. Whatever you assigned, e.g., `moodleuser`. Do not use the `root`/superuser account. Create a proper account with the minimum permissions needed.
- **dbpass** - the password for the above user.

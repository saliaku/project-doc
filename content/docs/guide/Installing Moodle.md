---
title: 
cascade:
  type: docs
weight: 1
---

### Download and Copy Files into Place

You have two options for getting Moodle:

1. **Pull the Code from the Git Repository**  
   This method is recommended for developers and makes upgrading very simple. To pull the Moodle code, run the following command:

   ```bash
   git clone -b MOODLE_405_STABLE git://git.moodle.org/moodle.git

{{< callout type="info" >}}
  Tip: If you are downloading Moodle to your local computer and then uploading it to your hosted web site, it is usually better to upload the compressed Moodle file and then decompress on your hosted web site. If you decompress Moodle on your local computer, because Moodle is comprised of over 25,000 files, trying to upload over 25,000 files using an FTP client or your host's "file manager" can sometimes miss a file and cause errors.
{{< /callout >}}

### Secure the Moodle Files

It is vital that the files are not writeable by the web server user. For example, on Unix/Linux (as root):

```bash
chown -R root /path/to/moodle
chmod -R 0755 /path/to/moodle
```

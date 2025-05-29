---
title: Getting Started
cascade:
type: docs
weight: 1
---


# Setting up the Server

This guide will walk you through the steps to install and set up a Moodle server on a Linux-based system (Ubuntu). Moodle is a popular open-source learning management system (LMS) that is widely used for online learning environments.

## Prerequisites

Before starting the moodle installation, ensure you have the following:

- A Linux server (Ubuntu is used in this guide).
- A user account with root privileges.
- Basic knowledge of the terminal and SSH (if you're installing remotely).
- A working LAMP stack (Linux, Apache, MySQL, PHP).

If you don't have LAMP installed, follow the below steps first.

## Moodle Hardware Requirements

The hardware requirements for Moodle can vary based on the number of users and the type of content. The following are general recommendations for a Moodle server:

### Minimum Hardware Requirements

- **Disk Space**: 
  - 200MB for the Moodle code, plus as much as you need to store content. 
  - 5GB is probably a realistic minimum.
  
- **Processor**: 
  - 1 GHz (min), 
  - 2 GHz dual-core or more is recommended.

- **Memory**: 
  - 512MB (min), 
  - 1GB or more is recommended.
  - For large production servers, 8GB plus may be required.




## Setting Up

### 1. Update your system:
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Apache
```bash
sudo apt install apache2
```

### 3. Install MySQL
```bash
sudo apt install mysql-server
```

### 4. Install PHP and required extensions
```bash
sudo apt install php php-mysqli php-xmlrpc php-soap php-intl php-mbstring php-xml php-zip php-curl php-gd
```

### 5.Install additional dependencies:
```bash
sudo apt install libjpeg-dev libpng-dev libfreetype6-dev
```

### 6. Restart Apache to apply the changes:
```bash
sudo systemctl restart apache2
```

## For a More Detailed Guide

For more detailed information on Moodle's installation requirements, please refer to the official [Moodle Installation Requirements](https://docs.moodle.org/405/en/Installing_Moodle#Requirements).
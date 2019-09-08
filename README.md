InstAPI
=============

[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet)](https://www.python.org/dev/peps/pep-0008/) 
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](/LICENSE) 
[![Build Status](https://travis-ci.com/uriyyo/instapi.svg?branch=develop)](https://travis-ci.com/uriyyo/instapi)
[![codecov](https://codecov.io/gh/uriyyo/instapi/branch/develop/graph/badge.svg)](https://codecov.io/gh/uriyyo/instapi)

<h1 align="center">
  <img src="/logo.svg" alt="Instapi" width="256" height="256">
</h1>

InstAPI - comfortable and easy to use Python's library for interaction with Instagram.

Installation
------------
1. Download InstAPI from this repository.
2. Run `pip install -e [PATH to directory with InstAPI]` in console.
3. Done!

Usage
-----
Example how to like all feeds for user
```python
from instapi import bind
from instapi import User

bind('your_username_here', 'your_password_here')

# Get user profile by username
instagram_profile = User.from_username('username')

# Like all posts
for feed in instagram_profile.iter_feeds():
  feed.like()
```

Install requires
----------------
* dataclasses (version 0.6.0)
* instagram-private-api (version 1.6.0.0)
* Pillow (version 6.1.0)
* requests (version 2.22.0)

Release History
---------------
* 0.0.1
  * Work in progress

Contribute
----------
Contributions are always welcome!

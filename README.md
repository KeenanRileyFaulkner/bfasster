# Bfasster: BFASST 2.0

This project removes a lot of overhead from the [bfasst project](https://github.com/byuccl/bfasst). 
* It takes advantage of the ninja build tool to automatically handle job creation, up-to-date checking of dependencies, parallel processing, and io redirection. 
* It uses chevron, the python implementation of the mustache templating engine.
* It keeps python as its base language, rather than switching to bash in order to minimize the learning curve in transitioning to the new architecture.

The project is currently in demo mode, with few designs and flows supported as compared to the original bfasst. The hope is to migrate all flows and designs from the original project over to this new architecture.

### Usage:

```py
python bfasster.py
```
_or_
```py
python flows/vivado.py
cd designs/add4/out
ninja
```
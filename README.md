# Bfasster: BFASST 2.0

This project removes a lot of overhead from the [bfasst project](https://github.com/byuccl/bfasst). 
* It takes advantage of the ninja build tool to automatically handle job creation, up-to-date checking of dependencies, parallel processing, and io redirection. 
* It uses chevron, the python implementation of the mustache templating engine.
* It keeps python as its base language, rather than switching to bash in order to minimize the learning curve in transitioning to the new architecture.

The project is currently in demo mode, with few designs and flows supported as compared to the original bfasst. The hope is to migrate all flows and designs from the original project over to this new architecture.

### Usage:

<pre>Usage:<code>
    python bfasster.py [--yaml YAML] [--design DESIGN] [--flow FLOW]

options:
    --yaml YAML         The yaml experiment to run, same as with bfasst
    --design DESIGN     The design to run
    --flow FLOW         The flow to use for the specified design

NOTE: You must specify <em>either</em> a yaml file or <em>both</em> a design and flow
</code></pre>

_or_

```
python bfasster/flows/vivado.py
cd designs/byu/alu/out
ninja
```
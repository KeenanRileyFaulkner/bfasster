# Bfasster: BFASST 2.0

This project removes a lot of overhead from the [bfasst project](https://github.com/byuccl/bfasst). 
* It takes advantage of the ninja build tool to automatically handle job creation, up-to-date checking of dependencies, parallel processing, and io redirection. 
* It uses chevron, the python implementation of the mustache templating engine to template the scripts used for common operations such as synthesis and implementation of designs, and even the running of other ninja files at the top level.
* It keeps python as its base language, rather than switching to bash in order to minimize the learning curve and maximize portability in transitioning to the new architecture.

The project is currently in demo mode, with few designs and flows supported as compared to the original bfasst. The hope is to migrate all flows and designs from the original project over to this new architecture.

### Usage:

There are two steps two running any flow with any design(s): a ninja generation step and a run step. For convenience, a script is included to execute both steps sequentially with a single command:

<pre>Usage:<code>
    python bfasster.py [--yaml YAML] [--design DESIGN] [--flow FLOW]

options:
    --yaml YAML         The yaml experiment to run, same as with bfasst
    --design DESIGN     The design to run
    --flow FLOW         The flow to use for the specified design

NOTE: You must specify <em>either</em> a yaml file or <em>both</em> a design and flow.
</code></pre>

Alternatively, you can execute the ninja generation step entirely separate from the run step for a single design:

<pre style="padding-top:0">Usage:<code>
    python bfasster/flows/vivado.py [--design DESIGN]
    ninja
</code></pre>
In either use case, the design should be specified as a subdirectory of the included designs directory in this repo (e.g. 'byu/alu').
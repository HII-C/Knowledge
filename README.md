# Knowledge

## About

This is the Knowledge repository for the HII-C project. This repository contains
the scripts that process the medical source data to form an intelligent medical knowledge
base. If you are looking for how this knowledge base is processed and delivered on our 
API, look at our [MedLearnAPI repository](https://github.com/HII-C/MedLearnAPI).


## Building

If you wish to change the default environment values and configurations, you can modify 
the config files provided in the data folder prior to building. Note that modules
can still be loaded with custom configs at runtime. See the documentation for more
details regarding important environment variables and configurations.

To build, clone this repository and install using pip:

```
    git clone https://github.com/HII-C/Knowledge.git /path/to/repository
    pip install /path/to/repository
```

The package will be installed under the name `knowledge-hiic` and root module will be
named `knowledge`.


## Environment Creation

Once you have built the package, you may wnat to recreate the environment for a given 
medical dataset. 


## Documentation

### `knowledge.model`

scripts for the medical concept association generation models

- fpgrowth

### `knowledge.util`

various utilities used through out project

- dropbox
- print
- database

### `knowledge.env`

scripts focused on manipulation the data environment

-
-

### `knowledge.source`

scripts to load and process data from their source files

-
-

## Contributing

If you are contributing to this repository, please read through the guidelines in the
[contribution file](https://github.com/HII-C/Knowledge/blob/master/CONTRIBUTING.md). 
These guidelines are a mixture of the basic python best practices as well as some structural
practices specific to to this project that keep our code clean, consistent, and organized.


## Archive

You can find old scripts from this repository stored in the archive folder. These 
scripts are not involved in the ongoing build of the Knowledge repository but are kept
as reference to old code or as code to be implemented in the future.
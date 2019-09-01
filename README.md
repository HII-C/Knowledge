# Knowledge

## About

This is the Knowledge repository for the HII-C project. This repository contains
the scripts that process the medical source data to form an intelligent medical knowledge
base. If you are looking for how this knowledge base is processed and delivered on our 
API, look at our [MedLearnAPI repository](https://github.com/HII-C/MedLearnAPI).

---

## Building

If you wish to change the default environment values and configurations, you can modify 
the config files provided in the data folder prior to building. Note that modules
can still be loaded with custom configs at runtime. See the documentation for more
details regarding important environment valiables and configurations.

To build, clone this repository and install using pip:

```
    git clone https://github.com/HII-C/Knowledge.git /path/to/repository
    pip install /path/to/repository
```

---

## Environment Creation

Once you have built the package, you may wnat to recreate the environment for a medical
dataset.

---

## Documentation

### **`knowledge.model`**

scripts for the medical concept association generation models

-
-

### **`knowledge.util`**

various utilities used through out project

-
-

### **`knowledge.env`**

scripts focused on manipulation the data environment

-
-

### **`knowledge.source`**

scripts to load and process data from their source files

-
-

---

## Contributing

If you are contributing to this repository, please review the best practices and general
structure expectations in the 
[contribution file](https://github.com/HII-C/Knowledge/CONTRIBUTING.md). These guidelines 
are a mixture of the basic python best practices as well as some structural practices 
specific to to this project that keep our code clean, consistent, and organized.

---

## Archives

You can find old scripts from this repository stored in the archives folder. These 
scripts are not involved in the ongoing build of the Knowledge repository but are kept
as reference to old code or as code to be implemented in the future.
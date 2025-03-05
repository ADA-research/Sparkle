# Frequently Asked Questions

In this section we discuss various questions and problems you may run into when using Sparkle.

## Setting up

A problem that can occur for most users in the beginning is setting up the required compilers and executables such as `GCC`, `R` or `Java`.

### Lmod: I am having problems managing my versions in Lmod, what can I do?

If your system works with [Lmod](http://lmod.readthedocs.org), we recommend loading the modules in the following order (Check that the versions are available):

```bash
module load R/4.3.2
module load Java/8.402
module load numactl/2.0.16-GCCcore-12.2.0
```

Whilst loading these modules you can receive various messages that module versions have changed whilst loading. Executing the loads in this order will ensure the changes are correct. Afterwards you can save your loaded modules as a set with nickname `sparkle` by typing:

```bash
module save sparkle
```

Which can then at a later point easily be loaded by typing:

```bash
module restore sparkle
```

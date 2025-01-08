(tutorials)=
# Tutorials

In this section we demonstrate the usage of the platform for Algorithm Configuration, the creation of Algorithm Portfolios and Algorithm Selection.

## Setting up Sparkle

Before running Sparkle, you probably want to have a look at the settings described in the {ref}`Platform <settings>` section.
In particular, the default Slurm settings should be reconfigured to work with your cluster, for example by specifying a partition to run on.

### Recompilation of example Solvers

Although the examples come precompiled with the download, in some cases they may not directly work on your target system due to certain target-system specific choices that are made during compilation. You can follow the steps below to re-compile.

#### CSCCSat

The CSCCSat Solver can be recompiled as follows in the `Examples/Resources/Solvers/CSCCSat/` directory:

```bash
unzip src.zip
cd src/CSCCSat_source_codes/
make
cp CSCCSat ../../
```

#### MiniSAT

The MiniSAT solver can be recompiled as follows in the `Examples/Resources/Solvers/MiniSAT/` directory:

```bash
unzip src.zip
cd minisat-master/
make
cp build/release/bin/minisat ../
```

#### PbO-CCSAT
The PbO-CCSAT solver can be recompiled as follows in the `Examples/Resources/Solvers/PbO-CCSAT-Generic/` directory:

```bash
unzip src.zip
cd PbO-CCSAT-master/PbO-CCSAT_process_oriented_version_source_code/
make
cp PbO-CCSAT ../../
```

#### TCA and FastCA
The TCA and FastCA solvers, require `GLIBCXX_3.4.21`. This library comes with `GCC 5.1.0` (or greater). Following installation you may have to update environment variables such as `LD_LIBRARY_PATH, LD_RUN_PATH, CPATH` to point to your installation directory.

TCA can be recompiled as follows in the
`Examples/Resources/CCAG/Solvers/TCA/` directory:

```bash
unzip src.zip
cd TCA-master/
make clean
make
cp TCA ../
```

FastCA can be recompiled as follows in the `Examples/Resources/CCAG/Solvers/FastCA/` directory:

```bash
unzip src.zip
cd fastca-master/fastCA/
make clean
make
cp FastCA ../../
```

#### VRP_SISRs

VRP_SISRs solver can be recompiled as follows in the `Examples/Resources/CVRP/Solvers/VRP_SISRs/` directory:

```bash
unzip src.zip
cd src/
make
cp VRP_SISRs ../
```

#### FastVC2+p

FastVC2+p requires `glibc-static` in order to compile, and is currently untested within Sparkle.
It can be recompiled as follows in the `Examples/Resources/MinVC/Solvers/FastVC2+p` directory:

```bash
unzip FastVC2+p_std_source_code.zip
cd FastVC2+p_std_source_code
make

```

```{include} ../../Examples/configuration_runtime.md
```

```{include} ../../Examples/configuration_quality.md
```

```{include} ../../Examples/configuration_randomforest.md
```

```{include} ../../Examples/parallel_portfolio_runtime.md
```

```{include} ../../Examples/selection.md
```

```{include} ../../Examples/selection_multi-file_instance.md
```

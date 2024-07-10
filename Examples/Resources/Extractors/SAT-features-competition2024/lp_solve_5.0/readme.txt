July 21, 2004

This is the release version of lp_solve 5.0
-------------------------------------------

The engine of this new version has changed fundamentally (thanks to Kjell Eikland).  The result
is more speed and more stability, which means that larger and tougher models can be solved.
The file and module structure of lp_solve is now also a very much-improved platform for further
development.  Check lp_solve.chm, or the HTML help files for a fuller description changes since
version 4.0.  Begin by taking a look at 'Changes compared to version 4' and 'lp_solve usage'
This gives a good starting point.

lp_solve v5 is herewith released.  It is a major enhancement compared to v4 in
terms of functionality, usability, accessibility and documentation.  While the
new core v5 engine has been tested for 6 months, including a beta phase of 3 months,
there are areas of the code that contain placeholders for coming functionality
and can therefore not be expected to be verified.  This includes partial and
multiple pricing and, to a lesser extent, Steepest Edge-based pricing.  In
addition, the development team is aware of issues related to particulare settings
that in some cases can make worst-case performance unsatisfactory.

For example, the default tolerance settings are known to be very thight compared
to many other solvers.  This can in a few very rare cases lead to excessive
running times or that lp_solve determines the model to be infeasible.  We have
chosen to keep the tight settings since in many cases we have found that other
solvers produce solutions even if the underlying solution quality is unacceptable
or strictly considered even infeasible.  We may, however, decide to selectively
loosen tolerances in a v5 subrelease if we feel that this is warranted.


BFP stands for Basis Factorization Package, which is a unique lp_solve feature.  Considerable
effort has been put in this new feature and we have big expectations for this. BFP is a generic
interface model and users can develop their own implementations based on the provided templates.
We are very interested in providing as many different BFPs as possible to the community.

lp_solve has the v3.2 etaPFI built in as default engine, versioned 1.0,  In addition two other
BFPs are included for both Windows and Linux: bfp_LUSOL.dll, bfp_etaPFI.dll for Windows and
libbfp_LUSOL.so, libbfp_etaPFI.so for Linux.  The standalone bfp_etaPFI is v2.0 and includes
advanced column ordering using the COLAMD library, as well as better pivot management for
stability.  For complex models, however, the LU factorization approach is much better, and
lp_solve now includes LUSOL as one of the most stable engines available anywhere.  LUSOL was
originally developed by Prof. Saunders at Stanford, and it has now been ported to C
and enhanced by Kjell.  It is expected that the LUSOL source will be made available.

Note that for the time being only bfp_etaPFI can be recompiled by you using the included source.
A third BFP based on GLPK may be included later, but license issues must first be resolved.  In
the interim, you may experiment with the working sample BFP interface files for GLPK.

If you compile BFPs yourself, make sure that under Windows, you use __stdcall convention and
use 4 byte alignments.  This is needed for the BFPs to work correctly with the general
distribution of lp_solve and also to make sharing BFPs as uncomplicated as possible.

Don't forget that the API has changed compared to previous versions of lpsolve and that you just
can't use the version 5 lpsolve library with your version 4 or older code.  That is also the
reason why the library is now called lpsolve5.dll/lpsolve5.a.  lpsolve5.dll or lpsolve5.a are
only needed when you call the lpsolve library via the API interface from your program.
The lp_solve program is still a stand-alone executable program.

There are examples interfaces for different language like C, VB, C#, VB.NET, JAVA (Windows only),
Delphi, and there is now also even a COM object to access the lpsolve library.  This means that
the door is wide-open for using lp_solve in many different situations.  Thus everything that is
available in version 4 is now also available in version 5 and already much more!

Note that lp2mps and mps2lp don't exist anymore. However this functionality is now implemented
in lp_solve:

lp2mps can be simulated as following:
lp_solve -parse_only -lp infile -wmps outfile

mps2lp can be simulated as following:
lp_solve -parse_only -mps infile -wlp outfile


Change history:

??/??/?? version incorrect, probably 5.0.0.0
- Some small bugs are solved
- print_lp reported wrong information on ranges on constraints
- A new function print_tableau is added
- The demo program failed at some points. Fixed
- Solving time is improved again. Calculation of sensitivity is only done when asked for.

01/05/04 version incorrect, probably 5.0.0.0
- Some compiler warnings solved
- New API function print_str
- Some functions were not exported in the lpsolve5 dll. Fixed.

02/05/04 version incorrect, probably 5.0.0.0
- Solved some small bugs
- New API routine is_maxim added.
- New API routine is_constr_type added.
- New API routine is_piv_rule added.
- Routine get_reduced_costs renamed to get_dual_solution.
- Routine get_ptr_reduced_costs renamed to get_ptr_dual_solution.
- Return codes of solve API call are changed.
- ANTIDEGEN codes have changed. See set_anti_degen.

08/05/04 version 5.0.4.0
- Routine write_debugdump renamed to print_debugdump
- Routine set_scalemode renamed to set_scaling
- Routine get_scalemode renamed to get_scaling
- New API routine set_add_rowmode added
- New API routine is_add_rowmode added
- Fix of a B&B subperformance issue
- File lp_lp.h renamed to lp_wlp.h
- File lp_lp.c renamed to lp_wlp.c
- File lp_lpt.h renamed to lp_rlpt.h
- File lp_lpt.c renamed to lp_rlpt.c
- File read.h renamed to yacc_read.h
- File read.c renamed to yacc_read.c
- File lex.l renamed to lp_rlp.l
- File lp.y renamed to lp_rlp.y
- File lex.c renamed to lp_rlp.h
- File lp.c renamed to lp_rlp.c

If you build your model via the routine add_constraint, then take a look at the
new routine set_add_rowmode. It will result in a spectacular performance improvement
to build your model.

17/05/04 version 5.0.5.0
- Reading from lp and mps file is considerably made faster. Especially for larger models
  The improvement can be spectacular.
  Also writing lp and mps files are made faster.
- Improvements in B&B routines. Big models take less memory. Can be up to 50%
- Under Windows, the byte alignment is changed to 4 (before it was 1 in version 5).
  This results in some speed improvements. Test gave some 5% improvement.
- is_anti_degen did not return the correct status with ANTIDEGEN_NONE. Fixed.
- is_presolve did not return the correct status with PRESOLVE_NONE. Fixed.
- Under non-windows system, BFP_CALLMODEL doesn't have to be specified anymore

25/05/04 version 5.0.6.0
- lp_solve5.zip now also contains the needed header files to build a C/C++ application.
  The source files that use the lpsolve API functions must now include lp_lib.h
  lpkit.h is obsolete. It is only used internally in the lpsolve library.
  Developers using the lpsolve library must use lp_lib.h
  The examples are changed accordingly.
- set_piv_rule renamed to set_pivoting
- get_piv_rule renamed to get_pivoting
- is_piv_strategy renamed to is_piv_mode
- Constants INFEASIBLE, UNBOUNDED, DEGENERATE, NUMFAILURE have new values
- New solve return value: SUBOPTIMAL
- When there are negative bounds on variables such that these variables must be split in
  a negative and a positive part and solve was called multiple time, then each time the solve
  was done, a new split was done. This could lead to bad performance. Corrected.
- API function get_row is now considerably faster, especially for large models.
- When compiled with VC, some warnings were given about structure alignment. Solved.
- Creation of an mps file (via write_mps) sometimes created numbers with the wrong sign.
  This problem was introduced in 5.0.5.0. Corrected.
- In several source files there were improper /* */ comments. Corrected.
- Several improvements/corrections in the algorithms.
- Some corrections in writing the model to an lp/lpt file.

29/05/04 version 5.0.7.0
- A small error corrected in the lp parser. If there was a constraint with both a lower
  and upper restriction on the same line and with only one variable, then the parser did
  not accept this. For example:
  R1: 1 <= x <= 2;
  This is now corrected.
  Note that normally it is preferred to make of this a bound instead of a constraint:
  1 <= x <= 2;
  This results in a smaller model (less constraints) and faster solution times.
  By adding the label: prefix it is forced as a constraint. This can be for testing purposes
  of in some special circumstances.
- Return values in case of user abort and timeout is now cleaner, and makes it possible to recover
  sub optimal values directly (if the problem was feasible)..
- calculate_duals and sensitivity duals could not be constructed in the presence of free variables
  when these were deleted. The deletion / cleanup of free variables was enforced in the previous beta.
- Added constant PRESOLVE_DUALS so that the program precalculates duals, and always if there are free
  variables. The PRESOLVE_SENSDUALS are only calculated if the user has explicitly asked for it, even
  if there are split variables. The only way to get around this problem is to convert the simplex
  algorithm to a general bounded version, which is a v6 issue.
- Presolve is accelerated significantly for large models with many row and column removals.
  This is done by moving the basis definition logic to after the presolve logic.
- Factorization efficiency statistics were sometimes computed incorrectly with non-etaPFI BFPs.
  This is now fixed without any effect on the user.
- Some minor tuning of bfp_LUSOL has been done.  There will be more coming in this department later.
- Routines set_add_rowmode and is_add_rowmode were not available in the lpsolve5.dll dll. Corrected.
- Constant PRESOLVE_SENSDUALS has new value. Before it was 128. Now it is 256.

04/06/04 version 5.0.8.0
- There was an error in the CPLEX lp parser. When there is a constraint (Subject To section) with only
  one variable (like -C1 >= -99900), the file could not be read. Fixed.
  Note that it is better to have bounds on this kind of constraints. (C1 <= 99900). This gives
  better performance. On the other hand, presolve detects these conditions and auto converts them
  to bounds.
- Under Windows, byte alignment is now set to 8 (previously it was 4). Gives some better performance.
- There were a couple of problems when a restart was done. lp_solve failed, gave numerical unstable
  errors, NUMFAILURE return code.
  Also when the objective function was changed after a solve and solve was done again, lp_solve
  stated that the model was infeasible.
  Also when the objective function or an element in the matrix was changed and a previous non-zero value
  was set to zero, the matrix was blown up with unpredictable effects. Even an unhandled exception error/
  core dump could be the result of this problem.
  These problems should be solved now.
- There was a potential problem in the MPS reader. When column entries were not in ascending order,
  the model could not be read (add_columnex error message).
  Note that lp_solve always generates column entries in ascending order. So the problem only
  occurred when the MPS file was created outside of lp_solve.
- add_columnex did not return FALSE if column entries were not in ascending order.
- Added the option -S7 to the lp_solve program to also print the tableau
- Added a functional index in the lp_solve API reference. API calls are grouped per functionality.
  This can be a great help to find which API routines are needed at which time.
- Added in the manual a section about Basis Factorization Packages (BFPs)

08/06/04 version 5.0.8.1
- There was a memory leak when solve was called multiple times after each other. Fixed.

18/06/04 version 5.0.9.0
- There was a possible memory overrun in some specific cases. This could result in protection
  errors and crashes.
- The default branch-and-bound depth limit is now set to 50 (get_bb_depthlimit)
- There are two new API functions: add_constraintex and set_obj_fnex
- On some systems, the macro CHAR_BIT is already defined and the compiler gave a warning about it. Fixed.
- variable vector is renamed. In some situations this confliced with a macro definition.
- Before, version 5 had to be compiled with __stdcall calling convention. This is no longer
  required. Any calling convention is now ok.
- Big coefficients (>2147483647) in the matrix were handled incorrectly resulting in totally
  wrong results. Corrected.
- column_in_lp now returns an integer indicating the column number where it is found in the lp
  If the column is not in the lp it returns 0.
- get_orig_index and get_lp_index returned wrong values if the functions were used before solve.
  Fixed.
- New routines added: add_constraintex and set_obj_fnex
- New constants PRICE_MULTIPLE and PRICE_AUTOPARTIAL added for set_pivoting/get_pivoting/is_piv_mode
  added new options -pivm and -pivp to lp_solve program to support these new constants.
- New routines read_XLI, write_XLI, has_XLI, is_nativeXLI added to support user written
  model language interfaces. Not yet documented in the manual. Here is a short explanation:
    As you know, lp_solve supports reading and writing of lp, mps and CPLEX lp style model files.
    In addition, lp_solve is interfaced with other systems via LIB code link-ins or the DLL,
    but this has never been an officially supported part of lp_solve.

    To facilitate the development of other model language interfaces, a quite
    simple "eXternal Language Interface" (XLI) has been defined, which allows
    lp_solve to be dynamically configured (at run-time) to use alternative XLIs.
    At present, a MathProg (AMPL subset) interface is in place, and the template
    is provided for other platforms. An XML-based interface is likely to come
    fairly soon also. Obviously, all existing interface methods will remain
    unchanged.

21/07/04 version 5.0.10.0
- This is the first official release of version 5!!!
- The default branch-and-bound depth limit is not 50 as specified in 5.0.9.0, but -50
  This indicates a relative depth limit. See the docs.
- The callback functions were not working properly because they didn't have the __stdcall
  attributes. Fixed. Also modified the VB, VB.NET, CS.NET examples to demonstrate the
  callback features.
- lp_colamdMDO.c and lp_colamdMDO.h renamed to lp_MDO.c and lp_MDO.h
- lp_pricerPSE.c and lp_pricerPSE.h renamed to lp_price.h/lp_pricePSE.h and lp_price.c/lp_pricePSE.c
- New routines read_freemps, read_freeMPS, write_freemps, write_freeMPS for reading/writing
  free MPS format.
- Added options -mfps, -wfmps to lp_solve command line program to handle free MPS files
- There was an error in set_obj_fnex when not in row add mode such that the object function
  was not set correct. Fixed.
- read_XLI, write_XLI now has an extra parameter: options
- Revised default_basis, set_basis to be more robust for wrong provided data.
  set_basis now returns a boolean indicating success of not.
- several internal improvements
- New pricer strategies constants: PRICE_PARTIAL, PRICE_LOOPLEFT, PRICE_LOOPALTERNATE.
- PRICE_ADAPTIVE, PRICE_RANDOMIZE have new values.
- All API functions are now available via the lp structure. This is needed for the XLIs.
- MathProg XLI now uses lp_solves verbose level to print messages.
- MathProg XLI fix for constant term in constraint.
- Fixed possible memory overrun in report function.
- added options -rxli, -rxlidata, -rxliopt to lp_solve command line program to read with XLI library
- added options -wxli, -wxliopt to lp_solve command line program to write with XLI library
- write_lpt, write_LPT now writes to the output set by set_outputstream/set_outputfile when NULL is
  given as filename, stream. Previously output was then written to stdout.
- set_break_at_value (-o option in lp_solve program) didn't work. Fixed.
- The lp format now also allows constant terms in the objective function.
  This value is added with the objective function value.
  This constant was already allowed by the MPS format and is also written when an lp file
  is created (see lp-format in help file).
- Fixed a runtime/protection/core dump error when a timeout occured.

We are thrilled to hear from you and your experiences with this new version. The good and the bad.
Also we would be pleased to hear about your experiences with the different BFPs on your models.

Please send reactions to:
Peter Notebaert: peno@mailme.org
Kjell Eikland: kjell.eikland@broadpark.no

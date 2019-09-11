/* A Bison parser, made by GNU Bison 2.3.  */

/* Skeleton implementation for Bison's Yacc-like parsers in C

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006
   Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor,
   Boston, MA 02110-1301, USA.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* All symbols defined below should begin with lp_yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output.  */
#define YYBISON 1

/* Bison version.  */
#define YYBISON_VERSION "2.3"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Using locations.  */
#define YYLSP_NEEDED 0



/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum lp_yytokentype {
     VAR = 258,
     CONS = 259,
     INTCONS = 260,
     VARIABLECOLON = 261,
     INF = 262,
     SEC_INT = 263,
     SEC_SEC = 264,
     SEC_SOS = 265,
     SOSDESCR = 266,
     SIGN = 267,
     AR_M_OP = 268,
     RE_OPLE = 269,
     RE_OPGE = 270,
     END_C = 271,
     COMMA = 272,
     COLON = 273,
     MINIMISE = 274,
     MAXIMISE = 275,
     UNDEFINED = 276
   };
#endif
/* Tokens.  */
#define VAR 258
#define CONS 259
#define INTCONS 260
#define VARIABLECOLON 261
#define INF 262
#define SEC_INT 263
#define SEC_SEC 264
#define SEC_SOS 265
#define SOSDESCR 266
#define SIGN 267
#define AR_M_OP 268
#define RE_OPLE 269
#define RE_OPGE 270
#define END_C 271
#define COMMA 272
#define COLON 273
#define MINIMISE 274
#define MAXIMISE 275
#define UNDEFINED 276




/* Copy the first part of user declarations.  */
#line 9 "lp.y"

#include <string.h>
#include <ctype.h>

#include "lpkit.h"
#include "read.h"

static int HadVar0, HadVar1, HadVar2, do_add_row, Had_lineair_sum0, HadSign;
static char Last_var[NAMELEN], Last_var0[NAMELEN];
static REAL f, f0, f1;
static int x;
static int state, state0;
static int Sign;
static int isign, isign0;      /* internal_sign variable to make sure nothing goes wrong */
                /* with lookahead */
static int make_neg;   /* is true after the relational operator is seen in order */
                /* to remember if lin_term stands before or after re_op */
static int Within_int_decl = FALSE; /* TRUE when we are within an int declaration */
static int Within_sec_decl = FALSE; /* TRUE when we are within an sec declaration */
static int Within_sos_decl = FALSE; /* TRUE when we are within an sos declaration */
static int Within_sos_decl1;
static short SOStype0; /* SOS type */
static short SOStype; /* SOS type */
static int SOSNr;
static int weight; /* SOS weight */
static int SOSweight = 0; /* SOS weight */

static int HadConstraint;
static int HadVar;
static int Had_lineair_sum;

#define YY_FATAL_ERROR lex_fatal_error

/* let's please C++ users */
#ifdef __cplusplus
extern "C" {
#endif

static int wrap(void)
{
  return(1);
}

#ifdef __cplusplus
};
#endif

#define lp_yywrap wrap
#define lp_yyerror read_error

#include "lex.c"



/* Enabling traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif

/* Enabling verbose error messages.  */
#ifdef YYERROR_VERBOSE
# undef YYERROR_VERBOSE
# define YYERROR_VERBOSE 1
#else
# define YYERROR_VERBOSE 0
#endif

/* Enabling the token table.  */
#ifndef YYTOKEN_TABLE
# define YYTOKEN_TABLE 0
#endif

#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef int YYSTYPE;
# define lp_yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif



/* Copy the second part of user declarations.  */


/* Line 216 of yacc.c.  */
#line 202 "y.tab.c"

#ifdef short
# undef short
#endif

#ifdef YYTYPE_UINT8
typedef YYTYPE_UINT8 lp_yytype_uint8;
#else
typedef unsigned char lp_yytype_uint8;
#endif

#ifdef YYTYPE_INT8
typedef YYTYPE_INT8 lp_yytype_int8;
#elif (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
typedef signed char lp_yytype_int8;
#else
typedef short int lp_yytype_int8;
#endif

#ifdef YYTYPE_UINT16
typedef YYTYPE_UINT16 lp_yytype_uint16;
#else
typedef unsigned short int lp_yytype_uint16;
#endif

#ifdef YYTYPE_INT16
typedef YYTYPE_INT16 lp_yytype_int16;
#else
typedef short int lp_yytype_int16;
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif ! defined YYSIZE_T && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned int
# endif
#endif

#define YYSIZE_MAXIMUM ((YYSIZE_T) -1)

#ifndef YY_
# if YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(msgid) dgettext ("bison-runtime", msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(msgid) msgid
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YYUSE(e) ((void) (e))
#else
# define YYUSE(e) /* empty */
#endif

/* Identity function, used to suppress warnings about constant conditions.  */
#ifndef lint
# define YYID(n) (n)
#else
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static int
YYID (int i)
#else
static int
YYID (i)
    int i;
#endif
{
  return i;
}
#endif

#if ! defined lp_yyoverflow || YYERROR_VERBOSE

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#     ifndef _STDLIB_H
#      define _STDLIB_H 1
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's `empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (YYID (0))
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined _STDLIB_H \
       && ! ((defined YYMALLOC || defined malloc) \
	     && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef _STDLIB_H
#    define _STDLIB_H 1
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined _STDLIB_H && (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* ! defined lp_yyoverflow || YYERROR_VERBOSE */


#if (! defined lp_yyoverflow \
     && (! defined __cplusplus \
	 || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union lp_yyalloc
{
  lp_yytype_int16 lp_yyss;
  YYSTYPE lp_yyvs;
  };

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (sizeof (union lp_yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (sizeof (lp_yytype_int16) + sizeof (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

/* Copy COUNT objects from FROM to TO.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(To, From, Count) \
      __builtin_memcpy (To, From, (Count) * sizeof (*(From)))
#  else
#   define YYCOPY(To, From, Count)		\
      do					\
	{					\
	  YYSIZE_T lp_yyi;				\
	  for (lp_yyi = 0; lp_yyi < (Count); lp_yyi++)	\
	    (To)[lp_yyi] = (From)[lp_yyi];		\
	}					\
      while (YYID (0))
#  endif
# endif

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack)					\
    do									\
      {									\
	YYSIZE_T lp_yynewbytes;						\
	YYCOPY (&lp_yyptr->Stack, Stack, lp_yysize);				\
	Stack = &lp_yyptr->Stack;						\
	lp_yynewbytes = lp_yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAXIMUM; \
	lp_yyptr += lp_yynewbytes / sizeof (*lp_yyptr);				\
      }									\
    while (YYID (0))

#endif

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  3
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   104

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  22
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  59
/* YYNRULES -- Number of rules.  */
#define YYNRULES  91
/* YYNRULES -- Number of states.  */
#define YYNSTATES  115

/* YYTRANSLATE(YYLEX) -- Bison symbol number corresponding to YYLEX.  */
#define YYUNDEFTOK  2
#define YYMAXUTOK   276

#define YYTRANSLATE(YYX)						\
  ((unsigned int) (YYX) <= YYMAXUTOK ? lp_yytranslate[YYX] : YYUNDEFTOK)

/* YYTRANSLATE[YYLEX] -- Bison symbol number corresponding to YYLEX.  */
static const lp_yytype_uint8 lp_yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21
};

#if YYDEBUG
/* YYPRHS[YYN] -- Index of the first RHS symbol of rule number YYN in
   YYRHS.  */
static const lp_yytype_uint8 lp_yyprhs[] =
{
       0,     0,     3,     4,     9,    10,    12,    14,    17,    19,
      20,    24,    26,    28,    29,    30,    31,    40,    41,    42,
      43,    49,    51,    52,    56,    59,    61,    62,    64,    66,
      69,    71,    73,    75,    76,    80,    81,    87,    89,    92,
      93,    94,    98,    99,   100,   105,   106,   109,   110,   112,
     114,   118,   119,   121,   122,   123,   124,   125,   128,   132,
     135,   138,   141,   146,   147,   150,   152,   155,   157,   159,
     161,   164,   167,   170,   174,   175,   177,   178,   182,   187,
     188,   190,   191,   193,   194,   196,   199,   202,   204,   207,
     208,   210
};

/* YYRHS -- A `-1'-separated list of the rules' RHS.  */
static const lp_yytype_int8 lp_yyrhs[] =
{
      23,     0,    -1,    -1,    24,    77,    25,    40,    -1,    -1,
      26,    -1,    27,    -1,    26,    27,    -1,    30,    -1,    -1,
       6,    28,    30,    -1,    14,    -1,    15,    -1,    -1,    -1,
      -1,    76,    31,    29,    32,    37,    33,    34,    16,    -1,
      -1,    -1,    -1,    29,    35,    39,    36,    80,    -1,    63,
      -1,    -1,     7,    38,    80,    -1,    70,    66,    -1,     7,
      -1,    -1,    41,    -1,    43,    -1,    41,    43,    -1,     8,
      -1,     9,    -1,    10,    -1,    -1,    42,    44,    47,    -1,
      -1,    46,    48,    53,    50,    16,    -1,    45,    -1,    47,
      45,    -1,    -1,    -1,    11,    49,    59,    -1,    -1,    -1,
      14,     5,    51,    52,    -1,    -1,    18,     5,    -1,    -1,
      54,    -1,    60,    -1,    54,    55,    60,    -1,    -1,    17,
      -1,    -1,    -1,    -1,    -1,    75,    56,    -1,     6,    57,
      61,    -1,     5,    58,    -1,    59,    62,    -1,    75,    56,
      -1,     6,    57,     5,    58,    -1,    -1,    64,    65,    -1,
      68,    -1,    65,    68,    -1,     5,    -1,     4,    -1,    66,
      -1,    73,    75,    -1,    70,    67,    -1,    70,    71,    -1,
      69,    70,    71,    -1,    -1,    12,    -1,    -1,    75,    72,
      74,    -1,    66,    73,    75,    74,    -1,    -1,    13,    -1,
      -1,     3,    -1,    -1,    37,    -1,    20,    78,    -1,    19,
      78,    -1,    78,    -1,    79,    16,    -1,    -1,    69,    -1,
      -1
};

/* YYRLINE[YYN] -- source line where rule number YYN was defined.  */
static const lp_yytype_uint16 lp_yyrline[] =
{
       0,    67,    67,    67,    79,    80,    83,    84,    88,    90,
      89,    98,    98,   102,   107,   114,   101,   153,   159,   169,
     158,   194,   196,   195,   202,   204,   210,   211,   214,   215,
     218,   218,   218,   223,   222,   230,   230,   252,   253,   256,
     258,   257,   265,   273,   271,   288,   291,   298,   299,   302,
     303,   308,   309,   313,   340,   358,   382,   397,   399,   404,
     406,   411,   413,   420,   420,   438,   439,   443,   443,   446,
     450,   457,   494,   496,   502,   506,   514,   513,   518,   524,
     525,   529,   543,   547,   556,   562,   566,   570,   573,   584,
     585,   589
};
#endif

#if YYDEBUG || YYERROR_VERBOSE || YYTOKEN_TABLE
/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const lp_yytname[] =
{
  "$end", "error", "$undefined", "VAR", "CONS", "INTCONS",
  "VARIABLECOLON", "INF", "SEC_INT", "SEC_SEC", "SEC_SOS", "SOSDESCR",
  "SIGN", "AR_M_OP", "RE_OPLE", "RE_OPGE", "END_C", "COMMA", "COLON",
  "MINIMISE", "MAXIMISE", "UNDEFINED", "$accept", "inputfile", "@1",
  "constraints", "x_constraints", "constraint", "@2", "RE_OP",
  "real_constraint", "@3", "@4", "@5", "optionalrange", "@6", "@7",
  "xxx_lineair_sum", "@8", "cons_term", "int_sec_sos_declarations",
  "real_int_sec_sos_decls", "SEC_INT_SEC_SOS", "int_sec_sos_declaration",
  "@9", "xx_int_sec_sos_declaration", "@10", "x_int_sec_sos_declaration",
  "optionalsos", "@11", "optionalsostype", "@12", "optionalSOSweight",
  "vars", "x_vars", "optionalcomma", "variable", "variablecolon",
  "intcons", "sosdescr", "onevarwithoptionalweight", "INTCONSorVARIABLE",
  "x_onevarwithoptionalweight", "x_lineair_sum", "@13", "xxxx_lineair_sum",
  "REALCONS", "xx_lineair_term", "x_lineair_term", "lineair_sum", "x_SIGN",
  "lineair_term", "@14", "optional_AR_M_OP", "VAR_STORE", "VARIABLE",
  "xx_lineair_sum", "objective_function", "real_of",
  "optional_lineair_sum", "RHS_STORE", 0
};
#endif

# ifdef YYPRINT
/* YYTOKNUM[YYLEX-NUM] -- Internal token number corresponding to
   token YYLEX-NUM.  */
static const lp_yytype_uint16 lp_yytoknum[] =
{
       0,   256,   257,   258,   259,   260,   261,   262,   263,   264,
     265,   266,   267,   268,   269,   270,   271,   272,   273,   274,
     275,   276
};
# endif

/* YYR1[YYN] -- Symbol number of symbol that rule YYN derives.  */
static const lp_yytype_uint8 lp_yyr1[] =
{
       0,    22,    24,    23,    25,    25,    26,    26,    27,    28,
      27,    29,    29,    31,    32,    33,    30,    34,    35,    36,
      34,    37,    38,    37,    39,    39,    40,    40,    41,    41,
      42,    42,    42,    44,    43,    46,    45,    47,    47,    48,
      49,    48,    50,    51,    50,    52,    52,    53,    53,    54,
      54,    55,    55,    56,    57,    58,    59,    60,    60,    61,
      61,    62,    62,    64,    63,    65,    65,    66,    66,    67,
      67,    68,    69,    69,    70,    70,    72,    71,    71,    73,
      73,    74,    75,    76,    76,    77,    77,    77,    78,    79,
      79,    80
};

/* YYR2[YYN] -- Number of symbols composing right hand side of rule YYN.  */
static const lp_yytype_uint8 lp_yyr2[] =
{
       0,     2,     0,     4,     0,     1,     1,     2,     1,     0,
       3,     1,     1,     0,     0,     0,     8,     0,     0,     0,
       5,     1,     0,     3,     2,     1,     0,     1,     1,     2,
       1,     1,     1,     0,     3,     0,     5,     1,     2,     0,
       0,     3,     0,     0,     4,     0,     2,     0,     1,     1,
       3,     0,     1,     0,     0,     0,     0,     2,     3,     2,
       2,     2,     4,     0,     2,     1,     2,     1,     1,     1,
       2,     2,     2,     3,     0,     1,     0,     3,     4,     0,
       1,     0,     1,     0,     1,     2,     2,     1,     2,     0,
       1,     0
};

/* YYDEFACT[STATE-NAME] -- Default rule to reduce with in state
   STATE-NUM when YYTABLE doesn't specify something else to do.  Zero
   means the default is an error.  */
static const lp_yytype_uint8 lp_yydefact[] =
{
       2,     0,    74,     1,    75,    74,    74,    74,     0,    63,
      87,     0,    86,    85,     0,    82,    68,    67,    79,    72,
      76,     9,    22,    26,    63,     6,     8,    84,    21,    74,
      13,    88,    73,    80,     0,    81,    63,    91,    30,    31,
      32,     3,    27,    33,    28,     7,    74,    65,    79,     0,
      81,    77,    10,    23,    29,    35,    66,    69,    71,     0,
      11,    12,    14,    78,    37,    39,    35,    70,    63,    40,
      47,    38,    15,    56,    54,    42,    48,    49,    53,    17,
      41,    56,     0,     0,    52,     0,    57,    18,     0,    55,
       0,    58,    43,    36,    50,    74,    16,    59,    54,    60,
      53,    45,    25,    19,     0,     0,    61,     0,    44,    91,
      24,    55,    46,    20,    62
};

/* YYDEFGOTO[NTERM-NUM].  */
static const lp_yytype_int8 lp_yydefgoto[] =
{
      -1,     1,     2,    23,    24,    25,    36,    62,    26,    49,
      68,    79,    88,    95,   109,    27,    37,   103,    41,    42,
      43,    44,    55,    64,    65,    66,    70,    73,    83,   101,
     108,    75,    76,    85,    86,    81,    97,    80,    77,    91,
      99,    28,    29,    46,    18,    58,    47,     7,     8,    19,
      35,    34,    51,    20,    30,     9,    10,    11,    53
};

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
#define YYPACT_NINF -47
static const lp_yytype_int8 lp_yypact[] =
{
     -47,    49,    22,   -47,   -47,    34,    34,    44,    40,     3,
     -47,    17,   -47,   -47,    40,   -47,   -47,   -47,    48,   -47,
     -47,   -47,   -47,    55,    21,   -47,   -47,   -47,   -47,    60,
     -47,   -47,   -47,   -47,    70,   -47,    33,   -47,   -47,   -47,
     -47,   -47,    55,   -47,   -47,   -47,    39,   -47,    19,    52,
     -47,   -47,   -47,   -47,   -47,   -47,   -47,   -47,   -47,    70,
     -47,   -47,   -47,   -47,   -47,    63,     6,   -47,    68,   -47,
       1,   -47,   -47,   -47,   -47,    62,     2,   -47,   -47,    52,
     -47,    72,    73,    66,   -47,     1,   -47,   -47,    67,   -47,
      56,   -47,   -47,   -47,   -47,    13,   -47,   -47,   -47,   -47,
     -47,    61,   -47,   -47,    64,    75,   -47,    76,   -47,   -47,
     -47,   -47,   -47,   -47,   -47
};

/* YYPGOTO[NTERM-NUM].  */
static const lp_yytype_int8 lp_yypgoto[] =
{
     -47,   -47,   -47,   -47,   -47,    69,   -47,     5,    50,   -47,
     -47,   -47,   -47,   -47,   -47,    23,   -47,   -47,   -47,   -47,
     -47,    43,   -47,    24,   -47,   -47,   -47,   -47,   -47,   -47,
     -47,   -47,   -47,   -47,   -13,    -9,   -19,    14,     9,   -47,
     -47,   -47,   -47,   -47,   -46,   -47,    51,   -47,    -7,    82,
     -47,    53,    54,   -33,   -47,   -47,    65,   -47,   -11
};

/* YYTABLE[YYPACT[STATE-NUM]].  What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule which
   number is the opposite.  If zero, do what YYDEFACT says.
   If YYTABLE_NINF, syntax error.  */
#define YYTABLE_NINF -91
static const lp_yytype_int8 lp_yytable[] =
{
      14,    50,    57,    -4,    15,   -51,   -34,    74,   -51,    21,
      22,    -4,    -4,    -4,   -34,   -34,   -34,   -83,   -83,    84,
     102,    -5,    48,    16,    17,     4,    67,    21,    22,    -5,
      -5,    -5,    33,    31,     4,   -83,   -83,    78,   -89,    48,
      22,     5,     6,    15,    16,    17,     4,   -83,   -83,     3,
     -89,     4,    78,   -64,   -64,   -64,     4,   100,   110,    15,
     -90,    33,    98,    38,    39,    40,    60,    61,    16,    17,
      12,    13,     4,    15,    69,    22,    82,    89,    92,   107,
     111,   112,    93,    96,    87,    54,    52,   106,   104,   105,
      71,    72,   114,    45,    94,    90,    32,    56,   113,     0,
       0,    59,     0,     0,    63
};

static const lp_yytype_int8 lp_yycheck[] =
{
       7,    34,    48,     0,     3,     3,     0,     6,     6,     6,
       7,     8,     9,    10,     8,     9,    10,    14,    15,    17,
       7,     0,    29,     4,     5,    12,    59,     6,     7,     8,
       9,    10,    13,    16,    12,    14,    15,    70,    16,    46,
       7,    19,    20,     3,     4,     5,    12,    14,    15,     0,
      16,    12,    85,    14,    15,    16,    12,    90,   104,     3,
      16,    13,     6,     8,     9,    10,    14,    15,     4,     5,
       5,     6,    12,     3,    11,     7,    14,     5,     5,    18,
       5,     5,    16,    16,    79,    42,    36,   100,    95,    98,
      66,    68,   111,    24,    85,    81,    14,    46,   109,    -1,
      -1,    48,    -1,    -1,    50
};

/* YYSTOS[STATE-NUM] -- The (internal number of the) accessing
   symbol of state STATE-NUM.  */
static const lp_yytype_uint8 lp_yystos[] =
{
       0,    23,    24,     0,    12,    19,    20,    69,    70,    77,
      78,    79,    78,    78,    70,     3,     4,     5,    66,    71,
      75,     6,     7,    25,    26,    27,    30,    37,    63,    64,
      76,    16,    71,    13,    73,    72,    28,    38,     8,     9,
      10,    40,    41,    42,    43,    27,    65,    68,    70,    31,
      75,    74,    30,    80,    43,    44,    68,    66,    67,    73,
      14,    15,    29,    74,    45,    46,    47,    75,    32,    11,
      48,    45,    37,    49,     6,    53,    54,    60,    75,    33,
      59,    57,    14,    50,    17,    55,    56,    29,    34,     5,
      59,    61,     5,    16,    60,    35,    16,    58,     6,    62,
      75,    51,     7,    39,    70,    57,    56,    18,    52,    36,
      66,     5,     5,    80,    58
};

#define lp_yyerrok		(lp_yyerrstatus = 0)
#define lp_yyclearin	(lp_yychar = YYEMPTY)
#define YYEMPTY		(-2)
#define YYEOF		0

#define YYACCEPT	goto lp_yyacceptlab
#define YYABORT		goto lp_yyabortlab
#define YYERROR		goto lp_yyerrorlab


/* Like YYERROR except do call lp_yyerror.  This remains here temporarily
   to ease the transition to the new meaning of YYERROR, for GCC.
   Once GCC version 2 has supplanted version 1, this can go.  */

#define YYFAIL		goto lp_yyerrlab

#define YYRECOVERING()  (!!lp_yyerrstatus)

#define YYBACKUP(Token, Value)					\
do								\
  if (lp_yychar == YYEMPTY && lp_yylen == 1)				\
    {								\
      lp_yychar = (Token);						\
      lp_yylval = (Value);						\
      lp_yytoken = YYTRANSLATE (lp_yychar);				\
      YYPOPSTACK (1);						\
      goto lp_yybackup;						\
    }								\
  else								\
    {								\
      lp_yyerror (YY_("syntax error: cannot back up")); \
      YYERROR;							\
    }								\
while (YYID (0))


#define YYTERROR	1
#define YYERRCODE	256


/* YYLLOC_DEFAULT -- Set CURRENT to span from RHS[1] to RHS[N].
   If N is 0, then set CURRENT to the empty location which ends
   the previous symbol: RHS[0] (always defined).  */

#define YYRHSLOC(Rhs, K) ((Rhs)[K])
#ifndef YYLLOC_DEFAULT
# define YYLLOC_DEFAULT(Current, Rhs, N)				\
    do									\
      if (YYID (N))                                                    \
	{								\
	  (Current).first_line   = YYRHSLOC (Rhs, 1).first_line;	\
	  (Current).first_column = YYRHSLOC (Rhs, 1).first_column;	\
	  (Current).last_line    = YYRHSLOC (Rhs, N).last_line;		\
	  (Current).last_column  = YYRHSLOC (Rhs, N).last_column;	\
	}								\
      else								\
	{								\
	  (Current).first_line   = (Current).last_line   =		\
	    YYRHSLOC (Rhs, 0).last_line;				\
	  (Current).first_column = (Current).last_column =		\
	    YYRHSLOC (Rhs, 0).last_column;				\
	}								\
    while (YYID (0))
#endif


/* YY_LOCATION_PRINT -- Print the location on the stream.
   This macro was not mandated originally: define only if we know
   we won't break user code: when these are the locations we know.  */

#ifndef YY_LOCATION_PRINT
# if YYLTYPE_IS_TRIVIAL
#  define YY_LOCATION_PRINT(File, Loc)			\
     fprintf (File, "%d.%d-%d.%d",			\
	      (Loc).first_line, (Loc).first_column,	\
	      (Loc).last_line,  (Loc).last_column)
# else
#  define YY_LOCATION_PRINT(File, Loc) ((void) 0)
# endif
#endif


/* YYLEX -- calling `lp_yylex' with the right arguments.  */

#ifdef YYLEX_PARAM
# define YYLEX lp_yylex (YYLEX_PARAM)
#else
# define YYLEX lp_yylex ()
#endif

/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)			\
do {						\
  if (lp_yydebug)					\
    YYFPRINTF Args;				\
} while (YYID (0))

# define YY_SYMBOL_PRINT(Title, Type, Value, Location)			  \
do {									  \
  if (lp_yydebug)								  \
    {									  \
      YYFPRINTF (stderr, "%s ", Title);					  \
      lp_yy_symbol_print (stderr,						  \
		  Type, Value); \
      YYFPRINTF (stderr, "\n");						  \
    }									  \
} while (YYID (0))


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

/*ARGSUSED*/
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
lp_yy_symbol_value_print (FILE *lp_yyoutput, int lp_yytype, YYSTYPE const * const lp_yyvaluep)
#else
static void
lp_yy_symbol_value_print (lp_yyoutput, lp_yytype, lp_yyvaluep)
    FILE *lp_yyoutput;
    int lp_yytype;
    YYSTYPE const * const lp_yyvaluep;
#endif
{
  if (!lp_yyvaluep)
    return;
# ifdef YYPRINT
  if (lp_yytype < YYNTOKENS)
    YYPRINT (lp_yyoutput, lp_yytoknum[lp_yytype], *lp_yyvaluep);
# else
  YYUSE (lp_yyoutput);
# endif
  switch (lp_yytype)
    {
      default:
	break;
    }
}


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
lp_yy_symbol_print (FILE *lp_yyoutput, int lp_yytype, YYSTYPE const * const lp_yyvaluep)
#else
static void
lp_yy_symbol_print (lp_yyoutput, lp_yytype, lp_yyvaluep)
    FILE *lp_yyoutput;
    int lp_yytype;
    YYSTYPE const * const lp_yyvaluep;
#endif
{
  if (lp_yytype < YYNTOKENS)
    YYFPRINTF (lp_yyoutput, "token %s (", lp_yytname[lp_yytype]);
  else
    YYFPRINTF (lp_yyoutput, "nterm %s (", lp_yytname[lp_yytype]);

  lp_yy_symbol_value_print (lp_yyoutput, lp_yytype, lp_yyvaluep);
  YYFPRINTF (lp_yyoutput, ")");
}

/*------------------------------------------------------------------.
| lp_yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
lp_yy_stack_print (lp_yytype_int16 *bottom, lp_yytype_int16 *top)
#else
static void
lp_yy_stack_print (bottom, top)
    lp_yytype_int16 *bottom;
    lp_yytype_int16 *top;
#endif
{
  YYFPRINTF (stderr, "Stack now");
  for (; bottom <= top; ++bottom)
    YYFPRINTF (stderr, " %d", *bottom);
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)				\
do {								\
  if (lp_yydebug)							\
    lp_yy_stack_print ((Bottom), (Top));				\
} while (YYID (0))


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
lp_yy_reduce_print (YYSTYPE *lp_yyvsp, int lp_yyrule)
#else
static void
lp_yy_reduce_print (lp_yyvsp, lp_yyrule)
    YYSTYPE *lp_yyvsp;
    int lp_yyrule;
#endif
{
  int lp_yynrhs = lp_yyr2[lp_yyrule];
  int lp_yyi;
  unsigned long int lp_yylno = lp_yyrline[lp_yyrule];
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %lu):\n",
	     lp_yyrule - 1, lp_yylno);
  /* The symbols being reduced.  */
  for (lp_yyi = 0; lp_yyi < lp_yynrhs; lp_yyi++)
    {
      fprintf (stderr, "   $%d = ", lp_yyi + 1);
      lp_yy_symbol_print (stderr, lp_yyrhs[lp_yyprhs[lp_yyrule] + lp_yyi],
		       &(lp_yyvsp[(lp_yyi + 1) - (lp_yynrhs)])
		       		       );
      fprintf (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)		\
do {					\
  if (lp_yydebug)				\
    lp_yy_reduce_print (lp_yyvsp, Rule); \
} while (YYID (0))

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int lp_yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
# define YY_SYMBOL_PRINT(Title, Type, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef	YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif



#if YYERROR_VERBOSE

# ifndef lp_yystrlen
#  if defined __GLIBC__ && defined _STRING_H
#   define lp_yystrlen strlen
#  else
/* Return the length of YYSTR.  */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static YYSIZE_T
lp_yystrlen (const char *lp_yystr)
#else
static YYSIZE_T
lp_yystrlen (lp_yystr)
    const char *lp_yystr;
#endif
{
  YYSIZE_T lp_yylen;
  for (lp_yylen = 0; lp_yystr[lp_yylen]; lp_yylen++)
    continue;
  return lp_yylen;
}
#  endif
# endif

# ifndef lp_yystpcpy
#  if defined __GLIBC__ && defined _STRING_H && defined _GNU_SOURCE
#   define lp_yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static char *
lp_yystpcpy (char *lp_yydest, const char *lp_yysrc)
#else
static char *
lp_yystpcpy (lp_yydest, lp_yysrc)
    char *lp_yydest;
    const char *lp_yysrc;
#endif
{
  char *lp_yyd = lp_yydest;
  const char *lp_yys = lp_yysrc;

  while ((*lp_yyd++ = *lp_yys++) != '\0')
    continue;

  return lp_yyd - 1;
}
#  endif
# endif

# ifndef lp_yytnamerr
/* Copy to YYRES the contents of YYSTR after stripping away unnecessary
   quotes and backslashes, so that it's suitable for lp_yyerror.  The
   heuristic is that double-quoting is unnecessary unless the string
   contains an apostrophe, a comma, or backslash (other than
   backslash-backslash).  YYSTR is taken from lp_yytname.  If YYRES is
   null, do not copy; instead, return the length of what the result
   would have been.  */
static YYSIZE_T
lp_yytnamerr (char *lp_yyres, const char *lp_yystr)
{
  if (*lp_yystr == '"')
    {
      YYSIZE_T lp_yyn = 0;
      char const *lp_yyp = lp_yystr;

      for (;;)
	switch (*++lp_yyp)
	  {
	  case '\'':
	  case ',':
	    goto do_not_strip_quotes;

	  case '\\':
	    if (*++lp_yyp != '\\')
	      goto do_not_strip_quotes;
	    /* Fall through.  */
	  default:
	    if (lp_yyres)
	      lp_yyres[lp_yyn] = *lp_yyp;
	    lp_yyn++;
	    break;

	  case '"':
	    if (lp_yyres)
	      lp_yyres[lp_yyn] = '\0';
	    return lp_yyn;
	  }
    do_not_strip_quotes: ;
    }

  if (! lp_yyres)
    return lp_yystrlen (lp_yystr);

  return lp_yystpcpy (lp_yyres, lp_yystr) - lp_yyres;
}
# endif

/* Copy into YYRESULT an error message about the unexpected token
   YYCHAR while in state YYSTATE.  Return the number of bytes copied,
   including the terminating null byte.  If YYRESULT is null, do not
   copy anything; just return the number of bytes that would be
   copied.  As a special case, return 0 if an ordinary "syntax error"
   message will do.  Return YYSIZE_MAXIMUM if overflow occurs during
   size calculation.  */
static YYSIZE_T
lp_yysyntax_error (char *lp_yyresult, int lp_yystate, int lp_yychar)
{
  int lp_yyn = lp_yypact[lp_yystate];

  if (! (YYPACT_NINF < lp_yyn && lp_yyn <= YYLAST))
    return 0;
  else
    {
      int lp_yytype = YYTRANSLATE (lp_yychar);
      YYSIZE_T lp_yysize0 = lp_yytnamerr (0, lp_yytname[lp_yytype]);
      YYSIZE_T lp_yysize = lp_yysize0;
      YYSIZE_T lp_yysize1;
      int lp_yysize_overflow = 0;
      enum { YYERROR_VERBOSE_ARGS_MAXIMUM = 5 };
      char const *lp_yyarg[YYERROR_VERBOSE_ARGS_MAXIMUM];
      int lp_yyx;

# if 0
      /* This is so xgettext sees the translatable formats that are
	 constructed on the fly.  */
      YY_("syntax error, unexpected %s");
      YY_("syntax error, unexpected %s, expecting %s");
      YY_("syntax error, unexpected %s, expecting %s or %s");
      YY_("syntax error, unexpected %s, expecting %s or %s or %s");
      YY_("syntax error, unexpected %s, expecting %s or %s or %s or %s");
# endif
      char *lp_yyfmt;
      char const *lp_yyf;
      static char const lp_yyunexpected[] = "syntax error, unexpected %s";
      static char const lp_yyexpecting[] = ", expecting %s";
      static char const lp_yyor[] = " or %s";
      char lp_yyformat[sizeof lp_yyunexpected
		    + sizeof lp_yyexpecting - 1
		    + ((YYERROR_VERBOSE_ARGS_MAXIMUM - 2)
		       * (sizeof lp_yyor - 1))];
      char const *lp_yyprefix = lp_yyexpecting;

      /* Start YYX at -YYN if negative to avoid negative indexes in
	 YYCHECK.  */
      int lp_yyxbegin = lp_yyn < 0 ? -lp_yyn : 0;

      /* Stay within bounds of both lp_yycheck and lp_yytname.  */
      int lp_yychecklim = YYLAST - lp_yyn + 1;
      int lp_yyxend = lp_yychecklim < YYNTOKENS ? lp_yychecklim : YYNTOKENS;
      int lp_yycount = 1;

      lp_yyarg[0] = lp_yytname[lp_yytype];
      lp_yyfmt = lp_yystpcpy (lp_yyformat, lp_yyunexpected);

      for (lp_yyx = lp_yyxbegin; lp_yyx < lp_yyxend; ++lp_yyx)
	if (lp_yycheck[lp_yyx + lp_yyn] == lp_yyx && lp_yyx != YYTERROR)
	  {
	    if (lp_yycount == YYERROR_VERBOSE_ARGS_MAXIMUM)
	      {
		lp_yycount = 1;
		lp_yysize = lp_yysize0;
		lp_yyformat[sizeof lp_yyunexpected - 1] = '\0';
		break;
	      }
	    lp_yyarg[lp_yycount++] = lp_yytname[lp_yyx];
	    lp_yysize1 = lp_yysize + lp_yytnamerr (0, lp_yytname[lp_yyx]);
	    lp_yysize_overflow |= (lp_yysize1 < lp_yysize);
	    lp_yysize = lp_yysize1;
	    lp_yyfmt = lp_yystpcpy (lp_yyfmt, lp_yyprefix);
	    lp_yyprefix = lp_yyor;
	  }

      lp_yyf = YY_(lp_yyformat);
      lp_yysize1 = lp_yysize + lp_yystrlen (lp_yyf);
      lp_yysize_overflow |= (lp_yysize1 < lp_yysize);
      lp_yysize = lp_yysize1;

      if (lp_yysize_overflow)
	return YYSIZE_MAXIMUM;

      if (lp_yyresult)
	{
	  /* Avoid sprintf, as that infringes on the user's name space.
	     Don't have undefined behavior even if the translation
	     produced a string with the wrong number of "%s"s.  */
	  char *lp_yyp = lp_yyresult;
	  int lp_yyi = 0;
	  while ((*lp_yyp = *lp_yyf) != '\0')
	    {
	      if (*lp_yyp == '%' && lp_yyf[1] == 's' && lp_yyi < lp_yycount)
		{
		  lp_yyp += lp_yytnamerr (lp_yyp, lp_yyarg[lp_yyi++]);
		  lp_yyf += 2;
		}
	      else
		{
		  lp_yyp++;
		  lp_yyf++;
		}
	    }
	}
      return lp_yysize;
    }
}
#endif /* YYERROR_VERBOSE */


/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

/*ARGSUSED*/
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
static void
lp_yydestruct (const char *lp_yymsg, int lp_yytype, YYSTYPE *lp_yyvaluep)
#else
static void
lp_yydestruct (lp_yymsg, lp_yytype, lp_yyvaluep)
    const char *lp_yymsg;
    int lp_yytype;
    YYSTYPE *lp_yyvaluep;
#endif
{
  YYUSE (lp_yyvaluep);

  if (!lp_yymsg)
    lp_yymsg = "Deleting";
  YY_SYMBOL_PRINT (lp_yymsg, lp_yytype, lp_yyvaluep, lp_yylocationp);

  switch (lp_yytype)
    {

      default:
	break;
    }
}


/* Prevent warnings from -Wmissing-prototypes.  */

#ifdef YYPARSE_PARAM
#if defined __STDC__ || defined __cplusplus
int lp_yyparse (void *YYPARSE_PARAM);
#else
int lp_yyparse ();
#endif
#else /* ! YYPARSE_PARAM */
#if defined __STDC__ || defined __cplusplus
int lp_yyparse (void);
#else
int lp_yyparse ();
#endif
#endif /* ! YYPARSE_PARAM */



/* The look-ahead symbol.  */
int lp_yychar;

/* The semantic value of the look-ahead symbol.  */
YYSTYPE lp_yylval;

/* Number of syntax errors so far.  */
int lp_yynerrs;



/*----------.
| lp_yyparse.  |
`----------*/

#ifdef YYPARSE_PARAM
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
int
lp_yyparse (void *YYPARSE_PARAM)
#else
int
lp_yyparse (YYPARSE_PARAM)
    void *YYPARSE_PARAM;
#endif
#else /* ! YYPARSE_PARAM */
#if (defined __STDC__ || defined __C99__FUNC__ \
     || defined __cplusplus || defined _MSC_VER)
int
lp_yyparse (void)
#else
int
lp_yyparse ()

#endif
#endif
{
  
  int lp_yystate;
  int lp_yyn;
  int lp_yyresult;
  /* Number of tokens to shift before error messages enabled.  */
  int lp_yyerrstatus;
  /* Look-ahead token as an internal (translated) token number.  */
  int lp_yytoken = 0;
#if YYERROR_VERBOSE
  /* Buffer for error messages, and its allocated size.  */
  char lp_yymsgbuf[128];
  char *lp_yymsg = lp_yymsgbuf;
  YYSIZE_T lp_yymsg_alloc = sizeof lp_yymsgbuf;
#endif

  /* Three stacks and their tools:
     `lp_yyss': related to states,
     `lp_yyvs': related to semantic values,
     `lp_yyls': related to locations.

     Refer to the stacks thru separate pointers, to allow lp_yyoverflow
     to reallocate them elsewhere.  */

  /* The state stack.  */
  lp_yytype_int16 lp_yyssa[YYINITDEPTH];
  lp_yytype_int16 *lp_yyss = lp_yyssa;
  lp_yytype_int16 *lp_yyssp;

  /* The semantic value stack.  */
  YYSTYPE lp_yyvsa[YYINITDEPTH];
  YYSTYPE *lp_yyvs = lp_yyvsa;
  YYSTYPE *lp_yyvsp;



#define YYPOPSTACK(N)   (lp_yyvsp -= (N), lp_yyssp -= (N))

  YYSIZE_T lp_yystacksize = YYINITDEPTH;

  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE lp_yyval;


  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int lp_yylen = 0;

  YYDPRINTF ((stderr, "Starting parse\n"));

  lp_yystate = 0;
  lp_yyerrstatus = 0;
  lp_yynerrs = 0;
  lp_yychar = YYEMPTY;		/* Cause a token to be read.  */

  /* Initialize stack pointers.
     Waste one element of value and location stack
     so that they stay on the same level as the state stack.
     The wasted elements are never initialized.  */

  lp_yyssp = lp_yyss;
  lp_yyvsp = lp_yyvs;

  goto lp_yysetstate;

/*------------------------------------------------------------.
| lp_yynewstate -- Push a new state, which is found in lp_yystate.  |
`------------------------------------------------------------*/
 lp_yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  lp_yyssp++;

 lp_yysetstate:
  *lp_yyssp = lp_yystate;

  if (lp_yyss + lp_yystacksize - 1 <= lp_yyssp)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T lp_yysize = lp_yyssp - lp_yyss + 1;

#ifdef lp_yyoverflow
      {
	/* Give user a chance to reallocate the stack.  Use copies of
	   these so that the &'s don't force the real ones into
	   memory.  */
	YYSTYPE *lp_yyvs1 = lp_yyvs;
	lp_yytype_int16 *lp_yyss1 = lp_yyss;


	/* Each stack pointer address is followed by the size of the
	   data in use in that stack, in bytes.  This used to be a
	   conditional around just the two extra args, but that might
	   be undefined if lp_yyoverflow is a macro.  */
	lp_yyoverflow (YY_("memory exhausted"),
		    &lp_yyss1, lp_yysize * sizeof (*lp_yyssp),
		    &lp_yyvs1, lp_yysize * sizeof (*lp_yyvsp),

		    &lp_yystacksize);

	lp_yyss = lp_yyss1;
	lp_yyvs = lp_yyvs1;
      }
#else /* no lp_yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto lp_yyexhaustedlab;
# else
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= lp_yystacksize)
	goto lp_yyexhaustedlab;
      lp_yystacksize *= 2;
      if (YYMAXDEPTH < lp_yystacksize)
	lp_yystacksize = YYMAXDEPTH;

      {
	lp_yytype_int16 *lp_yyss1 = lp_yyss;
	union lp_yyalloc *lp_yyptr =
	  (union lp_yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (lp_yystacksize));
	if (! lp_yyptr)
	  goto lp_yyexhaustedlab;
	YYSTACK_RELOCATE (lp_yyss);
	YYSTACK_RELOCATE (lp_yyvs);

#  undef YYSTACK_RELOCATE
	if (lp_yyss1 != lp_yyssa)
	  YYSTACK_FREE (lp_yyss1);
      }
# endif
#endif /* no lp_yyoverflow */

      lp_yyssp = lp_yyss + lp_yysize - 1;
      lp_yyvsp = lp_yyvs + lp_yysize - 1;


      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
		  (unsigned long int) lp_yystacksize));

      if (lp_yyss + lp_yystacksize - 1 <= lp_yyssp)
	YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", lp_yystate));

  goto lp_yybackup;

/*-----------.
| lp_yybackup.  |
`-----------*/
lp_yybackup:

  /* Do appropriate processing given the current state.  Read a
     look-ahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to look-ahead token.  */
  lp_yyn = lp_yypact[lp_yystate];
  if (lp_yyn == YYPACT_NINF)
    goto lp_yydefault;

  /* Not known => get a look-ahead token if don't already have one.  */

  /* YYCHAR is either YYEMPTY or YYEOF or a valid look-ahead symbol.  */
  if (lp_yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      lp_yychar = YYLEX;
    }

  if (lp_yychar <= YYEOF)
    {
      lp_yychar = lp_yytoken = YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      lp_yytoken = YYTRANSLATE (lp_yychar);
      YY_SYMBOL_PRINT ("Next token is", lp_yytoken, &lp_yylval, &lp_yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  lp_yyn += lp_yytoken;
  if (lp_yyn < 0 || YYLAST < lp_yyn || lp_yycheck[lp_yyn] != lp_yytoken)
    goto lp_yydefault;
  lp_yyn = lp_yytable[lp_yyn];
  if (lp_yyn <= 0)
    {
      if (lp_yyn == 0 || lp_yyn == YYTABLE_NINF)
	goto lp_yyerrlab;
      lp_yyn = -lp_yyn;
      goto lp_yyreduce;
    }

  if (lp_yyn == YYFINAL)
    YYACCEPT;

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (lp_yyerrstatus)
    lp_yyerrstatus--;

  /* Shift the look-ahead token.  */
  YY_SYMBOL_PRINT ("Shifting", lp_yytoken, &lp_yylval, &lp_yylloc);

  /* Discard the shifted token unless it is eof.  */
  if (lp_yychar != YYEOF)
    lp_yychar = YYEMPTY;

  lp_yystate = lp_yyn;
  *++lp_yyvsp = lp_yylval;

  goto lp_yynewstate;


/*-----------------------------------------------------------.
| lp_yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
lp_yydefault:
  lp_yyn = lp_yydefact[lp_yystate];
  if (lp_yyn == 0)
    goto lp_yyerrlab;
  goto lp_yyreduce;


/*-----------------------------.
| lp_yyreduce -- Do a reduction.  |
`-----------------------------*/
lp_yyreduce:
  /* lp_yyn is the number of a rule to reduce with.  */
  lp_yylen = lp_yyr2[lp_yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     `$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  lp_yyval = lp_yyvsp[1-lp_yylen];


  YY_REDUCE_PRINT (lp_yyn);
  switch (lp_yyn)
    {
        case 2:
#line 67 "lp.y"
    {
  isign = 0;
  make_neg = 0;
  Sign = 0;
  HadConstraint = FALSE;
  HadVar = HadVar0 = FALSE;
}
    break;

  case 9:
#line 90 "lp.y"
    {
  if(!add_constraint_name(Last_var))
    YYABORT;
  HadConstraint = TRUE;
}
    break;

  case 13:
#line 102 "lp.y"
    {
  HadVar1 = HadVar0;
  HadVar0 = FALSE;
}
    break;

  case 14:
#line 107 "lp.y"
    {
  if(!store_re_op((char *) lp_yytext, HadConstraint, HadVar, Had_lineair_sum))
    YYABORT;
  make_neg = 1;
  f1 = 0;
}
    break;

  case 15:
#line 114 "lp.y"
    {
  Had_lineair_sum0 = Had_lineair_sum;
  Had_lineair_sum = TRUE;
  HadVar2 = HadVar0;
  HadVar0 = FALSE;
  do_add_row = FALSE;
  if(HadConstraint && !HadVar ) {
    /* it is a range */
    /* already handled */
  }
  else if(!HadConstraint && HadVar) {
    /* it is a bound */

    if(!store_bounds(TRUE))
      YYABORT;
  }
  else {
    /* it is a row restriction */
    do_add_row = TRUE;
  }
}
    break;

  case 16:
#line 137 "lp.y"
    {
  if((!HadVar) && (!HadConstraint)) {
    lp_yyerror("parse error");
    YYABORT;
  }
  if(do_add_row)
    add_row();
  HadConstraint = FALSE;
  HadVar = HadVar0 = FALSE;
  isign = 0;
  make_neg = 0;
  null_tmp_store(TRUE);
}
    break;

  case 17:
#line 153 "lp.y"
    {
  if((!HadVar1) && (Had_lineair_sum0))
    if(!negate_constraint())
      YYABORT;
}
    break;

  case 18:
#line 159 "lp.y"
    {
  make_neg = 0;
  isign = 0;
  if(HadConstraint)
    HadVar = Had_lineair_sum = FALSE;
  HadVar0 = FALSE;
  if(!store_re_op((*lp_yytext == '<') ? ">" : (*lp_yytext == '>') ? "<" : (char *) lp_yytext, HadConstraint, HadVar, Had_lineair_sum))
    YYABORT;
}
    break;

  case 19:
#line 169 "lp.y"
    {
  f -= f1;
}
    break;

  case 20:
#line 173 "lp.y"
    {
  if((HadVar1) || (!HadVar2) || (HadVar0)) {
    lp_yyerror("parse error");
    YYABORT;
  }

  if(HadConstraint && !HadVar ) {
    /* it is a range */
    /* already handled */
    if(!negate_constraint())
      YYABORT;
  }
  else if(!HadConstraint && HadVar) {
    /* it is a bound */

    if(!store_bounds(TRUE))
      YYABORT;
  }
}
    break;

  case 22:
#line 196 "lp.y"
    {
  isign = Sign;
}
    break;

  case 25:
#line 205 "lp.y"
    {
  isign = Sign;
}
    break;

  case 33:
#line 223 "lp.y"
    {
  Within_sos_decl1 = Within_sos_decl;
}
    break;

  case 35:
#line 230 "lp.y"
    {
  if((!Within_int_decl) && (!Within_sec_decl) && (!Within_sos_decl1)) {
    lp_yyerror("parse error");
    YYABORT;
  }
  SOStype = SOStype0;
  check_int_sec_sos_decl(Within_int_decl, Within_sec_decl, Within_sos_decl1 = (Within_sos_decl1 ? 1 : 0));
}
    break;

  case 36:
#line 242 "lp.y"
    {
  if((Within_sos_decl1) && (SOStype == 0))
  {
    lp_yyerror("Unsupported SOS type (0)");
    YYABORT;
  }
}
    break;

  case 40:
#line 258 "lp.y"
    {
  strcpy(Last_var0, Last_var);
}
    break;

  case 42:
#line 265 "lp.y"
    {
  if(Within_sos_decl1) {
    set_sos_type(SOStype);
    set_sos_weight(SOSweight, 1);
  }
}
    break;

  case 43:
#line 273 "lp.y"
    {
  if((Within_sos_decl1) && (!SOStype))
  {
    set_sos_type(SOStype = (short) (f + .1));
  }
  else
  {
    lp_yyerror("SOS type not expected");
    YYABORT;
  }
}
    break;

  case 45:
#line 288 "lp.y"
    {
  set_sos_weight(SOSweight, 1);
}
    break;

  case 46:
#line 293 "lp.y"
    {
  set_sos_weight((int) (f + .1), 1);
}
    break;

  case 53:
#line 313 "lp.y"
    { /* peno1 */
  if(Within_sos_decl1 == 1)
  {
    char buf[16];

    SOSweight++;
    sprintf(buf, "SOS%d", SOSweight);
    storevarandweight(buf);

    check_int_sec_sos_decl(Within_int_decl, Within_sec_decl, 2);
    Within_sos_decl1 = 2;
    weight = 0;
    SOSNr = 0;
  }

  storevarandweight(Last_var);

  if(Within_sos_decl1 == 2)
  {
    SOSNr++;
    weight = SOSNr;
    set_sos_weight(weight, 2);
  }
}
    break;

  case 54:
#line 340 "lp.y"
    { /* peno2 */
  if(!Within_sos_decl1) {
    lp_yyerror("parse error");
    YYABORT;
  }
  if(Within_sos_decl1 == 1)
    strcpy(Last_var0, Last_var);
  if(Within_sos_decl1 == 2)
  {
    storevarandweight(Last_var);  
    SOSNr++;
    weight = SOSNr;
    set_sos_weight(weight, 2);
  }
}
    break;

  case 55:
#line 358 "lp.y"
    { /* peno3 */
  if(Within_sos_decl1 == 1)
  {
    char buf[16];

    SOSweight++;
    sprintf(buf, "SOS%d", SOSweight);
    storevarandweight(buf);

    check_int_sec_sos_decl(Within_int_decl, Within_sec_decl, 2);
    Within_sos_decl1 = 2;
    weight = 0;
    SOSNr = 0;

    storevarandweight(Last_var0);  
    SOSNr++;
  }

  weight = (int) (f + .1);
  set_sos_weight(weight, 2);
}
    break;

  case 56:
#line 382 "lp.y"
    { /* SOS name */ /* peno4 */
  if(Within_sos_decl1 == 1)
  {
    storevarandweight(Last_var0);
    set_sos_type(SOStype);
    check_int_sec_sos_decl(Within_int_decl, Within_sec_decl, 2);
    Within_sos_decl1 = 2;
    weight = 0;
    SOSNr = 0;
    SOSweight++;
  }
}
    break;

  case 63:
#line 420 "lp.y"
    {
  state0 = 0;
}
    break;

  case 64:
#line 424 "lp.y"
    {
  if (state == 1) {
    /* RHS_STORE */
    if (    (isign0 || !make_neg)
        && !(isign0 && !make_neg)) /* but not both! */
      f0 = -f0;
    if(make_neg)
      f1 += f0;
    if(!rhs_store(f0, HadConstraint, HadVar, Had_lineair_sum))
      YYABORT;
  }
}
    break;

  case 69:
#line 447 "lp.y"
    {
  state = 1;
}
    break;

  case 70:
#line 452 "lp.y"
    {
  state = 2;
}
    break;

  case 71:
#line 459 "lp.y"
    {
  if ((HadSign || state == 1) && (state0 == 1)) {
    /* RHS_STORE */
    if (    (isign0 || !make_neg)
        && !(isign0 && !make_neg)) /* but not both! */
      f0 = -f0;
    if(make_neg)
      f1 += f0;
    if(!rhs_store(f0, HadConstraint, HadVar, Had_lineair_sum))
      YYABORT;
  }
  if (state == 1) {
    f0 = f;
    isign0 = isign;
  }
  if (state == 2) {
    if((HadSign) || (state0 != 1)) {
     isign0 = isign;
     f0 = 1.0;
    }
    /* VAR_STORE */
    if (    (isign0 || make_neg)
        && !(isign0 && make_neg)) /* but not both! */
      f0 = -f0;
    if(!var_store(Last_var, f0, HadConstraint, HadVar, Had_lineair_sum)) {
      lp_yyerror("var_store failed");
      YYABORT;
    }
    HadConstraint |= HadVar;
    HadVar = HadVar0 = TRUE;
  }
  state0 = state;
}
    break;

  case 74:
#line 502 "lp.y"
    {
  isign = 0;
  HadSign = FALSE;
}
    break;

  case 75:
#line 507 "lp.y"
    {
  isign = Sign;
  HadSign = TRUE;
}
    break;

  case 76:
#line 514 "lp.y"
    {
  f = 1.0;
}
    break;

  case 81:
#line 529 "lp.y"
    {
  if (    (isign || make_neg)
      && !(isign && make_neg)) /* but not both! */
    f = -f;
  if(!var_store(Last_var, f, HadConstraint, HadVar, Had_lineair_sum)) {
    lp_yyerror("var_store failed");
    YYABORT;
  }
  HadConstraint |= HadVar;
  HadVar = HadVar0 = TRUE;
  isign = 0;
}
    break;

  case 83:
#line 547 "lp.y"
    {
  /* to allow a range */
  /* constraint: < max */
  if(!HadConstraint) {
    lp_yyerror("parse error");
    YYABORT;
  }
  Had_lineair_sum = FALSE;
}
    break;

  case 84:
#line 557 "lp.y"
    {
  Had_lineair_sum = TRUE;
}
    break;

  case 85:
#line 563 "lp.y"
    {
  set_obj_dir(TRUE);
}
    break;

  case 86:
#line 567 "lp.y"
    {
  set_obj_dir(FALSE);
}
    break;

  case 88:
#line 575 "lp.y"
    {
  add_row();
  HadConstraint = FALSE;
  HadVar = HadVar0 = FALSE;
  isign = 0;
  make_neg = 0;
}
    break;

  case 91:
#line 589 "lp.y"
    {
  if (    (isign || !make_neg)
      && !(isign && !make_neg)) /* but not both! */
    f = -f;
  if(!rhs_store(f, HadConstraint, HadVar, Had_lineair_sum))
    YYABORT;
  isign = 0;
}
    break;


/* Line 1267 of yacc.c.  */
#line 2000 "y.tab.c"
      default: break;
    }
  YY_SYMBOL_PRINT ("-> $$ =", lp_yyr1[lp_yyn], &lp_yyval, &lp_yyloc);

  YYPOPSTACK (lp_yylen);
  lp_yylen = 0;
  YY_STACK_PRINT (lp_yyss, lp_yyssp);

  *++lp_yyvsp = lp_yyval;


  /* Now `shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  lp_yyn = lp_yyr1[lp_yyn];

  lp_yystate = lp_yypgoto[lp_yyn - YYNTOKENS] + *lp_yyssp;
  if (0 <= lp_yystate && lp_yystate <= YYLAST && lp_yycheck[lp_yystate] == *lp_yyssp)
    lp_yystate = lp_yytable[lp_yystate];
  else
    lp_yystate = lp_yydefgoto[lp_yyn - YYNTOKENS];

  goto lp_yynewstate;


/*------------------------------------.
| lp_yyerrlab -- here on detecting error |
`------------------------------------*/
lp_yyerrlab:
  /* If not already recovering from an error, report this error.  */
  if (!lp_yyerrstatus)
    {
      ++lp_yynerrs;
#if ! YYERROR_VERBOSE
      lp_yyerror (YY_("syntax error"));
#else
      {
	YYSIZE_T lp_yysize = lp_yysyntax_error (0, lp_yystate, lp_yychar);
	if (lp_yymsg_alloc < lp_yysize && lp_yymsg_alloc < YYSTACK_ALLOC_MAXIMUM)
	  {
	    YYSIZE_T lp_yyalloc = 2 * lp_yysize;
	    if (! (lp_yysize <= lp_yyalloc && lp_yyalloc <= YYSTACK_ALLOC_MAXIMUM))
	      lp_yyalloc = YYSTACK_ALLOC_MAXIMUM;
	    if (lp_yymsg != lp_yymsgbuf)
	      YYSTACK_FREE (lp_yymsg);
	    lp_yymsg = (char *) YYSTACK_ALLOC (lp_yyalloc);
	    if (lp_yymsg)
	      lp_yymsg_alloc = lp_yyalloc;
	    else
	      {
		lp_yymsg = lp_yymsgbuf;
		lp_yymsg_alloc = sizeof lp_yymsgbuf;
	      }
	  }

	if (0 < lp_yysize && lp_yysize <= lp_yymsg_alloc)
	  {
	    (void) lp_yysyntax_error (lp_yymsg, lp_yystate, lp_yychar);
	    lp_yyerror (lp_yymsg);
	  }
	else
	  {
	    lp_yyerror (YY_("syntax error"));
	    if (lp_yysize != 0)
	      goto lp_yyexhaustedlab;
	  }
      }
#endif
    }



  if (lp_yyerrstatus == 3)
    {
      /* If just tried and failed to reuse look-ahead token after an
	 error, discard it.  */

      if (lp_yychar <= YYEOF)
	{
	  /* Return failure if at end of input.  */
	  if (lp_yychar == YYEOF)
	    YYABORT;
	}
      else
	{
	  lp_yydestruct ("Error: discarding",
		      lp_yytoken, &lp_yylval);
	  lp_yychar = YYEMPTY;
	}
    }

  /* Else will try to reuse look-ahead token after shifting the error
     token.  */
  goto lp_yyerrlab1;


/*---------------------------------------------------.
| lp_yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
lp_yyerrorlab:

  /* Pacify compilers like GCC when the user code never invokes
     YYERROR and the label lp_yyerrorlab therefore never appears in user
     code.  */
  if (/*CONSTCOND*/ 0)
     goto lp_yyerrorlab;

  /* Do not reclaim the symbols of the rule which action triggered
     this YYERROR.  */
  YYPOPSTACK (lp_yylen);
  lp_yylen = 0;
  YY_STACK_PRINT (lp_yyss, lp_yyssp);
  lp_yystate = *lp_yyssp;
  goto lp_yyerrlab1;


/*-------------------------------------------------------------.
| lp_yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
lp_yyerrlab1:
  lp_yyerrstatus = 3;	/* Each real token shifted decrements this.  */

  for (;;)
    {
      lp_yyn = lp_yypact[lp_yystate];
      if (lp_yyn != YYPACT_NINF)
	{
	  lp_yyn += YYTERROR;
	  if (0 <= lp_yyn && lp_yyn <= YYLAST && lp_yycheck[lp_yyn] == YYTERROR)
	    {
	      lp_yyn = lp_yytable[lp_yyn];
	      if (0 < lp_yyn)
		break;
	    }
	}

      /* Pop the current state because it cannot handle the error token.  */
      if (lp_yyssp == lp_yyss)
	YYABORT;


      lp_yydestruct ("Error: popping",
		  lp_yystos[lp_yystate], lp_yyvsp);
      YYPOPSTACK (1);
      lp_yystate = *lp_yyssp;
      YY_STACK_PRINT (lp_yyss, lp_yyssp);
    }

  if (lp_yyn == YYFINAL)
    YYACCEPT;

  *++lp_yyvsp = lp_yylval;


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", lp_yystos[lp_yyn], lp_yyvsp, lp_yylsp);

  lp_yystate = lp_yyn;
  goto lp_yynewstate;


/*-------------------------------------.
| lp_yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
lp_yyacceptlab:
  lp_yyresult = 0;
  goto lp_yyreturn;

/*-----------------------------------.
| lp_yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
lp_yyabortlab:
  lp_yyresult = 1;
  goto lp_yyreturn;

#ifndef lp_yyoverflow
/*-------------------------------------------------.
| lp_yyexhaustedlab -- memory exhaustion comes here.  |
`-------------------------------------------------*/
lp_yyexhaustedlab:
  lp_yyerror (YY_("memory exhausted"));
  lp_yyresult = 2;
  /* Fall through.  */
#endif

lp_yyreturn:
  if (lp_yychar != YYEOF && lp_yychar != YYEMPTY)
     lp_yydestruct ("Cleanup: discarding lookahead",
		 lp_yytoken, &lp_yylval);
  /* Do not reclaim the symbols of the rule which action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (lp_yylen);
  YY_STACK_PRINT (lp_yyss, lp_yyssp);
  while (lp_yyssp != lp_yyss)
    {
      lp_yydestruct ("Cleanup: popping",
		  lp_yystos[*lp_yyssp], lp_yyvsp);
      YYPOPSTACK (1);
    }
#ifndef lp_yyoverflow
  if (lp_yyss != lp_yyssa)
    YYSTACK_FREE (lp_yyss);
#endif
#if YYERROR_VERBOSE
  if (lp_yymsg != lp_yymsgbuf)
    YYSTACK_FREE (lp_yymsg);
#endif
  /* Make sure YYID is used.  */
  return YYID (lp_yyresult);
}


#line 599 "lp.y"


static void lp_yy_delete_allocated_memory(void)
{
  /* free memory allocated by flex. Otherwise some memory is not freed.
     This is a bit tricky. There is not much documentation about this, but a lot of
     reports of memory that keeps allocated */

  /* If you get errors on this function call, just comment it. This will only result
     in some memory that is not being freed. */

# if defined YY_CURRENT_BUFFER
    /* flex defines the macro YY_CURRENT_BUFFER, so you should only get here if lex.c is
       generated by flex */
    /* lex doesn't define this macro and thus should not come here, but lex doesn't has
       this memory leak also ...*/

    lp_yy_delete_buffer(YY_CURRENT_BUFFER); /* comment this line if you have problems with it */
    lp_yy_init = 1; /* make sure that the next time memory is allocated again */
    lp_yy_start = 0;
# endif
}

static int parse(void)
{
  return(lp_yyparse());
}

lprec *read_lp(FILE *input, short verbose, char *lp_name)
{
  lp_yyin = input;
  return(yacc_read(verbose, lp_name, &lp_yylineno, parse, lp_yy_delete_allocated_memory));
}

lprec *read_LP(char *input, short verbose, char *lp_name)
{
  FILE *fpin;
  lprec *lp = NULL;

  if((fpin = fopen(input, "r")) != NULL) {
    lp = read_lp(fpin, verbose, lp_name);
    fclose(fpin);
  }
  return(lp);
}


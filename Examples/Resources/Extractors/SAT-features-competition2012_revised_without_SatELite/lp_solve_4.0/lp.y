/* ========================================================================= */
/* NAME  : lp.y                                                              */
/* ========================================================================= */


%token VAR CONS INTCONS VARIABLECOLON INF SEC_INT SEC_SEC SEC_SOS SOSDESCR SIGN AR_M_OP RE_OPLE RE_OPGE END_C COMMA COLON MINIMISE MAXIMISE UNDEFINED


%{
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

#define yywrap wrap
#define yyerror read_error

#include "lex.c"

%}

%start inputfile
%%

inputfile       :
{
  isign = 0;
  make_neg = 0;
  Sign = 0;
  HadConstraint = FALSE;
  HadVar = HadVar0 = FALSE;
}
                  objective_function
                  constraints
                  int_sec_sos_declarations
                ;

constraints:    /* EMPTY */
                | x_constraints
                ;

x_constraints   : constraint
                | x_constraints
                  constraint
                ;

constraint      : real_constraint
                | VARIABLECOLON
{
  if(!add_constraint_name(Last_var))
    YYABORT;
  HadConstraint = TRUE;
}
                  real_constraint
                ;

RE_OP: RE_OPLE | RE_OPGE
                ;

real_constraint : xx_lineair_sum
{
  HadVar1 = HadVar0;
  HadVar0 = FALSE;
}
                  RE_OP
{
  if(!store_re_op((char *) yytext, HadConstraint, HadVar, Had_lineair_sum))
    YYABORT;
  make_neg = 1;
  f1 = 0;
}
                  xxx_lineair_sum
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
                  optionalrange
                  END_C
{
  if((!HadVar) && (!HadConstraint)) {
    yyerror("parse error");
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
                ;

optionalrange: /* EMPTY */
{
  if((!HadVar1) && (Had_lineair_sum0))
    if(!negate_constraint())
      YYABORT;
}
                | RE_OP
{
  make_neg = 0;
  isign = 0;
  if(HadConstraint)
    HadVar = Had_lineair_sum = FALSE;
  HadVar0 = FALSE;
  if(!store_re_op((*yytext == '<') ? ">" : (*yytext == '>') ? "<" : (char *) yytext, HadConstraint, HadVar, Had_lineair_sum))
    YYABORT;
}
                  cons_term
{
  f -= f1;
}
                  RHS_STORE
{
  if((HadVar1) || (!HadVar2) || (HadVar0)) {
    yyerror("parse error");
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
                ;

xxx_lineair_sum:  x_lineair_sum
                | INF
{
  isign = Sign;
}
                  RHS_STORE
                ;

cons_term:        x_SIGN
                  REALCONS
                | INF
{
  isign = Sign;
}
                ;

int_sec_sos_declarations: /* EMPTY */
                | real_int_sec_sos_decls
                ;

real_int_sec_sos_decls: int_sec_sos_declaration
                | real_int_sec_sos_decls int_sec_sos_declaration
                ;

SEC_INT_SEC_SOS: SEC_INT | SEC_SEC | SEC_SOS
                ;

int_sec_sos_declaration:
                  SEC_INT_SEC_SOS
{
  Within_sos_decl1 = Within_sos_decl;
}
                  x_int_sec_sos_declaration
                ;

xx_int_sec_sos_declaration:
{
  if((!Within_int_decl) && (!Within_sec_decl) && (!Within_sos_decl1)) {
    yyerror("parse error");
    YYABORT;
  }
  SOStype = SOStype0;
  check_int_sec_sos_decl(Within_int_decl, Within_sec_decl, Within_sos_decl1 = (Within_sos_decl1 ? 1 : 0));
}
                  optionalsos
                  vars
                  optionalsostype
                  END_C
{
  if((Within_sos_decl1) && (SOStype == 0))
  {
    yyerror("Unsupported SOS type (0)");
    YYABORT;
  }
}
                ;

x_int_sec_sos_declaration:
                  xx_int_sec_sos_declaration
                | x_int_sec_sos_declaration xx_int_sec_sos_declaration
                ;

optionalsos:    /* EMPTY */
                | SOSDESCR
{
  strcpy(Last_var0, Last_var);
}                
                  sosdescr
                ;

optionalsostype: /* EMPTY */
{
  if(Within_sos_decl1) {
    set_sos_type(SOStype);
    set_sos_weight(SOSweight, 1);
  }
}
                | RE_OPLE
                  INTCONS
{
  if((Within_sos_decl1) && (!SOStype))
  {
    set_sos_type(SOStype = (short) (f + .1));
  }
  else
  {
    yyerror("SOS type not expected");
    YYABORT;
  }
}
                optionalSOSweight
                ;

optionalSOSweight: /* EMPTY */
{
  set_sos_weight(SOSweight, 1);
}
                | COLON
                  INTCONS
{
  set_sos_weight((int) (f + .1), 1);
}
                ;

vars:             /* EMPTY */
                | x_vars
                ;

x_vars          : onevarwithoptionalweight
                | x_vars
                  optionalcomma
                  onevarwithoptionalweight
                ;

optionalcomma:    /* EMPTY */
                | COMMA
                ;

variable:         /* EMPTY */
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
                ;

variablecolon:
{ /* peno2 */
  if(!Within_sos_decl1) {
    yyerror("parse error");
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
                ;

intcons:          /* EMPTY */
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
                ;

sosdescr:         /* EMPTY */
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
                ;

onevarwithoptionalweight:
                  VARIABLE
                  variable
                | VARIABLECOLON
                  variablecolon
                  INTCONSorVARIABLE
                ;

INTCONSorVARIABLE:INTCONS
                  intcons
                | sosdescr
                  x_onevarwithoptionalweight
                ;

x_onevarwithoptionalweight:
                  VARIABLE
                  variable
                | VARIABLECOLON
                  variablecolon
                  INTCONS
                  intcons
                ;

x_lineair_sum:
{
  state0 = 0;
}
                xxxx_lineair_sum
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
                ;

xxxx_lineair_sum: x_lineair_term
                | xxxx_lineair_sum
                  x_lineair_term
                ;

REALCONS: INTCONS | CONS
                ;

xx_lineair_term:  REALCONS
{
  state = 1;
}
                | optional_AR_M_OP
                  VARIABLE
{
  state = 2;
}
                ;

x_lineair_term  : x_SIGN
                  xx_lineair_term
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
      yyerror("var_store failed");
      YYABORT;
    }
    HadConstraint |= HadVar;
    HadVar = HadVar0 = TRUE;
  }
  state0 = state;
}
                ;

lineair_sum     : x_SIGN
                  lineair_term
                | lineair_sum
                  x_SIGN
                  lineair_term
                ;

x_SIGN: /* EMPTY */
{
  isign = 0;
  HadSign = FALSE;
}
                | SIGN
{
  isign = Sign;
  HadSign = TRUE;
}
                ;

lineair_term    : VARIABLE
{
  f = 1.0;
}
                  VAR_STORE
                | REALCONS
                  optional_AR_M_OP
                  VARIABLE
                  VAR_STORE
                ;

optional_AR_M_OP: /* EMPTY */
                | AR_M_OP
                ;

VAR_STORE: /* EMPTY */
{
  if (    (isign || make_neg)
      && !(isign && make_neg)) /* but not both! */
    f = -f;
  if(!var_store(Last_var, f, HadConstraint, HadVar, Had_lineair_sum)) {
    yyerror("var_store failed");
    YYABORT;
  }
  HadConstraint |= HadVar;
  HadVar = HadVar0 = TRUE;
  isign = 0;
}
                ;

VARIABLE: VAR
                ;

xx_lineair_sum: /* EMPTY */
{
  /* to allow a range */
  /* constraint: < max */
  if(!HadConstraint) {
    yyerror("parse error");
    YYABORT;
  }
  Had_lineair_sum = FALSE;
}
                | xxx_lineair_sum
{
  Had_lineair_sum = TRUE;
}
                ;

objective_function:   MAXIMISE real_of
{
  set_obj_dir(TRUE);
}
                    | MINIMISE real_of
{
  set_obj_dir(FALSE);
}
                    | real_of
                ;

real_of:            optional_lineair_sum
                    END_C
{
  add_row();
  HadConstraint = FALSE;
  HadVar = HadVar0 = FALSE;
  isign = 0;
  make_neg = 0;
}
                ;

optional_lineair_sum: /* EMPTY */
                    | lineair_sum
                ;

RHS_STORE: /* EMPTY */
{
  if (    (isign || !make_neg)
      && !(isign && !make_neg)) /* but not both! */
    f = -f;
  if(!rhs_store(f, HadConstraint, HadVar, Had_lineair_sum))
    YYABORT;
  isign = 0;
}
                ;

%%

static void yy_delete_allocated_memory(void)
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

    yy_delete_buffer(YY_CURRENT_BUFFER); /* comment this line if you have problems with it */
    yy_init = 1; /* make sure that the next time memory is allocated again */
    yy_start = 0;
# endif
}

static int parse(void)
{
  return(yyparse());
}

lprec *read_lp(FILE *input, short verbose, char *lp_name)
{
  yyin = input;
  return(yacc_read(verbose, lp_name, &yylineno, parse, yy_delete_allocated_memory));
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

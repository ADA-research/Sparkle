(mod-AblationScenario)=
```{eval-rst}
AblationScenario
===============
.. automodule:: sparkle.AblationScenario
    :members: __init__,check_for_ablation,check_requirements,create_configuration_file,create_instance_file,create_scenario,download_requirements,from_file,read_ablation_table,submit_ablation
```

(mod-Callable)=
```{eval-rst}
Callable
===============
.. automodule:: sparkle.Callable
    :members: 
```

(mod-ConfigurationScenario)=
```{eval-rst}
ConfigurationScenario
===============
.. automodule:: sparkle.ConfigurationScenario
    :members: __init__,create_scenario,create_scenario_file,from_file,serialise
```

(mod-Configurator)=
```{eval-rst}
Configurator
===============
.. automodule:: sparkle.Configurator
    :members: __init__,check_requirements,configure,download_requirements,get_status_from_logs,organise_output,save_configuration,scenario_class
```

(mod-Extractor)=
```{eval-rst}
Extractor
===============
.. automodule:: sparkle.Extractor
    :members: __init__,__repr__,__str__,build_cmd,get_feature_vector,run,run_cli
```

(mod-FeatureDataFrame)=
```{eval-rst}
FeatureDataFrame
===============
.. automodule:: sparkle.FeatureDataFrame
    :members: __abs__,__add__,__and__,__array__,__array_ufunc__,__arrow_c_stream__,__bool__,__contains__,__copy__,__dataframe__,__dataframe_consortium_standard__,__deepcopy__,__delitem__,__dir__,__divmod__,__eq__,__finalize__,__floordiv__,__ge__,__getattr__,__getitem__,__getstate__,__gt__,__iadd__,__iand__,__ifloordiv__,__imod__,__imul__,__init__,__invert__,__ior__,__ipow__,__isub__,__iter__,__itruediv__,__ixor__,__le__,__len__,__lt__,__matmul__,__mod__,__mul__,__ne__,__neg__,__nonzero__,__or__,__pos__,__pow__,__radd__,__rand__,__rdivmod__,__repr__,__rfloordiv__,__rmatmul__,__rmod__,__rmul__,__ror__,__round__,__rpow__,__rsub__,__rtruediv__,__rxor__,__setattr__,__setitem__,__setstate__,__sizeof__,__sub__,__truediv__,__xor__,_accum_func,_align_for_op,_align_frame,_align_series,_append,_arith_method,_arith_method_with_reindex,_as_manager,_box_col_values,_check_inplace_and_allows_duplicate_labels,_check_is_chained_assignment_possible,_check_label_or_level_ambiguity,_check_setitem_copy,_clear_item_cache,_clip_with_one_bound,_clip_with_scalar,_cmp_method,_combine_frame,_consolidate,_consolidate_inplace,_construct_axes_dict,_construct_result,_constructor_from_mgr,_constructor_sliced_from_mgr,_create_data_for_split_and_tight_to_dict,_deprecate_downcast,_dir_additions,_dir_deletions,_dispatch_frame_op,_drop_axis,_drop_labels_or_levels,_ensure_valid_index,_find_valid_index,_flex_arith_method,_flex_cmp_method,_get_agg_axis,_get_axis,_get_axis_resolvers,_get_bool_data,_get_cleaned_column_resolvers,_get_column_array,_get_index_resolvers,_get_item_cache,_get_label_or_level_values,_get_numeric_data,_get_value,_get_values_for_csv,_getitem_bool_array,_getitem_multilevel,_getitem_nocopy,_getitem_slice,_gotitem,_indexed_same,_info_repr,_inplace_method,_is_label_or_level_reference,_is_label_reference,_is_level_reference,_is_view_after_cow_rules,_iset_item,_iset_item_mgr,_iset_not_inplace,_iter_column_arrays,_ixs,_logical_func,_logical_method,_maybe_align_series_as_frame,_maybe_cache_changed,_maybe_update_cacher,_min_count_stat_function,_needs_reindex_multi,_pad_or_backfill,_protect_consolidate,_reduce,_reduce_axis1,_reindex_axes,_reindex_multi,_reindex_with_indexers,_rename,_replace_columnwise,_repr_data_resource_,_repr_fits_horizontal_,_repr_fits_vertical_,_repr_html_,_repr_latex_,_reset_cache,_reset_cacher,_sanitize_column,_set_axis,_set_axis_name,_set_axis_nocheck,_set_is_copy,_set_item,_set_item_frame_value,_set_item_mgr,_set_value,_setitem_array,_setitem_frame,_setitem_slice,_shift_with_freq,_should_reindex_frame_op,_slice,_stat_function,_stat_function_ddof,_take_with_is_copy,_to_dict_of_blocks,_to_latex_via_styler,_update_inplace,_where,abs,add,add_extractor,add_instances,add_prefix,add_suffix,agg,aggregate,align,all,any,apply,applymap,asfreq,asof,assign,astype,at_time,backfill,between_time,bfill,bool,boxplot,clip,combine,combine_first,compare,convert_dtypes,copy,corr,corrwith,count,cov,cummax,cummin,cumprod,cumsum,describe,diff,div,divide,dot,drop,drop_duplicates,droplevel,dropna,duplicated,eq,equals,eval,ewm,expanding,explode,ffill,fillna,filter,first,first_valid_index,floordiv,ge,get,get_feature_groups,get_instance,get_value,groupby,gt,has_missing_value,has_missing_vectors,head,hist,idxmax,idxmin,impute_missing_values,infer_objects,info,insert,interpolate,isetitem,isin,isna,isnull,items,iterrows,itertuples,join,keys,kurt,kurtosis,last,last_valid_index,le,lt,map,mask,max,mean,median,melt,memory_usage,merge,min,mod,mode,mul,multiply,ne,nlargest,notna,notnull,nsmallest,nunique,pad,pct_change,pipe,pivot,pivot_table,pop,pow,prod,product,quantile,query,radd,rank,rdiv,reindex,reindex_like,remaining_jobs,remove_extractor,remove_instances,rename,rename_axis,reorder_levels,replace,resample,reset_dataframe,reset_index,rfloordiv,rmod,rmul,rolling,round,rpow,rsub,rtruediv,sample,save_csv,select_dtypes,sem,set_axis,set_flags,set_index,set_value,shift,skew,sort,sort_index,sort_values,squeeze,stack,std,sub,subtract,sum,swapaxes,swaplevel,tail,take,to_clipboard,to_csv,to_dict,to_excel,to_feather,to_gbq,to_hdf,to_html,to_json,to_latex,to_markdown,to_numpy,to_orc,to_parquet,to_period,to_pickle,to_records,to_sql,to_stata,to_string,to_timestamp,to_xarray,to_xml,transform,transpose,truediv,truncate,tz_convert,tz_localize,unstack,update,value_counts,var,where,xs
```

(mod-FeatureGroup)=
```{eval-rst}
FeatureGroup
===============
.. automodule:: sparkle.FeatureGroup
    :members: 
```

(mod-FeatureSubgroup)=
```{eval-rst}
FeatureSubgroup
===============
.. automodule:: sparkle.FeatureSubgroup
    :members: 
```

(mod-FeatureType)=
```{eval-rst}
FeatureType
===============
.. automodule:: sparkle.FeatureType
    :members: 
```

(mod-FileInstanceSet)=
```{eval-rst}
FileInstanceSet
===============
.. automodule:: sparkle.FileInstanceSet
    :members: __init__,__repr__,__str__,get_path_by_name
```

(mod-InstanceSet)=
```{eval-rst}
InstanceSet
===============
.. automodule:: sparkle.InstanceSet
    :members: __init__,__repr__,__str__,get_path_by_name
```

(mod-Instance_Set)=
```{eval-rst}
Instance_Set
===============
.. automodule:: sparkle.Instance_Set
    :members: 
```

(mod-IterableFileInstanceSet)=
```{eval-rst}
IterableFileInstanceSet
===============
.. automodule:: sparkle.IterableFileInstanceSet
    :members: __determine_size__,__init__,__repr__,__str__,get_path_by_name
```

(mod-MultiFileInstanceSet)=
```{eval-rst}
MultiFileInstanceSet
===============
.. automodule:: sparkle.MultiFileInstanceSet
    :members: __init__,__repr__,__str__,get_path_by_name
```

(mod-Option)=
```{eval-rst}
Option
===============
.. automodule:: sparkle.Option
    :members: __eq__,__getnewargs__,__new__,__repr__,__str__,_asdict,_replace
```

(mod-PCSConverter)=
```{eval-rst}
PCSConverter
===============
.. automodule:: sparkle.PCSConverter
    :members: export,get_convention,parse,parse_irace,parse_paramils,parse_smac,validate
```

(mod-Path)=
```{eval-rst}
Path
===============
.. automodule:: sparkle.Path
    :members: __bytes__,__enter__,__eq__,__exit__,__fspath__,__ge__,__gt__,__hash__,__le__,__lt__,__new__,__reduce__,__repr__,__rtruediv__,__str__,__truediv__,_make_child,_make_child_relpath,absolute,as_posix,as_uri,chmod,exists,expanduser,glob,group,hardlink_to,is_absolute,is_block_device,is_char_device,is_dir,is_fifo,is_file,is_mount,is_relative_to,is_reserved,is_socket,is_symlink,iterdir,joinpath,lchmod,link_to,lstat,match,mkdir,open,owner,read_bytes,read_text,readlink,relative_to,rename,replace,resolve,rglob,rmdir,samefile,stat,symlink_to,touch,unlink,with_name,with_stem,with_suffix,write_bytes,write_text
```

(mod-PerformanceDataFrame)=
```{eval-rst}
PerformanceDataFrame
===============
.. automodule:: sparkle.PerformanceDataFrame
    :members: __abs__,__add__,__and__,__array__,__array_ufunc__,__arrow_c_stream__,__bool__,__contains__,__copy__,__dataframe__,__dataframe_consortium_standard__,__deepcopy__,__delitem__,__dir__,__divmod__,__eq__,__finalize__,__floordiv__,__ge__,__getattr__,__getitem__,__getstate__,__gt__,__iadd__,__iand__,__ifloordiv__,__imod__,__imul__,__init__,__invert__,__ior__,__ipow__,__isub__,__iter__,__itruediv__,__ixor__,__le__,__len__,__lt__,__matmul__,__mod__,__mul__,__ne__,__neg__,__nonzero__,__or__,__pos__,__pow__,__radd__,__rand__,__rdivmod__,__repr__,__rfloordiv__,__rmatmul__,__rmod__,__rmul__,__ror__,__round__,__rpow__,__rsub__,__rtruediv__,__rxor__,__setattr__,__setitem__,__setstate__,__sizeof__,__sub__,__truediv__,__xor__,_accum_func,_align_for_op,_align_frame,_align_series,_append,_arith_method,_arith_method_with_reindex,_as_manager,_box_col_values,_check_inplace_and_allows_duplicate_labels,_check_is_chained_assignment_possible,_check_label_or_level_ambiguity,_check_setitem_copy,_clear_item_cache,_clip_with_one_bound,_clip_with_scalar,_cmp_method,_combine_frame,_consolidate,_consolidate_inplace,_construct_axes_dict,_construct_result,_constructor_from_mgr,_constructor_sliced_from_mgr,_create_data_for_split_and_tight_to_dict,_deprecate_downcast,_dir_additions,_dir_deletions,_dispatch_frame_op,_drop_axis,_drop_labels_or_levels,_ensure_valid_index,_find_valid_index,_flex_arith_method,_flex_cmp_method,_get_agg_axis,_get_axis,_get_axis_resolvers,_get_bool_data,_get_cleaned_column_resolvers,_get_column_array,_get_index_resolvers,_get_item_cache,_get_label_or_level_values,_get_numeric_data,_get_value,_get_values_for_csv,_getitem_bool_array,_getitem_multilevel,_getitem_nocopy,_getitem_slice,_gotitem,_indexed_same,_info_repr,_inplace_method,_is_label_or_level_reference,_is_label_reference,_is_level_reference,_is_view_after_cow_rules,_iset_item,_iset_item_mgr,_iset_not_inplace,_iter_column_arrays,_ixs,_logical_func,_logical_method,_maybe_align_series_as_frame,_maybe_cache_changed,_maybe_update_cacher,_min_count_stat_function,_needs_reindex_multi,_pad_or_backfill,_protect_consolidate,_reduce,_reduce_axis1,_reindex_axes,_reindex_multi,_reindex_with_indexers,_rename,_replace_columnwise,_repr_data_resource_,_repr_fits_horizontal_,_repr_fits_vertical_,_repr_html_,_repr_latex_,_reset_cache,_reset_cacher,_sanitize_column,_set_axis,_set_axis_name,_set_axis_nocheck,_set_is_copy,_set_item,_set_item_frame_value,_set_item_mgr,_set_value,_setitem_array,_setitem_frame,_setitem_slice,_shift_with_freq,_should_reindex_frame_op,_slice,_stat_function,_stat_function_ddof,_take_with_is_copy,_to_dict_of_blocks,_to_latex_via_styler,_update_inplace,_where,abs,add,add_configuration,add_instance,add_objective,add_prefix,add_runs,add_solver,add_suffix,agg,aggregate,align,all,any,apply,applymap,asfreq,asof,assign,astype,at_time,backfill,best_configuration,best_instance_performance,best_performance,between_time,bfill,bool,boxplot,clean_csv,clip,clone,combine,combine_first,compare,configuration_performance,convert_dtypes,copy,corr,corrwith,count,cov,cummax,cummin,cumprod,cumsum,describe,diff,div,divide,dot,drop,drop_duplicates,droplevel,dropna,duplicated,eq,equals,eval,ewm,expanding,explode,ffill,fillna,filter,filter_objective,first,first_valid_index,floordiv,ge,get,get_configurations,get_full_configuration,get_instance_num_runs,get_job_list,get_solver_ranking,get_value,groupby,gt,head,hist,idxmax,idxmin,infer_objects,info,insert,interpolate,is_missing,isetitem,isin,isna,isnull,items,iterrows,itertuples,join,keys,kurt,kurtosis,last,last_valid_index,le,lt,map,marginal_contribution,mask,max,mean,median,melt,memory_usage,merge,min,mod,mode,mul,multiply,ne,nlargest,notna,notnull,nsmallest,nunique,pad,pct_change,pipe,pivot,pivot_table,pop,pow,prod,product,quantile,query,radd,rank,rdiv,reindex,reindex_like,remove_configuration,remove_empty_runs,remove_instances,remove_objective,remove_runs,remove_solver,rename,rename_axis,reorder_levels,replace,resample,reset_index,reset_value,rfloordiv,rmod,rmul,rolling,round,rpow,rsub,rtruediv,sample,save_csv,schedule_performance,select_dtypes,sem,set_axis,set_flags,set_index,set_value,shift,skew,sort_index,sort_values,squeeze,stack,std,sub,subtract,sum,swapaxes,swaplevel,tail,take,to_clipboard,to_csv,to_dict,to_excel,to_feather,to_gbq,to_hdf,to_html,to_json,to_latex,to_markdown,to_numpy,to_orc,to_parquet,to_period,to_pickle,to_records,to_sql,to_stata,to_string,to_timestamp,to_xarray,to_xml,transform,transpose,truediv,truncate,tz_convert,tz_localize,unstack,update,value_counts,var,verify_indexing,verify_objective,verify_run_id,where,xs
```

(mod-RunSolver)=
```{eval-rst}
RunSolver
===============
.. automodule:: sparkle.RunSolver
    :members: __init__,get_measurements,get_solver_args,get_solver_output,get_status,wrap_command
```

(mod-SATVerifier)=
```{eval-rst}
SATVerifier
===============
.. automodule:: sparkle.SATVerifier
    :members: __str__,call_sat_raw_result,sat_verify_output,verify
```

(mod-SelectionScenario)=
```{eval-rst}
SelectionScenario
===============
.. automodule:: sparkle.SelectionScenario
    :members: __init__,create_scenario,create_scenario_file,from_file,serialise
```

(mod-Selector)=
```{eval-rst}
Selector
===============
.. automodule:: sparkle.Selector
    :members: __init__,construct,run,run_cli
```

(mod-Settings)=
```{eval-rst}
Settings
===============
.. automodule:: sparkle.Settings
    :members: __init__,_abstract_getter,apply_arguments,check_settings_changes,get_configurator_output_path,get_configurator_settings,read_settings_ini,write_settings_ini,write_used_settings
```

(mod-SlurmBatch)=
```{eval-rst}
SlurmBatch
===============
.. automodule:: sparkle.SlurmBatch
    :members: __init__
```

(mod-SolutionVerifier)=
```{eval-rst}
SolutionVerifier
===============
.. automodule:: sparkle.SolutionVerifier
    :members: verify
```

(mod-Solver)=
```{eval-rst}
Solver
===============
.. automodule:: sparkle.Solver
    :members: __init__,__repr__,__str__,build_cmd,config_str_to_dict,get_configuration_space,get_pcs_file,parse_solver_output,port_pcs,read_pcs_file,run,run_performance_dataframe
```

(mod-SolverStatus)=
```{eval-rst}
SolverStatus
===============
.. automodule:: sparkle.SolverStatus
    :members: 
```

(mod-SparkleCallable)=
```{eval-rst}
SparkleCallable
===============
.. automodule:: sparkle.SparkleCallable
    :members: __init__,build_cmd,run
```

(mod-SparkleObjective)=
```{eval-rst}
SparkleObjective
===============
.. automodule:: sparkle.SparkleObjective
    :members: __init__,__str__
```

(mod-UseTime)=
```{eval-rst}
UseTime
===============
.. automodule:: sparkle.UseTime
    :members: 
```

(mod-about)=
```{eval-rst}
about
===============
.. automodule:: sparkle.about
    :members: 
```

(mod-cli_types)=
```{eval-rst}
cli_types
===============
.. automodule:: sparkle.cli_types
    :members: TEXT,VerbosityLevel
```

(mod-configspace)=
```{eval-rst}
configspace
===============
.. automodule:: sparkle.configspace
    :members: expression_to_configspace,override,recursive_conversion,ForbiddenGreaterEqualsClause,ForbiddenGreaterThanClause,ForbiddenGreaterThanEqualsRelation,ForbiddenLessEqualsClause,ForbiddenLessThanClause,ForbiddenLessThanEqualsRelation,ForbiddenOrConjunction
```

(mod-configurator)=
```{eval-rst}
configurator
===============
.. automodule:: sparkle.configurator
    :members: Instance_Set,AblationScenario,ConfigurationScenario,Configurator,InstanceSet,PerformanceDataFrame,Solver,SparkleObjective
```

(mod-extractor)=
```{eval-rst}
extractor
===============
.. automodule:: sparkle.extractor
    :members: Extractor,FeatureDataFrame,InstanceSet,RunSolver,SolverStatus,SparkleCallable
```

(mod-feature_dataframe)=
```{eval-rst}
feature_dataframe
===============
.. automodule:: sparkle.feature_dataframe
    :members: FeatureDataFrame
```

(mod-features)=
```{eval-rst}
features
===============
.. automodule:: sparkle.features
    :members: FeatureGroup,FeatureSubgroup,FeatureType
```

(mod-general)=
```{eval-rst}
general
===============
.. automodule:: sparkle.general
    :members: get_time_pid_random_string
```

(mod-get_solver_call_params)=
```{eval-rst}
get_solver_call_params
===============
.. automodule:: sparkle.get_solver_call_params
    :members: 
```

(mod-get_time_pid_random_string)=
```{eval-rst}
get_time_pid_random_string
===============
.. automodule:: sparkle.get_time_pid_random_string
    :members: 
```

(mod-implementations)=
```{eval-rst}
implementations
===============
.. automodule:: sparkle.implementations
    :members: resolve_configurator,Configurator,IRACE,IRACEScenario,ParamILS,ParamILSScenario,SMAC2,SMAC2Scenario,SMAC3,SMAC3Scenario
```

(mod-importlib)=
```{eval-rst}
importlib
===============
.. automodule:: sparkle.importlib
    :members: __import__,_pack_uint32,_unpack_uint32,find_loader,import_module,invalidate_caches,reload
```

(mod-inspect)=
```{eval-rst}
inspect
===============
.. automodule:: sparkle.inspect
    :members: _check_class,_check_instance,_findclass,_finddoc,_has_code_flag,_is_type,_main,_missing_arguments,_shadowed_dict,_signature_bound_method,_signature_from_builtin,_signature_from_callable,_signature_from_function,_signature_fromstr,_signature_get_bound_param,_signature_get_partial,_signature_get_user_defined_method,_signature_is_builtin,_signature_is_functionlike,_signature_strip_non_python_syntax,_static_getmro,_too_many,classify_class_attrs,cleandoc,currentframe,findsource,formatannotation,formatannotationrelativeto,formatargspec,formatargvalues,get_annotations,getabsfile,getargs,getargspec,getargvalues,getattr_static,getblock,getcallargs,getclasstree,getclosurevars,getcomments,getcoroutinelocals,getcoroutinestate,getdoc,getfile,getframeinfo,getfullargspec,getgeneratorlocals,getgeneratorstate,getinnerframes,getlineno,getmembers,getmodule,getmodulename,getmro,getouterframes,getsource,getsourcefile,getsourcelines,indentsize,isabstract,isasyncgen,isasyncgenfunction,isawaitable,isbuiltin,isclass,iscode,iscoroutine,iscoroutinefunction,isdatadescriptor,isframe,isfunction,isgenerator,isgeneratorfunction,isgetsetdescriptor,ismemberdescriptor,ismethod,ismethoddescriptor,ismodule,isroutine,istraceback,namedtuple,signature,stack,trace,unwrap,walktree
```

(mod-instance)=
```{eval-rst}
instance
===============
.. automodule:: sparkle.instance
    :members: Instance_Set,FileInstanceSet,InstanceSet,IterableFileInstanceSet,MultiFileInstanceSet
```

(mod-instances)=
```{eval-rst}
instances
===============
.. automodule:: sparkle.instances
    :members: FileInstanceSet,InstanceSet,IterableFileInstanceSet,MultiFileInstanceSet
```

(mod-objective)=
```{eval-rst}
objective
===============
.. automodule:: sparkle.objective
    :members: PAR,SolverStatus,SparkleObjective,UseTime
```

(mod-objective_string_regex)=
```{eval-rst}
objective_string_regex
===============
.. automodule:: sparkle.objective_string_regex
    :members: 
```

(mod-objective_variable_regex)=
```{eval-rst}
objective_variable_regex
===============
.. automodule:: sparkle.objective_variable_regex
    :members: 
```

(mod-parameters)=
```{eval-rst}
parameters
===============
.. automodule:: sparkle.parameters
    :members: expression_to_configspace,PCSConvention,PCSConverter
```

(mod-performance_dataframe)=
```{eval-rst}
performance_dataframe
===============
.. automodule:: sparkle.performance_dataframe
    :members: resolve_objective,PerformanceDataFrame,SparkleObjective
```

(mod-platform)=
```{eval-rst}
platform
===============
.. automodule:: sparkle.platform
    :members: Option,Settings
```

(mod-re)=
```{eval-rst}
re
===============
.. automodule:: sparkle.re
    :members: _compile,_expand,_pickle,_subx,compile,escape,findall,finditer,fullmatch,match,purge,search,split,sub,subn,template
```

(mod-resolve_objective)=
```{eval-rst}
resolve_objective
===============
.. automodule:: sparkle.resolve_objective
    :members: 
```

(mod-runsolver)=
```{eval-rst}
runsolver
===============
.. automodule:: sparkle.runsolver
    :members: get_time_pid_random_string,RunSolver,SolverStatus
```

(mod-selector)=
```{eval-rst}
selector
===============
.. automodule:: sparkle.selector
    :members: resolve_objective,FeatureDataFrame,InstanceSet,PerformanceDataFrame,SelectionScenario,Selector,SparkleObjective
```

(mod-settings_objects)=
```{eval-rst}
settings_objects
===============
.. automodule:: sparkle.settings_objects
    :members: NamedTuple,resolve_objective,Configurator,Option,Settings,SparkleObjective,VerbosityLevel
```

(mod-slurm_parsing)=
```{eval-rst}
slurm_parsing
===============
.. automodule:: sparkle.slurm_parsing
    :members: SlurmBatch
```

(mod-selector)=
```{eval-rst}
selector
===============
.. automodule:: sparkle.selector
    :members: Extractor,SelectionScenario,Selector
```

(mod-solver)=
```{eval-rst}
solver
===============
.. automodule:: sparkle.solver
    :members: resolve_objective,InstanceSet,PCSConvention,PCSConverter,PerformanceDataFrame,RunSolver,Solver,SolverStatus,SparkleCallable,SparkleObjective,UseTime
```

(mod-solver_wrapper_parsing)=
```{eval-rst}
solver_wrapper_parsing
===============
.. automodule:: sparkle.solver_wrapper_parsing
    :members: get_solver_call_params,parse_commandline_dict,parse_instance,parse_solver_wrapper_args,resolve_objective
```

(mod-sparkle_callable)=
```{eval-rst}
sparkle_callable
===============
.. automodule:: sparkle.sparkle_callable
    :members: SparkleCallable
```

(mod-status)=
```{eval-rst}
status
===============
.. automodule:: sparkle.status
    :members: SolverStatus
```

(mod-structures)=
```{eval-rst}
structures
===============
.. automodule:: sparkle.structures
    :members: FeatureDataFrame,PerformanceDataFrame
```

(mod-tools)=
```{eval-rst}
tools
===============
.. automodule:: sparkle.tools
    :members: get_solver_call_params,get_time_pid_random_string,PCSConverter,RunSolver,SlurmBatch
```

(mod-types)=
```{eval-rst}
types
===============
.. automodule:: sparkle.types
    :members: _check_class,resolve_objective,FeatureGroup,FeatureSubgroup,FeatureType,SolverStatus,SparkleCallable,SparkleObjective,UseTime
```

(mod-verifiers)=
```{eval-rst}
verifiers
===============
.. automodule:: sparkle.verifiers
    :members: SATVerifier,SolutionFileVerifier,SolutionVerifier,SolverStatus
```

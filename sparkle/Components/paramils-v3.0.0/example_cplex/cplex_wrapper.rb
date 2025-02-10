require "param_reader.rb"
#=== This wrapper reads in some parameters, sets up a call to CPLEX, performs it, reads the result, and outputs it in a nice format for ParamILS.

#=== Deal with inputs.
if ARGV.length < 5
	puts "CPLEX wrapper is a wrapper around CPLEX, so it can be tuned with ParamILS."
	puts "Usage: ruby cplex_wrapper.rb <instance_relname> <cutoff_time> <cutoff_length> <seed> <run_objective> <params to be passed on>."
	exit -1
end
instance_relname = ARGV[0]
instance_specifics = ARGV[1] # ignored in all cases so far
cutoff_time = ARGV[2].to_f
cutoff_length = ARGV[3].to_i 
seed = ARGV[4].to_i # ignored

if cutoff_length > 2100000000
	cutoff_length = 2100000000
end

t = Time.now
datetime = t.strftime("%Y-%m-%d %H:%M:%S") # YYYY-MM-DD HH:MM:SS
#outfile = "cplex-out-#{datetime}-#{rand}".gsub(/ /,"")
outfile = "./example_cplex/cplex-out-tmp-#{rand}"

param_lines = []
i=5
while i<ARGV.length-2
	param = ARGV[i].sub(/^-/,"")
	set_cmd = param.gsub(/_/," ")
	#=== Exception for parameter that has a tuple as value
	if param == "simplex_perturbation"
		param_lines << "set #{set_cmd} #{ARGV[i+1]} #{ARGV[i+2]}"
		i+=3
	else
		param_lines << "set #{set_cmd} #{ARGV[i+1]}"
		i+=2
	end
end

#=== Change to however you call CPLEX locally.
#=== This is a File.popen construct, because I need to pipe in all the parameters after calling CPLEX.
#=== (you can also do this as a double File.popen construct: call ruby on the command line to call CPLEX and output something; that something can be read in with File.popen again - this is what I used to do in the commented part below. But now I'm just going via the logfile.)
cmd = "ruby -e 'File.popen(\"use cplex; /cs/local/lib/pkg/cplex-10.1.1/bin/cplex\",\"w\"){|file| "

cplex_lines = []
cplex_lines << "read #{instance_relname}"
#cplex_lines << "set clocktype 2"
#cplex_lines << "set logfile #{outfile}"
cplex_lines << "set mip limits nodes #{cutoff_length}"
cplex_lines << "set timelimit #{cutoff_time}"

#=== Set parameters.
cplex_lines += param_lines

cplex_lines << "display settings all"

cplex_lines << "opt"
cplex_lines << "quit"

cplex_lines.map{|line| cmd += "file.puts \"#{line}\"; "}
cmd += "}'"

puts "Calling: #{cmd} > #{outfile}"
system("#{cmd} > #{outfile}")

=begin
inner_exit = $?
puts "inner exit: #{inner_exit}"
puts "Outfile: #{outfile}"
=end

=begin
File.open(outfile, "w"){|out|
#	puts "Calling cmd: #{cmd}"
	File.popen(cmd){|file|
		while line = file.gets
#			puts line
			out.puts line
		end
	}
}
=end



#########################################################################
#===  Reading output.
#########################################################################

#===  Setting up variables for run output.
solved = "CRASHED"
seed = -1
best_sol = -1
best_length = -1
measured_runlength = -1
measured_runtime = -1

gap = 1e10

File.open(outfile){|file|
	while line = file.gets
#			puts "Read line: #{line}"
		
		#########################################################################
		#===  Parsing CPLEX run output
		#########################################################################
		if line =~/(#{float_regexp})%/
			gap = $1.to_f
		end
			
		if line =~ /MIP\s*-\s*Integer optimal solution:\s*Objective\s*=\s*(#{float_regexp})/
			best_sol = $1
			solved = 'SAT'
		end

		if line =~ /MIP\s*-\s*Integer optimal,\s*tolerance\s*\(#{float_regexp}\/#{float_regexp}\):\s*Objective\s*=\s*(#{float_regexp})/
			best_sol = $1
			solved = 'SAT'
		end
		
		
		if line =~ /Solution time\s*=\s*(#{float_regexp})\s*sec\.\s*Iterations\s*=\s*(\d+)\s*Nodes\s*=\s*(\d+)/
			measured_runtime = $1
			iterations = $2
			measured_runlength = $3
		end

		if line =~ /Solution time\s*=\s*(#{float_regexp}) sec\.\s*Iterations =\s*(\d+)/
#			solved = 'SAT'
			measured_runtime = $1
			iterations = $2				
		end

		if line =~ /Solution time =\s*(#{float_regexp}) sec\./
			#solved = 'SAT'
			measured_runtime = $1
			iterations = 0
		end
		
		if line =~ /Optimal:\s*Objective =\s*#{float_regexp}/
			solved = 'SAT'
		end

		if line =~ /Infeasible/
			solved = 'UNSAT'
		end
		
		if line =~ /MIP\s*-\s*Time limit exceeded, integer feasible:\s*Objective\s*=\s*(#{float_regexp})/
			best_sol = $1
			solved = 'TIMEOUT'
		end
		
		if line =~ /MIP - Time limit exceeded, no integer solution./
			solved = 'TIMEOUT'
		end
		
		if line =~ /CPLEX Error  1001: Out of memory./
			solved = 'TIMEOUT'
		end
		
		if line =~ /CPLEX Error  3019: Failure to solve MIP subproblem./
			solved = 'TIMEOUT'
		end

		if line =~ /CPLEX Error/
			solved = 'TIMEOUT'
		end
		
		if line =~ /Time limit exceeded/
			solved = 'TIMEOUT'
		end
		
#			if line =~ /Filesize limit exceeded/
#				solved = 'TIMEOUT'
#			end

		if line =~ /Solution time =\s*(#{float_regexp})\s*sec\.\s*Iterations\s*=\s*(\d+)\s*Nodes\s*=\s*\((\d+)\)\s*\((\d+)\)/
			measured_runtime = $1
			iterations = $2
			measured_runlength = $3
		end
		
		raise "Error: Failed to initialize CPLEX environment" if line =~ /Failed to initialize CPLEX environment./
	end
	best_sol = gap # This is really what we want to minimize.

#		raise "Error: solved neither TIMEOUT nor SAT - probably parsing problem. Here's the complete output: #{content}"

	if solved == "CRASHED"
		puts "\n\n==============================================\n\nWARNING: CPLEX crashed -> most likely file not found or no license\n\n=======================\n"
		#=== You may want to catch this exception and try a rerun once a license frees up - that's what I do in my own experiments.
		raise "No such file or directory: CPLEX crashed -> most likely file not found or no license\n\n======================="
	else
		puts "Result for ParamILS: #{solved}, #{measured_runtime}, #{measured_runlength}, #{best_sol}, #{seed}"
	end
}
File.delete(outfile)

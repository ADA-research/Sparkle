#!/usr/bin/ruby

# parse all parameters
instance = ARGV[0]
runtime = ARGV[2].to_f
seed = ARGV[4].to_i
params = ARGV[5..-1].each_slice(2).map {|k,v| [k[1..-1], v]}.to_h

# show the value of the parameter "a"
puts params['a']

# mock the execution of the target algorithm
srand(seed)
quality = Array.new(4) { rand } # 4 random values
time = runtime # fake true runtime
status = 'SUCCESS'

# # write here how your algorithm must be executed
# cmd = "./my_complicated_target_algorithm %s --seed=%d"%[instance, seed]
# cmd += ' --param_a="+params['a']

# # execute cmd and returns the list of lines for the output
# output = `#{cmd}`.split("\n")

# # and how to parse its output
# quality = []
# quality << $1 if output.any? {|line| line =~ /final quality is (.*)/}
# if output.include?("finished successfully')
#   status = 'SUCCESS'
# else
#   status = 'CRASHED'
# end

# print final result
puts 'Result: %s, %f, %s, %d'%[status, time, quality.inspect, seed]

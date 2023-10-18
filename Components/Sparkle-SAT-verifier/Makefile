.PHONY: all clean

all: SAT

clean:
	rm -f *.o
	rm -f SAT

SAT: SAT.cc
	g++ SAT.cc -o SAT -O2
	rm -f *~

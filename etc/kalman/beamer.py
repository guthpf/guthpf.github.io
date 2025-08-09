# -*- coding: UTF-8 -*-
# Copyright (c) Gustavo T. Pfeiffer 2025.

# INSTALLATION METHOD #1
#	sudo gedit /usr/share/gtksourceview-3.0/language-specs/latex.lang
#	change this line:
#    <property name="globs">*.tex;*.ltx;*.sty;*.cls;*.dtx;*.ins;*.bbl;</property>
#	to:
#    <property name="globs">*.tex;*.ltx;*.sty;*.cls;*.dtx;*.ins;*.bbl;*.apr</property>

# INSTALLATION METHOD #2
#	sudo gedit /usr/share/mime/packages/freedesktop.org.xml
#	Find line:
#		<glob pattern="*.tex"/>
#	Add the following line afterwards:
#		<glob pattern="*.apr"/>


# ASTERISK SYNTAX
#
# *  :item			(APR only)
# */ :item+pause	(APR only)
# ** :asterisk		(both)
# *[ :latex begin	(APR only)
# *] :latex end		(TEX only)

import sys
for inputn in sys.argv[1:]:

	assert(inputn[-4:] == ".apr")
	outputn = inputn[:-4] + ".tex"
	raw = "".join([l for l in open(inputn)]).replace("　", " ");

	proc = [[]]
	special = False
	rubymode = False
	rubystr = []
	for c in raw:
		if special:
			special = False
			if rubymode:
				assert(c in ['>'])
				#assert(len(proc) % 2 == 1)
				rubymode = False
				rubystr = [x.split('.') for x in ''.join(rubystr).split('|')]
				print rubystr
				assert(len(rubystr)==2 and len(rubystr[0]) == len(rubystr[1]))
				proc[-1] += ["\\ruby{"+rubystr[0][i]+"}{"+rubystr[1][i]+"}" for i in range(len(rubystr[0]))]
				rubystr = []
			else:
				assert(c in ['[',']','*',' ', '/', '<'])
				if c == '[':
					assert(len(proc) % 2 == 1)
					proc += [[]]
				elif c == ']':
					assert(len(proc) % 2 == 0)
					proc += [[]]
				elif c == "<":
					assert(not rubymode)
					#assert(len(proc) % 2 == 1)
					rubymode = True
				elif c in [' ', '/']:
					assert(len(proc) % 2 == 1)
					proc[-1] += ['*', c]
				else: #c == "*"
					if len(proc) % 2 == 1: #APR mode
						proc[-1] += ['*', c]
					else: #TEX mode
						proc[-1] += [c]
		elif c == "*":
			special = True
		else:
			if rubymode:
				rubystr += [c]
			else:
				proc[-1] += [c]

	for i in range(len(proc)):
		proc[i] = ''.join(proc[i])
	
	if proc[-1] == "":
		proc = proc[:-1]

	output = []
	level = -2
	#levels:
	#           -> -2
	#Title      -> -1
	#* Item     -> 0
	#  * Item   -> 1
	#    * Item -> 2
	mode = 0
	#modes:
	#  0 - after \n
	#  1+ - before asterisk
	#  -1 - after asterisk or title
	special = False
	for i in range(len(proc)):
		if i % 2 == 0: #APR mode
			for j in range(len(proc[i])):
				c = proc[i][j]
				print c, level, mode
				if c == '\n' and not special:
					if mode >= 0:
						if level >= -1:
							while level > -1:
								level -= 1
								output += ['\t' * (level + 1) + "\\end{itemize}\n"]
							output += ["\\end{frame}\n"]
							level -= 1
							assert(level == -2)
					else: #mode == -1
						if level == -2:
							output += ["}"]
							level += 1
					output += [c]
					mode = 0
				elif c == ' ' and not special:
					if mode >= 0:
						mode += 1
					else:
						output += [c]
				elif c == '*' and not special:
					special = True
				else:
					if special:
						assert(c in ['*',' ', '/'])
						if c in [' ', '/']:
							assert(level >= -1)
							c = "\\item " + ("" if c == ' ' else "\\pause ")
							if mode > -1:
								mode += 2
						special = False
					if level == -2 and mode >= 0:
						mode = -1
						output += ["\\begin{frame}\\frametitle{"]
					else:
						if mode > -1:
							assert(mode % 2 == 0)
							newlevel = mode / 2 - 1
							if level < newlevel:
								while level != newlevel:
									output += ['\t' * (level + 1) + "\\begin{itemize}\n"]
									level += 1
							elif level > newlevel:
								while level != newlevel:
									level -= 1
									output += ['\t' * (level + 1) + "\\end{itemize}\n"]
							output += ['\t' * (mode / 2)]
							mode = -1
					output += [c]
					
		else:
			output += [proc[i]]
			if level != -2:
				mode = -1

	f = open(outputn,'w')
	f.write(''.join(output))

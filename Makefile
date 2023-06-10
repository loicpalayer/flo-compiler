# input files with relative path
BASE_INPUT=$(wildcard input/*)
# only basename of input files, without extension
INPUT=$(basename $(notdir $(BASE_INPUT)))

.DEFAULT_GOAL := all

create_output_dir:
	mkdir -p output

generation_code_nasm: create_output_dir
	for a in $(INPUT); do echo "Generation code nasm: " $${a}; python3 main.py input/$${a}.flo > output/$${a}.nasm || (exit 0); done; 

assembleur_vers_executable: generation_code_nasm
	for a in $(INPUT); do echo "Assemblage: " $${a}; nasm -f elf -g -F dwarf output/$${a}.nasm; ld -m elf_i386 -o output/$${a} output/$${a}.o; done;

all: assembleur_vers_executable
	exit 0
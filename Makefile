# Compiler
LUATEX = lualatex

# Directories
TEX_DIR = tex
PDF_DIR = pdf
BUILD_DIR = build
TEXMF = texmf

# Automatically find all .tex files in the tex directory
TEX_FILES := $(wildcard $(TEX_DIR)/*.tex)

# Replace .tex with .pdf and change output dir to pdf/
PDF_FILES := $(patsubst $(TEX_DIR)/%.tex, $(PDF_DIR)/%.pdf, $(TEX_FILES))

# TEXINPUTS tells LaTeX where to find custom classes/styles
TEXINPUTS := $(TEXMF):

# Default target
all: pdfs

pdfs: $(PDF_FILES)

# Ensure image assets are available in the build dir
prepare:
	rm -rf $(BUILD_DIR)/*
	mkdir -p $(BUILD_DIR)/res/img
	cp -ru res/img/* $(BUILD_DIR)/res/img/

# Compile rule: .tex in tex/ → .pdf in pdf/
$(PDF_DIR)/%.pdf: $(TEX_DIR)/%.tex | prepare
	@echo "Compiling $< to $@"
	@mkdir -p $(PDF_DIR) $(BUILD_DIR)
	TEXINPUTS=$(TEXINPUTS) $(LUATEX) -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $<
	TEXINPUTS=$(TEXINPUTS) $(LUATEX) -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $<
	@mv $(BUILD_DIR)/$*.pdf $(PDF_DIR)/

# Clean intermediate files
clean:
	rm -rf $(BUILD_DIR)/*

# Clean everything (intermediate + output)
distclean: clean
	rm -f $(PDF_DIR)/*.pdf

# Live preview (requires latexmk and fswatch installed)
watch:
	@echo "Watching .tex files for changes..."
	fswatch -o $(TEX_DIR)/*.tex | while read; do make; done

# Open PDFs (macOS: open, Linux: xdg-open)
open:
	xdg-open $(PDF_DIR)/resume_FR_webDev.pdf

.PHONY: all clean distclean watch open pdfs

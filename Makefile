# ── Variables ─────────────────────────────────────────────────────────────────
   # Compiler
LUATEX = lualatex

   # Directories
TEX_DIR  = artifacts/tex
PDF_DIR  = artifacts/pdf
QR_DIR   = artifacts/qr
BUILD_DIR = build
RES_DIR = res
TEXMF    = $(RES_DIR)/tex/texmf
VENV     := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip
   # ── TEXINPUTS ────
TEXINPUTS := $(TEXMF):

# ── Top-level entry point ─────────────────────────────────────────────────────
# Phase 1: generate .tex files, then re-invoke make for phase 2.
# The $(MAKE) call gets a completely fresh parse, so wildcard sees the new files.
all:
# 	$(MAKE) deps
# 	$(PYTHON) ./generate_tex.py --profiles it-software --files ./res/resumesData/resume_CAN*
	$(MAKE) tex
	$(MAKE) _build

tex: prepareTex
	$(MAKE) deps
	$(PYTHON) ./generate_tex.py --profiles it-software --files ./res/resumesData/resume_CAN* -o $(TEX_DIR) --selfrefqr

# ── Python venv ──────────────────────────────────────────────────────────────
$(VENV)/bin/python:
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip setuptools wheel

# ── Phase 2: everything that depends on .tex files existing ───────────────────
# Only reached via the recursive $(MAKE) call above, never directly by the user.
# At this point the .tex files are guaranteed to be on disk.
TEX_FILES := $(wildcard $(TEX_DIR)/*.tex)
PDF_FILES := $(patsubst $(TEX_DIR)/%.tex, $(PDF_DIR)/%.pdf, $(TEX_FILES))
QR_FILES  := $(patsubst $(TEX_DIR)/%.tex, $(QR_DIR)/%.png,  $(TEX_FILES))

_build: prepareQr qrcodes pdfs
resumes: pdfs
qrresumes: prepareQr qrcodes pdfs

pdfs:    $(PDF_FILES)
qrcodes: $(QR_FILES)

# ── Setup / deps ──────────────────────────────────────────────────────────────
setup:
	@echo "System requirements:"
	@echo "  - texlive-luatex"
	@echo "  - texlive-latex-extra"
	@echo "  - latexmk"
	@echo ""
	@echo "Python venv will be created automatically on first build."

deps: $(VENV)/bin/python requirements.txt
	$(PIP) install -r requirements.txt

# ── Prepare build dirs ────────────────────────────────────────────────────────
preparePdf:
	@rm -rf $(PDF_DIR)/*
	@mkdir -p $(PDF_DIR)
	rm -rf $(BUILD_DIR)/*
	mkdir -p $(BUILD_DIR)/res/img/qr
	cp -ru res/img/* $(BUILD_DIR)/res/img/
	cp -ru $(QR_DIR)/* $(BUILD_DIR)/res/img/qr

prepareQr: deps
	@echo "Preparing QR directory..."
	@rm -rf $(QR_DIR)/*
	@mkdir -p $(QR_DIR)

prepareTex:
	rm -rf $(TEX_DIR)/*
	mkdir -p $(TEX_DIR)

# ── Compile rules ─────────────────────────────────────────────────────────────
$(QR_DIR)/%.png: $(TEX_DIR)/%.tex | prepareQr
	@echo "Generating QR for $<"
	@mkdir -p $(QR_DIR)
	@filename=$$(basename $< .tex); \
	    url="https://nokheenig.github.io/ResumeGen/$$filename.pdf"; \
	    echo "Target URL: $$url"; \
	$(PYTHON) generate_qr.py -f $@ -u "$$url" -w 2

$(PDF_DIR)/%.pdf: $(TEX_DIR)/%.tex | preparePdf
	@echo "Compiling $< to $@"
	@mkdir -p $(PDF_DIR) $(BUILD_DIR)
	TEXINPUTS=$(TEXINPUTS) $(LUATEX) -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $<
	TEXINPUTS=$(TEXINPUTS) $(LUATEX) -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $<
	@mv $(BUILD_DIR)/$*.pdf $(PDF_DIR)/

# ── Utilities ─────────────────────────────────────────────────────────────────
clean:
	rm -rf $(BUILD_DIR)/*

distclean: clean
	rm -f $(PDF_DIR)/*.pdf
	rm -f $(TEX_DIR)/*.tex

watch:
	@echo "Watching .tex files for changes..."
	fswatch -o $(TEX_DIR)/*.tex | while read; do make; done

open:
	xdg-open $(PDF_DIR)/resume_FR_webDev.pdf

.PHONY: all _build clean distclean watch open pdfs qrcodes preparePdf prepareQr prepareTex deps setup tex
TEXFILES := $(wildcard tex/*.tex)
PDFFILES := $(patsubst tex/%.tex, pdf/%.pdf, $(TEXFILES))
TEXMF := texmf

LUATEX := lualatex
LUATEX_OPTS := -output-directory=build -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all clean pdfs

all: pdfs

pdfs: $(PDFFILES)

pdf/%.pdf: tex/%.tex
	@mkdir -p build
	@mkdir -p pdf
	$(LUATEX) -output-directory=build -include-directory=$(TEXMF) $<
	@cp build/$(notdir $@) $@

clean:
	rm -rf build/*

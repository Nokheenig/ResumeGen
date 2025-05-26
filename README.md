# 📄 LaTeX Resume Generator

This repository contains a dynamic LaTeX-based CV/resume system that supports:

- 🐍 Auto-generation of `.tex` files from source using Python
- 📦 Organized assets (images, class file, style file)
- 🛠️ Build automation with `Makefile`
- ☁️ Continuous PDF generation via GitHub Actions

---

## 🗂 Project Structure

project-root/
├── generate_tex.py       # Python script to generate .tex files
├── Makefile              # Build all PDFs
├── tex/                  # Auto-generated LaTeX sources,versioned source .tex files (output of generate_tex.py)
│   ├── resume_FR_webDev.tex
│   └── ...
├── pdf/                  # Output directory (compiled PDFs), Versioned output PDFs
│   ├── resume_FR_webDev.pdf
│   └── ...
├── build/                # Unversioned build folder (intermediate files)
│   ├── resume_FR_webDev.aux
│   ├── ...
├── texmf/                # Custom class/style files
│   ├── friggeri-cv.cls      # Custom CV class
│   └── dtklogos.sty         # Style file (if used)
├── res/                  # Static assets, All images and data used in resumes
│   ├── resume_FR.json
│   ├── resume_EN.json
│   └── img/
│       └── ...
├── .gitignore
└── README.md


---

## 🚀 Usage

### 1. Generate `.tex` files from Python

```bash
python generate_tex.py
```

This script creates .tex files in the tex/ directory.

### 2. Compile PDFs with make

```bash
make
```

This compiles all .tex files in tex/ into PDFs in the out/ folder using lualatex.

You can also compile a specific file:
```bash
make out/resume_FR_webDev.pdf
```

🧪 GitHub Actions (CI)
This repository includes a GitHub Actions workflow to:

Auto-generate PDFs on every push

Cache LaTeX packages

Upload PDFs as artifacts

📁 PDFs are saved in the out/ directory and versioned via Git.

📝 LaTeX Notes
Images must be referenced relatively: \includegraphics{../res/img/myphoto.jpg}

\graphicspath{{../res/img/}} is configured in the class file

Custom class: friggeri-cv.cls

All LaTeX packages used are included via \RequirePackage in the class file

⚙️ Requirements
- Python 3.8+
- lualatex (TeX Live recommended)
- make

For Ubuntu/Debian:
```bash
sudo apt install texlive-full make python3
```

Or lighter
```bash
sudo apt install texlive-luatex texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-bibtex-extra latexmk make python3
```

📜 License
MIT License – free to use, modify, and distribute.

🙋 Questions?
Open an issue or contact @Nokheenig


---

Let me know if you’d like it in French, or if you want separate sections for multilingual resumes, CI badges, or GitHub Pages integration.

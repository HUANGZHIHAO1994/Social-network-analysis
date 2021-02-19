(TeX-add-style-hook
 "bmvc2k"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "a4paper" "twoside" "10pt")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("hyperref" "colorlinks" "urlcolor=blue" "citecolor=red" "bookmarks=false") ("geometry" "twoside" "headsep=3mm" "a4paper" "inner=11mm" "outer=11mm" "top=3mm" "includehead" "bottom=8mm" "heightrounded" "papersize={410pt,620pt}" "inner=9mm" "outer=6mm" "bottom=5mm") ("fontenc" "T1") ("bmvc2k_natbib" "sort" "numbers")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperref")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "article"
    "art10"
    "color"
    "graphicx"
    "subfigure"
    "xspace"
    "eso-pic"
    "url"
    "hyperref"
    "amsmath"
    "geometry"
    "fontenc"
    "mathptmx"
    "helvet"
    "courier"
    "bmvc2k_natbib")
   (TeX-add-symbols
    "bmv"
    "bmvaOneDot"
    "bmvcreviewcopy"
    "bmvaCenterBox"
    "bmvaHangBox"
    "bmvaBaselineHangBox"
    "bmvadebug"
    "bmvaResetAuthors"
    "addauthor"
    "addinstitution"
    "maketitle"
    "runninghead"
    "bmvaEtAl"
    "makevruler"
    "bibsection")
   (LaTeX-add-pagestyles
    "bmv")
   (LaTeX-add-color-definecolors
    "bmv@PaleBlue"
    "bmv@PalePink"
    "bmv@sectioncolor"
    "bmv@captioncolor"
    "bmv@CiteBoxColor"))
 :latex)


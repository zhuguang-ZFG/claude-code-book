# Repository entry points for the offline book editions.
# The book Markdown is the source of truth; everything here only derives.
#
# Every target is a thin wrapper over scripts/bookctl.py, so Windows, a
# developer shell and CI run the same commands. On Windows without make, call
# the same lines directly, e.g. `python scripts/bookctl.py check --fast`.
#
#   PYTHON     python launcher (make PYTHON=python3 on Linux CI)
#   BOOK_LANG  zh | en | both  -- deliberately NOT named LANG, which every
#              shell already exports as the locale (C.UTF-8, zh_CN.UTF-8, ...)

PYTHON     ?= python
BOOK_LANG  ?= both
BOOKCTL    := $(PYTHON) scripts/bookctl.py

.PHONY: help doctor check check-fast check-full book book-pdf book-omp book-omp-pdf book-pi book-pi-pdf book-pi-epub book-pi-all index clean
.PHONY: book-agents book-opencode-all book-deepseek-all book-hermes-all book-codex-all
.PHONY: book-prompt-all book-kimi-all book-collected package-prompt

help:
	@echo "make doctor     environment report (python/node/browser/font/deps)"
	@echo "make check      fast checks: source build, tests, content, mermaid"
	@echo "make check-full fast + rendered HTML + both PDF editions"
	@echo "make book       both HTML editions (BOOK_LANG=zh|en|both, into yuyu-book/dist/)"
	@echo "make book-pdf   both HTML editions + A4 PDF post-pass"
	@echo "make book-omp   omp Chinese HTML (yuyu-omp-zh.html); does not touch harness"
	@echo "make book-omp-pdf  omp Chinese HTML + A4 PDF"
	@echo "make book-pi    Pi Chinese HTML (yuyu-pi-zh.html)"
	@echo "make book-pi-pdf  Pi Chinese HTML + A4 PDF"
	@echo "make book-pi-epub  Pi Chinese HTML + EPUB"
	@echo "make book-pi-all  Pi Chinese HTML + A4 PDF + EPUB"
	@echo "make book-agents  four Agent volumes: Chinese HTML + PDF + EPUB"
	@echo "make book-codex-all  one volume (also opencode/deepseek/hermes)"
	@echo "make index      rebuild subject-index.json from appendix D"
	@echo "make clean      remove yuyu-book/dist/ (no rm -rf)"
	@echo "variables in use: PYTHON=$(PYTHON) BOOK_LANG=$(BOOK_LANG)"

doctor:
	$(BOOKCTL) doctor

check: check-fast

check-fast:
	$(BOOKCTL) check --fast

check-full:
	$(BOOKCTL) check --full

book:
	$(BOOKCTL) build --product book --lang $(BOOK_LANG)

book-pdf:
	$(BOOKCTL) build --product book --lang $(BOOK_LANG) --pdf

book-omp:
	$(BOOKCTL) build --product omp --lang zh

book-omp-pdf:
	$(BOOKCTL) build --product omp --lang zh --pdf

book-pi:
	$(BOOKCTL) build --product pi --lang zh

book-pi-pdf:
	$(BOOKCTL) build --product pi --lang zh --pdf

book-pi-epub:
	$(BOOKCTL) build --product pi --lang zh --epub

book-pi-all:
	$(BOOKCTL) build --product pi --lang zh --pdf --epub

book-agents: book-opencode-all book-deepseek-all book-hermes-all book-codex-all \
            book-prompt-all book-kimi-all

book-opencode-all book-deepseek-all book-hermes-all book-codex-all \
book-prompt-all book-kimi-all:
	$(BOOKCTL) build --product $(patsubst book-%-all,%,$@) --lang zh --pdf --epub

# The nine-volume collected edition binds every shipped book; each volume
# keeps its own manifest, so only the collection manifest is passed. It ships
# the single HTML: binding nine books inlines every plate, and the print pass
# over that document is not a build step anyone should wait for.
book-collected:
	$(BOOKCTL) build --product collected --lang zh

# Offline exercise archive for the prompt volume; the digest table inside
# records every shipped source file.
package-prompt:
	$(PYTHON) scripts/package_prompt.py --output yuyu-book/dist/yuyu-prompt-zh-examples.zip

# --regen-index rebuilds subject-index.json and then continues into a full
# assembly; the canonical package CLI has no index-only invocation.
index:
	$(BOOKCTL) build --regen-index --lang $(BOOK_LANG)

clean:
	$(BOOKCTL) clean

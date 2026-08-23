.PHONY: help install run test lint format ruff check clean

help:            ## Показать список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install:         ## Установить зависимости
	poetry install

format:          ## Только форматирование
	poetry run ruff format .

lint:            ## Только проверка линтером с автофиксом
	poetry run ruff check . --fix

ruff:            ## Ruff на всё сразу: форматирование + линт с автофиксом
	poetry run ruff format .
	poetry run ruff check . --fix

check:           ## Проверка без изменений (для CI): формат + линт в режиме "только проверить"
	poetry run ruff format . --check
	poetry run ruff check .

clean:           ## Удалить кэши
	rm -rf .ruff_cache .pytest_cache __pycache__

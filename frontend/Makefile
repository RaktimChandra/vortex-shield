.PHONY: help install dev build start lint format test clean

help:
	@echo "VORTEX Shield Frontend - Development Commands"
	@echo ""
	@echo "install - Install dependencies"
	@echo "dev     - Run development server"
	@echo "build   - Build for production"
	@echo "start   - Start production server"
	@echo "lint    - Run ESLint"
	@echo "format  - Format code with Prettier"
	@echo "test    - Run tests"
	@echo "clean   - Clean build artifacts"

install:
	npm install

dev:
	npm run dev

build:
	npm run build

start:
	npm run start

lint:
	npm run lint

lint-fix:
	npm run lint -- --fix

format:
	npx prettier --write "**/*.{ts,tsx,js,jsx,json,css,md}"

test:
	npm test

test-watch:
	npm test -- --watch

clean:
	rm -rf .next
	rm -rf out
	rm -rf node_modules/.cache

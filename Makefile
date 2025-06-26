# Makefile for Monitor Brightness Toggle

.PHONY: help install test clean uninstall start stop status logs

help:
	@echo "Monitor Brightness Toggle - Available commands:"
	@echo ""
	@echo "  make install    - Deploy the service (conda environment + systemd)"
	@echo "  make test       - Test the application directly"
	@echo "  make start      - Start the systemd service"
	@echo "  make stop       - Stop the systemd service"
	@echo "  make status     - Show service status"
	@echo "  make logs       - Show service logs"
	@echo "  make clean      - Clean Python cache files"
	@echo "  make uninstall  - Remove service and optionally environment"
	@echo ""
	@echo "Development commands:"
	@echo "  ./dev.sh help   - Show all development commands"

install:
	@echo "Deploying Monitor Brightness Toggle service..."
	./deploy.sh

test:
	./dev.sh test

start:
	./dev.sh service-start

stop:
	./dev.sh service-stop

status:
	./dev.sh service-status

logs:
	./dev.sh service-logs

clean:
	./dev.sh clean

uninstall:
	./uninstall.sh

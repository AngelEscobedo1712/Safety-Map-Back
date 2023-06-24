.DEFAULT_GOAL := default
#################### PACKAGE ACTIONS ###################
reinstall_package:
	@pip uninstall -y Safety-Map || :
	@pip install -e .


run_api:
	uvicorn api.fastapi.fast:app --host 0.0.0.0 --port 8000

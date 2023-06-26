.DEFAULT_GOAL := default
#################### PACKAGE ACTIONS ###################
reinstall_package:
	@pip uninstall -y Safety-Map || :
	@pip install -e .


run_api:
	uvicorn api.fastapi.fast:app --reload

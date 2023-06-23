.DEFAULT_GOAL := default
#################### PACKAGE ACTIONS ###################
reinstall_package:
	@pip uninstall -y Safety-Map || :
	@pip install -e .


run_api:
	uvicorn Safety-Map.api.fastapi.fast:app --reload

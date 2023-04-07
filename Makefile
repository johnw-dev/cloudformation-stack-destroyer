.PHONY=clean,lint,lint_check,test,synth,deploy,deploy_ci,deploy_test
-include .env

clean:
	rm -rf cdk.out
	rm -rf dist
	find . -name __pycache__ | xargs rm -rf
	rm -rf assets

lint:
	poetry run black .

lint_check:
	poetry run black --check .
	poetry run bandit -r function
	poetry run safety check

test: clean lint_check assets
	poetry run pytest tests

assets: clean
	mkdir assets
	cp -r function assets/function

synth: clean assets
	cdk synth

deploy: clean assets
	cdk deploy CFDestroyer

deploy_ci: clean assets
	cdk deploy CFDestroyer --require-approval never

deploy_test: clean assets
	cdk deploy --all --require-approval never
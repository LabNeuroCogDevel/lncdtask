.PHONY: test
test: .pytest_res.txt
.pytest_res.txt: $(wildcard tests/*py) $(wildcard lncdtask/*py)
	python -m pytest tests/ | tee $@

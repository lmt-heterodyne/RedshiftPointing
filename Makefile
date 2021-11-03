PYTHON = python

clean:
	rm -f *~ *.pyc *.png


test1:
	$(PYTHON) runLineCheck.py > test1.log 2>&1
	@echo Plot in rsr_summary.png

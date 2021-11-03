PYTHON = python

clean:
	rm -f *~ *.pyc *.png


test1:
	@echo You need obsnum 27869 27870 27871 for this:
	$(PYTHON) runLineCheck.py > test1.log 2>&1
	@echo Plot in rsr_summary.png

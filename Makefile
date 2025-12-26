.PHONY: validate-junction

validate-junction:
	python src/geometry_core/tools/trix.py validate src/geometry_core/matrix_junction.md --spec src/geometry_core/spec/matrix_junction_ops.yaml

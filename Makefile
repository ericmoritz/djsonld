DJANGO_SETTINGS_MODULE ?= djsonld.test_settings
ENV=DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
test:
	${ENV} py.test --doctest-modules djsonld --flakes


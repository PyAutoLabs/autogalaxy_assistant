.PHONY: validate-literature-citations audit test colab-contexts

validate-literature-citations:
	python -m autoassistant.literature validate-citations

# Symbol/idiom audit of skills + wiki against the installed stack.
audit:
	python autoassistant/audit_skill_apis.py

# Assistant tooling test suite (slow: the gate tests import autogalaxy per case).
test:
	python -m pytest autoassistant/tests -q

# colab/contexts.yaml: mapped skills exist and every entry fits the Gemini cap (`cap:` in the file).
colab-contexts:
	python -m autoassistant.colab_contexts check

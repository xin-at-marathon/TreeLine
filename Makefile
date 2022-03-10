TREELINE_REPO:=$(HOME)/repo/xin/treeline-repo

.PHONY: test start bash
test:
	docker run -it --rm \
		-v $(PWD)/source:/usr/local/share/treeline \
		-v /tmp/output:/output \
		-v $(TREELINE_REPO):/input:ro \
		--workdir /usr/local/share/treeline --entrypoint python \
		bryt/treeline-cmd -m unittest -v command.test.test_render

bash:
	docker run -it --rm \
		-v $(PWD)/source:/usr/local/share/treeline \
		-v /tmp/output:/output \
		-v $(TREELINE_REPO):/input:ro \
		--entrypoint bash bryt/treeline-cmd

run:
	docker run -it --rm \
		-v $(PWD)/source:/usr/local/share/treeline \
		-v /tmp/output:/output \
		-v $(TREELINE_REPO):/input:ro \
		bryt/treeline-cmd render topic /input/repo.trln /input/res /input/template/topic-document-html.json /output/uid/document/html

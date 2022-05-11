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

render-topic:
	docker run -it --rm \
		-v $(PWD)/source:/usr/local/share/treeline \
		-v /tmp/output:/output \
		-v $(TREELINE_REPO):/input:ro \
		bryt/treeline-cmd render topic document html /input/repo.trln /output/topic/uid/document/html

render-article:
	docker run -it --rm \
		-v $(PWD)/source:/usr/local/share/treeline \
		-v /tmp/output:/output \
		-v $(TREELINE_REPO):/input:ro \
		bryt/treeline-cmd render article document html /input/repo.trln /output/article/uid/document/html

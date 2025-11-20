APP_NAME = hw3
CONTAINER_NAME = hw3-docker
PORT = 3000

build:
	docker build --no-cache -t $(APP_NAME) .

run:
	docker run -d \
		-p $(PORT):3000 \
		-v "$(PWD)/storage:/app/storage" \
		--name $(CONTAINER_NAME) \
		$(APP_NAME)

stop:
	docker stop $(CONTAINER_NAME)

rm:
	docker rm $(CONTAINER_NAME)

import time
import datetime
import numpy as np
import random
from faker import Faker
from zoneinfo import ZoneInfo
from kafka import KafkaProducer, KafkaAdminClient
from kafka.errors import KafkaError
from kafka.admin import NewTopic
import json
from log_paring_procesor import args


local_tz = ZoneInfo("Asia/Seoul")
faker = Faker()


class LogGenerator:
    def __init__(self, log_format: str):
        self.log_format = log_format
        self.status_codes = ["200", "404", "500", "301"]
        self.methods = ["GET", "POST", "DELETE", "PUT"]
        self.resources = [
            "/list",
            "/wp-content",
            "/wp-admin",
            "/explore",
            "/search/tag/list",
            "/app/main/posts",
            "/posts/posts/explore",
            "/apps/cart.jsp?appID=",
        ]
        self.user_agents = [
            faker.firefox,
            faker.chrome,
            faker.safari,
            faker.internet_explorer,
            faker.opera,
        ]

    def generate_log_line(self) -> dict:
        ip = faker.ipv4()
        timestamp = datetime.datetime.now(local_tz).strftime("%d/%b/%Y:%H:%M:%S %z")
        method = str(np.random.choice(self.methods, p=[0.6, 0.1, 0.1, 0.2]))
        resource = random.choice(self.resources)
        if "apps" in resource:
            resource += str(random.randint(1000, 10000))
        status_code = str(
            np.random.choice(self.status_codes, p=[0.9, 0.04, 0.02, 0.04])
        )
        byte_size = max(int(random.gauss(5000, 50)), 0)
        referer = faker.uri()
        user_agent = np.random.choice(self.user_agents, p=[0.5, 0.3, 0.1, 0.05, 0.05])()

        log_data = {
            "ip": ip,
            "timestamp": timestamp,
            "method": method,
            "resource": resource,
            "status_code": status_code,
            "byte_size": byte_size,
            "referer": referer,
            "user_agent": user_agent,
        }
        return log_data


class KafkaLogProducer:
    def __init__(self, brokers: str, linger_ms: int = 10000, batch_size: int = 100000):
        self.producer = KafkaProducer(
            bootstrap_servers=brokers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            linger_ms=linger_ms,
            batch_size=batch_size,
        )
        self.brokers = brokers
        self.status_code_partitions = {
            "200": 0,
            "404": 1,
            "500": 2,
            "301": 3,
        }

        # 브라우저별 토픽 정의를 위한 매핑
        self.browser_topics = {
            "Firefox": "web_log_firefox",
            "Chrome": "web_log_chrome",
            "Safari": "web_log_safari",
            "Internet Explorer": "web_log_ie",
            "Opera": "web_log_opera",
        }

        self.topics_created = False

    def get_browser_name(self, user_agent: str) -> str:
        """User Agent 문자열에서 브라우저 이름을 추출"""
        for browser in self.browser_topics.keys():
            if browser.lower() in user_agent.lower():
                return browser
        return "Firefox"  # 기본값

    def create_topics_with_partitions(self):
        if self.topics_created:
            return

        admin_client = KafkaAdminClient(bootstrap_servers=self.brokers)

        # 토픽 목록은 미리 정의된 브라우저 토픽 사용
        topic_names = list(self.browser_topics.values())

        # 기존 토픽 목록 조회
        existing_topics = admin_client.list_topics()

        # status_code 개수만큼 파티션 생성
        num_partitions = len(self.status_code_partitions)

        # 존재하지 않는 토픽만 생성
        topics_to_create = [
            NewTopic(name=topic, num_partitions=num_partitions, replication_factor=3)
            for topic in topic_names
            if topic not in existing_topics
        ]

        if topics_to_create:
            try:
                admin_client.create_topics(new_topics=topics_to_create)
                print(
                    f"Topics created: {', '.join([t.name for t in topics_to_create])}"
                )
            except KafkaError as e:
                print(f"Error creating topics: {e}")
        else:
            print("All topics already exist.")

        admin_client.close()
        self.topics_created = True

    def send_log(self, log_data: dict):
        if not self.topics_created:
            self.create_topics_with_partitions()

        # user_agent에서 브라우저 이름 추출
        browser_name = self.get_browser_name(log_data["user_agent"])
        # 브라우저 이름으로 토픽 결정
        topic = self.browser_topics[browser_name]
        # status_code에 따라 파티션 결정
        partition = self.status_code_partitions.get(log_data["status_code"], 0)

        self.producer.send(topic, value=log_data, partition=partition)

    def close(self):
        self.producer.flush()
        self.producer.close()


# Example instantiation and usage (assuming args are set up properly)
log_generator = LogGenerator(args.log_format)
kafka_producer = KafkaLogProducer(args.brokers, args.linger_ms, args.batch_size)

try:
    if args.topic:
        kafka_producer.create_topics_with_partitions()
    if args.num == 0:  # Infinite loop for continuous log generation
        while True:
            log_line = log_generator.generate_log_line()
            kafka_producer.send_log(log_line)
            if args.sleep > 0:
                time.sleep(args.sleep)
    else:  # Generate a specified number of log lines
        for _ in range(args.num):
            log_line = log_generator.generate_log_line()
            kafka_producer.send_log(log_line)
            if args.sleep > 0:
                time.sleep(args.sleep)
finally:
    kafka_producer.close()

from kafka import KafkaAdminClient
from kafka.admin import NewTopic

# Kafka 클러스터의 주소
kafka_bootstrap_servers = "node-kafka1:29092,node-kafka2:39092,node-kafka3:49092"
# Kafka AdminClient 객체 생성
admin_client = KafkaAdminClient(bootstrap_servers=kafka_bootstrap_servers)


def delete_all_topics():
    # 클러스터에서 모든 토픽을 조회합니다.
    topic_metadata = admin_client.list_topics()

    # 기본적으로 "_confluent"로 시작하는 내부 토픽은 제외할 수 있습니다.
    topics_to_delete = [
        topic for topic in topic_metadata if not topic.startswith("kafka")
    ]

    if not topics_to_delete:
        print("삭제할 토픽이 없습니다.")
        return

    # 삭제할 토픽 출력
    print(f"삭제할 토픽: {topics_to_delete}")
    try:
        # 토픽 삭제 요청
        admin_client.delete_topics(topics=topics_to_delete, timeout_ms=30000)
        print(f"토픽 삭제 요청을 보냈습니다: {topics_to_delete}")
    except Exception as e:
        print(f"토픽 삭제 중 오류 발생: {e}")


if __name__ == "__main__":
    delete_all_topics()

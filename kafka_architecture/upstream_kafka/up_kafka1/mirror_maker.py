import requests
import json


def create_mirror_maker_connector(
    connector_name: str = "mirror-maker-connector",
) -> dict:
    CONNECT_URL = "http://localhost:8083/connectors"
    connector_config = {
        "name": "mirror-maker-connector",
        "config": {
            "connector.class": "org.apache.kafka.connect.mirror.MirrorSourceConnector",
            "tasks.max": "25",
            "source.cluster.alias": "source-cluster",
            "source.cluster.bootstrap.servers": "kafka1:19092,kafka2:29092,kafka3:39092",
            "target.cluster.alias": "target-cluster",
            "target.cluster.bootstrap.servers": "node-kafka-1:49092,node-kafka-2:59092,node-kafka-3:59094",
            "topics": ".*",
            "topics.exclude": "^(kafka-configs|kafka-offsets|kafka-status|_schemas|__consumer_offsets|__transaction_state|prod)",
            "sync.topic.configs.enabled": "true",
            "sync.topic.acls.enabled": "false",
            "key.converter": "org.apache.kafka.connect.storage.StringConverter",
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter.schemas.enable": "false",
            "replication.factor": "1",  # 복제 계수를 1로 변경
            "offset.lag.max": "1000",  # 오프셋 지연 최대 값을 1000으로 변경
            "refresh.topics.interval.seconds": "60",  # 토픽 갱신 주기를 60초로 변경
            "topic.creation.enable": "false",
            "topic.creation.default.replication.factor": "1",
            "topic.creation.default.partitions": "5",
            "group.id": "mirror-maker-group",
            "security.protocol": "PLAINTEXT",
        },
    }

    try:
        response = requests.post(
            CONNECT_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(connector_config),
        )
        response.raise_for_status()
        print(f"MirrorMaker 커넥터 '{connector_name}' 생성 성공")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"MirrorMaker 커넥터 생성 실패: {str(e)}")
        if hasattr(e.response, "text"):
            print(f"에러 상세: {e.response.text}")
        return None


def delete_mirror_maker_connector(
    connector_name: str = "mirror-maker-connector",
) -> bool:
    CONNECT_URL = f"http://localhost:8083/connectors/{connector_name}"

    try:
        response = requests.delete(CONNECT_URL)
        response.raise_for_status()
        print(f"MirrorMaker 커넥터 '{connector_name}' 삭제 성공")
        return True
    except requests.exceptions.RequestException as e:
        print(f"MirrorMaker 커넥터 삭제 실패: {str(e)}")
        return False


def get_connector_status(connector_name: str = "mirror-maker-connector") -> dict:
    CONNECT_URL = f"http://localhost:8083/connectors/{connector_name}/status"

    try:
        response = requests.get(CONNECT_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"커넥터 상태 확인 실패: {str(e)}")
        if hasattr(e.response, "text"):
            print(f"에러 상세: {e.response.text}")
        return None


# 커넥터 생성
result = create_mirror_maker_connector()

# 커넥터 상태 확인
if result:
    status = get_connector_status()
    print(json.dumps(status, indent=2))

# 필요한 경우 커넥터 삭제
# delete_mirror_maker_connector()


def list_connectors():
    CONNECT_URL = "http://localhost:8083/connectors"
    try:
        response = requests.get(CONNECT_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"커넥터 목록 조회 실패: {str(e)}")
        return None


list_connectors()

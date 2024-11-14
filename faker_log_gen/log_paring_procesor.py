# Argument parsing
import argparse


parser = argparse.ArgumentParser(
    description="Fake Apache Log Generator with Kafka Support"
)
parser.add_argument(
    "--output",
    "-o",
    choices=["LOG", "GZ", "CONSOLE", "KAFKA"],
    help="Output type",
)
parser.add_argument(
    "--log-format",
    "-l",
    choices=["CLF", "ELF"],
    default="ELF",
    help="Log format",
)
parser.add_argument(
    "--num",
    "-n",
    type=int,
    default=1,
    help="Number of lines to generate (0 for infinite)",
)
parser.add_argument(
    "--prefix",
    "-p",
    type=str,
    help="Prefix for output file name",
)
parser.add_argument(
    "--sleep",
    "-s",
    type=float,
    default=0.0,
    help="Sleep duration between lines",
)
parser.add_argument(
    "--brokers",
    "-b",
    type=str,
    default="kafka1:19092,kafka2:29092,kafka3:39092",
    help="Kafka brokers (for Kafka output type only)",
)
parser.add_argument(
    "--linger-ms",
    type=int,
    default=10000,
    help="Maximum time in milliseconds to wait before sending a batch of messages",
)
parser.add_argument(
    "--batch-size",
    type=int,
    default=100000,
    help="Maximum batch size in bytes for Kafka producer",
)
parser.add_argument(
    "--topic",
    "-t",
    type=str,
    default="topic",
    help="topic_create",
)
args = parser.parse_args()

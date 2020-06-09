from py2neo import Graph, Node, Relationship
import json
import utils


class Neo4j:
    def __init__(self):
        # initialize the self.graph
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"), database="Database")

    def delete_all(self):
        self.graph.delete_all()

    def load_data(self, tweet):
        """
        :param tweet: a json doc with following schema
        {
            "type": "record",
            "name": "tweet",
            "keys" : [
                {"name": "company", "type": "string"},
                {"name": "sentiment", "type": "integer"},
                {"name": "id", "type": "string"},
                {"name": "date", "type": "string"},
                {"name": "time", "type": "string"},
                {"name": "retweet_count", "type": "integer"}
                {"name":"hashtags", "type":array}
                ]
        }
        :return: None
        """

        # retrieve company node from the remote self.graph
        company = self.graph.evaluate("MATCH(n) WHERE n.name = {company} return n", company=tweet["company"])
        # if remote node is null, create company node
        if company is None:
            company = Node("Company", name=tweet["company"])
            self.graph.create(company)
            # print("Node created:", company)

        # repeat above for all nodes
        tweet_node = self.graph.evaluate("MATCH(n) WHERE n.id = {id} return n", id=tweet["id"])
        if tweet_node is None:
            tweet_node = Node("Tweet", id=tweet["id"], sentiment=tweet["sentiment"], retweet_count=tweet["retweet_count"])
            self.graph.create(tweet_node)
            # print("Node created:", tweet_node)

        datetime = self.graph.evaluate("MATCH(n) WHERE n.time = {time} AND n.date = {date} return n",
                                  time=tweet["time"].split(":")[0]+':'+tweet["time"].split(':')[1],
                                  date=tweet["date"])
        if datetime is None:
            datetime = Node("DateTime", time=tweet["time"].split(":")[0]+':'+tweet["time"].split(":")[1], date=tweet["date"])
            self.graph.create(datetime)
            # print("Node created:", datetime)

        # create relationships
        # check if describes already exists
        describes = Relationship(tweet_node, "DESCRIBES", company)
        created_on = Relationship(tweet_node, "CREATED_ON", datetime)
        self.graph.create(describes)
        self.graph.create(created_on)
        # print("Relationships created")

        # create hashtag nodes and connect them with tweet nodes
        for hashtag in tweet["hashtags"]:
            hashtag_node = self.graph.evaluate("MATCH(n) WHERE n.name = {hashtag} return n", hashtag=hashtag)
            if hashtag_node is None:
                hashtag_node = Node("Hashtag", name=hashtag)
                self.graph.create(hashtag_node)
                contains_hashtag = Relationship(tweet_node, "CONTAINS_HASHTAG", hashtag_node)
                self.graph.create(contains_hashtag)
        # print("Hashtag nodes created")
        # print("Changes to self.graph complete")



if __name__ == "__main__":
    # read tweets files of different companies
    with open('Artifacts/google_tweets.json', 'r') as f:
        google_tweets = f.readlines()
    with open('Artifacts/apple_tweets.json', 'r') as f:
        apple_tweets = f.readlines()
    with open('Artifacts/apple_tweets.json', 'r') as f:
        huawei_tweets = f.readlines()

    # initialize the graph
    neo4j = Neo4j()

    # clear the self.graph
    neo4j.delete_all()

    # load the data in self.graph
    for tweet in google_tweets:
        # discard the tweets which don't have hashtag
        tweet_json = json.loads(tweet)
        if len(tweet_json["entities"]["hashtags"]) != 0:
            neo4j.load_data(utils.prune_tweet(tweet_json, 'google'))

    for tweet in apple_tweets:
        # discard the tweets which don't have hashtag
        tweet_json = json.loads(tweet)
        if len(tweet_json["entities"]["hashtags"]) != 0:
            neo4j.load_data(utils.prune_tweet(tweet_json, 'apple'))

    for tweet in huawei_tweets:
        # discard the tweets which don't have hashtag
        tweet_json = json.loads(tweet)
        if len(tweet_json["entities"]["hashtags"]) != 0:
            neo4j.load_data(utils.prune_tweet(tweet_json, 'huawei'))
import os
import unittest
from unittest.mock import patch

from embedchain import App
from embedchain.config import AppConfig, ElasticsearchDBConfig
from embedchain.vectordb.elasticsearch import ElasticsearchDB
from embedchain.embedder.gpt4all import GPT4AllEmbedder

class TestEsDB(unittest.TestCase):

    @patch("embedchain.vectordb.elasticsearch.Elasticsearch")
    def test_setUp(self, mock_client):
        self.db = ElasticsearchDB(config=ElasticsearchDBConfig(es_url="https://localhost:9200"))
        self.vector_dim = 384
        app_config = AppConfig(collection_name=False, collect_metrics=False)
        self.app = App(config=app_config, db=self.db)

        # Assert that the Elasticsearch client is stored in the ElasticsearchDB class.
        self.assertEqual(self.db.client, mock_client.return_value)

    @patch("embedchain.vectordb.elasticsearch.Elasticsearch")
    def test_query(self, mock_client):
        self.db = ElasticsearchDB(config=ElasticsearchDBConfig(es_url="https://localhost:9200"))
        app_config = AppConfig(collection_name=False, collect_metrics=False)
        self.app = App(config=app_config, db=self.db, embedder=GPT4AllEmbedder())

        # Assert that the Elasticsearch client is stored in the ElasticsearchDB class.
        self.assertEqual(self.db.client, mock_client.return_value)

        # Create some dummy data.
        embeddings = [[1, 2, 3], [4, 5, 6]]
        documents = ["This is a document.", "This is another document."]
        metadatas = [{}, {}]
        ids = ["doc_1", "doc_2"]

        # Add the data to the database.
        self.db.add(embeddings, documents, metadatas, ids, skip_embedding=False)

        search_response = {"hits":
            {"hits":
                [
                    {
                        "_source": {"text": "This is a document."},
                        "_score": 0.9
                    },
                    {
                        "_source": {"text": "This is another document."},
                        "_score": 0.8
                    }
                ]
            }
        }

        # Configure the mock client to return the mocked response.
        mock_client.return_value.search.return_value = search_response

        # Query the database for the documents that are most similar to the query "This is a document".
        query = ["This is a document"]
        results = self.db.query(query, n_results=2, where={}, skip_embedding=False)

        # Assert that the results are correct.
        self.assertEqual(results, ["This is a document.", "This is another document."])

    @patch("embedchain.vectordb.elasticsearch.Elasticsearch")
    def test_query_with_skip_embedding(self, mock_client):
        self.db = ElasticsearchDB(config=ElasticsearchDBConfig(es_url="https://localhost:9200"))
        app_config = AppConfig(collection_name=False, collect_metrics=False)
        self.app = App(config=app_config, db=self.db)

        # Assert that the Elasticsearch client is stored in the ElasticsearchDB class.
        self.assertEqual(self.db.client, mock_client.return_value)

        # Create some dummy data.
        embeddings = [[1, 2, 3], [4, 5, 6]]
        documents = ["This is a document.", "This is another document."]
        metadatas = [{}, {}]
        ids = ["doc_1", "doc_2"]

        # Add the data to the database.
        self.db.add(embeddings, documents, metadatas, ids, skip_embedding=True)

        search_response = {"hits":
            {"hits":
                [
                    {
                        "_source": {"text": "This is a document."},
                        "_score": 0.9
                    },
                    {
                        "_source": {"text": "This is another document."},
                        "_score": 0.8
                    }
                ]
            }
        }

        # Configure the mock client to return the mocked response.
        mock_client.return_value.search.return_value = search_response

        # Query the database for the documents that are most similar to the query "This is a document".
        query = ["This is a document"]
        results = self.db.query(query, n_results=2, where={}, skip_embedding=True)

        # Assert that the results are correct.
        self.assertEqual(results, ["This is a document.", "This is another document."])

    def test_init_without_url(self):
        # Make sure it's not loaded from env
        try:
            del os.environ["ELASTICSEARCH_URL"]
        except KeyError:
            pass
        # Test if an exception is raised when an invalid es_config is provided
        with self.assertRaises(AttributeError):
            ElasticsearchDB()

    def test_init_with_invalid_es_config(self):
        # Test if an exception is raised when an invalid es_config is provided
        with self.assertRaises(TypeError):
            ElasticsearchDB(es_config={"ES_URL": "some_url", "valid es_config": False})

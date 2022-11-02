# wiki-deepdive

An attempt to create a tree of connected links between Wikipedia pages to get to know Python

## To Run

Spin up a neo4J container provided in the docker compose file

```
docker compose up
```

Secondly, the script can be launched as follows

```
pip install requirements.txt
py ./wiki-deepdive.py
```

## To Monitor

The Neo4j dashboard can be accessed on port 7474 once started up.

### Worth mentioning queries

1) Amount of pages with references to specific page
    ``` Cypher
    MATCH (x:WikiPage)-[r]->()
    RETURN x.query as parent, count(*) as total_relations
    ORDER by total_relations DESC
    ```
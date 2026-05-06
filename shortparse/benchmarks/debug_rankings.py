from pprint import pprint

from shortparse.client import WarcraftLogsClient


def main():
    client = WarcraftLogsClient()

    query = """
    query {
      worldData {
        encounter(id: 3183) {
          characterRankings(
            difficulty: 5
            metric: dps
            className: "Mage"
            specName: "Frost"
          )
        }
      }
    }
    """

    data = client.graphql(query)
    pprint(data)


if __name__ == "__main__":
    main()
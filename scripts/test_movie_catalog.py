from src.retrieval.vector_store import VectorStore


def main():
    vector_store = VectorStore()

    movies = vector_store.get_movies()

    print("=" * 60)
    print("MOVIES IN CHROMADB")
    print("=" * 60)

    for movie in movies:
        print(movie)

    print(f"\nTotal unique movies: {len(movies)}")


if __name__ == "__main__":
    main()
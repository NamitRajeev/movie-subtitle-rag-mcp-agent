from src.agent.movie_resolver import MovieResolver


def main():
    resolver = MovieResolver()

    test_movies = [
        "Infinity War",
        "Avengers Infinity War",
        "Iron Man 2",
        "iron man 2",
        "The Batman",
        "",
    ]

    print("=" * 60)
    print("MOVIE RESOLVER TEST")
    print("=" * 60)

    for movie_name in test_movies:
        result = resolver.resolve(movie_name)

        print(f"\nInput: {movie_name!r}")
        print(f"Status: {result['status']}")
        print(f"Movie: {result['movie']}")
        print(f"Candidates: {result['candidates']}")


if __name__ == "__main__":
    main()
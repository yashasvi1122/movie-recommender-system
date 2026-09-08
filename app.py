import streamlit as st
import pickle
import requests


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="MovieVerse",
    page_icon="🎬",
    layout="wide"
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
}


/* Main heading */

.title {
    text-align: center;
    font-size: 55px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 0px;
}


.subtitle {
    text-align: center;
    font-size: 20px;
    color: #94a3b8;
    margin-bottom: 40px;
}


/* Recommendation section */

.section-title {
    font-size: 30px;
    font-weight: bold;
    color: white;
    margin-top: 40px;
    margin-bottom: 25px;
}


/* Movie card */

.movie-card {
    background-color: #1e293b;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #334155;
    min-height: 220px;
    margin-top: 10px;
}


/* Movie name */

.movie-name {
    font-size: 19px;
    font-weight: bold;
    color: white;
    margin-top: 12px;
    margin-bottom: 12px;
}


/* Movie details */

.movie-details {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.8;
}


/* Recommendation label */

.movie-type {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 15px;
}


/* Button styling */

.stButton > button {
    background-color: #e50914;
    color: white;
    font-size: 17px;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 10px;
}

.stButton > button:hover {
    background-color: #b20710;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------

movies_dict = pickle.load(
    open("movie_list.pkl", "rb")
)

movies = movies_dict["title"].values


similarity = pickle.load(
    open("similarity.pkl", "rb")
)


# ---------------- OMDb API KEY ----------------

api_key = "YOUR_API_KEY"


# ---------------- FETCH MOVIE DETAILS ----------------

def fetch_movie_details(movie_name):

    try:

        response = requests.get(
            "https://www.omdbapi.com/",
            params={
                "t": movie_name,
                "apikey": API_KEY
            },
            timeout=10
        )

        data = response.json()

        if data.get("Response") == "True":

            return {
                "poster": data.get("Poster"),
                "rating": data.get("imdbRating"),
                "genre": data.get("Genre"),
                "year": data.get("Year")
            }

    except Exception:
        pass

    return None


# ---------------- RECOMMEND FUNCTION ----------------

def recommend(movie):

    movie_index = movies_dict[
        movies_dict["title"] == movie
    ].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []

    for i in movie_list:

        recommended_movies.append(
            movies_dict.iloc[i[0]].title
        )

    return recommended_movies


# ---------------- HEADER ----------------

st.markdown(
    '<div class="title">🎬 MovieVerse</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Discover movies you will love • Powered by Machine Learning 🤖'
    '</div>',
    unsafe_allow_html=True
)


# ---------------- MOVIE SELECTION ----------------

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    selected_movie = st.selectbox(
        "🔍 Choose a movie you like",
        movies
    )

    recommend_button = st.button(
        "✨ RECOMMEND MOVIES",
        use_container_width=True
    )


# ---------------- RECOMMENDATIONS ----------------

if recommend_button:

    recommendations = recommend(selected_movie)

    st.markdown(
        '<div class="section-title">🎬 Recommended For You</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(5)

    for index, movie_name in enumerate(recommendations):

        with cols[index]:

            # Fetch movie details from OMDb
            movie_details = fetch_movie_details(movie_name)

            # ---------------- POSTER ----------------

            if (
                movie_details
                and movie_details["poster"]
                and movie_details["poster"] != "N/A"
            ):

                st.image(
                    movie_details["poster"],
                    width=200
                )

            else:

                st.write("🎬 Poster not available")


            # ---------------- MOVIE NAME ----------------

            st.markdown(
                f'<div class="movie-name">{movie_name}</div>',
                unsafe_allow_html=True
            )


            # ---------------- MOVIE DETAILS ----------------

            if movie_details:

                rating = movie_details["rating"]
                genre = movie_details["genre"]
                year = movie_details["year"]

                st.markdown(
                    f"""
                    <div class="movie-details">
                        ⭐ IMDb: {rating}<br>
                        🎭 {genre}<br>
                        📅 {year}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="movie-details">
                        Movie details not available
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ---------------- RECOMMENDATION TYPE ----------------

            st.markdown(
                """
                <div class="movie-type">
                    🤖 Content-Based Recommendation
                </div>
                """,
                unsafe_allow_html=True
            )
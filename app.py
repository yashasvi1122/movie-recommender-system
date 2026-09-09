import streamlit as st
import pickle
import requests
from io import BytesIO

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="MovieVerse",
    page_icon="🎬",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* Main background */

.stApp {
    background-color: #0f172a;
}


/* Remove unnecessary top spacing */

.block-container {
    padding-top: 2rem;
}


/* Main title */

.title {
    text-align: center;
    font-size: 58px;
    font-weight: 800;
    color: white;
    margin-bottom: 5px;
}


/* Subtitle */

.subtitle {
    text-align: center;
    font-size: 21px;
    color: #94a3b8;
    margin-bottom: 45px;
}


/* Section heading */

.section-title {
    font-size: 34px;
    font-weight: 800;
    color: white;
    margin-top: 55px;
    margin-bottom: 30px;
}


/* Selectbox text */

div[data-baseweb="select"] {
    font-size: 18px;
}


/* Make selectbox bigger */

div[data-baseweb="select"] > div {
    min-height: 55px;
}


/* Recommendation button */

.stButton > button {
    background-color: #e50914 !important;
    color: white !important;

    font-size: 20px !important;
    font-weight: bold !important;

    border-radius: 10px !important;
    border: none !important;

    min-height: 58px !important;

    padding: 12px 25px !important;

    width: 100% !important;

    transition: 0.3s;
}


/* Button hover */

.stButton > button:hover {
    background-color: #b20710 !important;
    color: white !important;
}


/* Movie information */

.movie-info {
    font-size: 15px;
    line-height: 1.8;
    color: #cbd5e1;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# LOAD MOVIE DATA
# ==================================================

try:

    movies_dict = pickle.load(
        open("movie_list.pkl", "rb")
    )

    similarity = pickle.load(
        open("similarity.pkl", "rb")
    )

except FileNotFoundError:

    st.error(
        "Movie data files not found. "
        "Make sure movie_list.pkl and similarity.pkl "
        "are in the same folder as app.py."
    )

    st.stop()


# Reset index to avoid similarity index problems

movies_dict = movies_dict.reset_index(drop=True)


# Get movie titles

movies = movies_dict["title"].values


# ==================================================
# LOAD OMDB API KEY
# ==================================================

try:

    API_KEY = st.secrets["OMDB_API_KEY"]

except Exception:

    st.error(
        "OMDb API key not found. "
        "Please check your Streamlit Secrets."
    )

    st.stop()


# ==================================================
# FETCH MOVIE DETAILS FROM OMDB
# ==================================================

@st.cache_data(show_spinner=False)
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


        # API request successful

        if data.get("Response") == "True":

            return {

                "poster": data.get(
                    "Poster",
                    "N/A"
                ),

                "rating": data.get(
                    "imdbRating",
                    "N/A"
                ),

                "genre": data.get(
                    "Genre",
                    "N/A"
                ),

                "year": data.get(
                    "Year",
                    "N/A"
                )

            }


        # Movie not found or API error

        return None


    except requests.exceptions.RequestException:

        return None


    except Exception:

        return None


# ==================================================
# MOVIE RECOMMENDATION FUNCTION
# ==================================================

def recommend(movie):

    # Find position of selected movie

    movie_index = movies_dict[
        movies_dict["title"] == movie
    ].index[0]


    # Get similarity scores

    distances = similarity[movie_index]


    # Sort movies according to similarity

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )


    # Remove selected movie and take 5 recommendations

    movie_list = movie_list[1:6]


    recommended_movies = []


    for i in movie_list:

        movie_name = movies_dict.iloc[
            i[0]
        ].title


        recommended_movies.append(
            movie_name
        )


    return recommended_movies


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="title">🎬 MovieVerse</div>',
    unsafe_allow_html=True
)


st.markdown(
    '''
    <div class="subtitle">
        Discover movies you will love • Powered by Machine Learning 🤖
    </div>
    ''',
    unsafe_allow_html=True
)


# ==================================================
# MOVIE SELECTION AREA
# ==================================================

# Create a centered area

left_space, main_area, right_space = st.columns(
    [1, 2.5, 1]
)


with main_area:

    selected_movie = st.selectbox(
        "🔍 Choose a movie you like",
        movies
    )


    # Center the recommendation button

    button_left, button_center, button_right = st.columns(
    [0.5, 3, 0.5]
    )


    with button_center:

        recommend_button = st.button(
            "✨ RECOMMEND MOVIES"
        )


# ==================================================
# RECOMMENDATIONS
# ==================================================

if recommend_button:

    # Get recommended movies

    recommendations = recommend(
        selected_movie
    )


    # Section heading

    st.markdown(
        '<div class="section-title">'
        '🎬 Recommended For You'
        '</div>',
        unsafe_allow_html=True
    )


    # Create 5 columns

    cols = st.columns(5)


    # ==================================================
    # DISPLAY EACH MOVIE
    # ==================================================

    for index, movie_name in enumerate(
        recommendations
    ):

        with cols[index]:

            # ------------------------------------------
            # FETCH MOVIE DETAILS
            # ------------------------------------------

            movie_details = fetch_movie_details(
                movie_name
            )


            # ------------------------------------------
            # POSTER
            # ------------------------------------------

            if (
                movie_details is not None
                and movie_details.get("poster")
                and movie_details["poster"] != "N/A"
            ):

                try:

                    poster_response = requests.get(
                        movie_details["poster"],
                        headers={
                            "User-Agent": "Mozilla/5.0"
                        },
                        timeout=15
                    )


                    if poster_response.status_code == 200:

                        poster_image = BytesIO(
                            poster_response.content
                        )


                        st.image(
                            poster_image,
                            use_column_width=True
                        )

                    else:

                        st.info(
                            "🎬 Poster not available"
                        )


                except Exception:

                    st.info(
                        "🎬 Poster not available"
                    )


            else:

                st.info(
                    "🎬 Poster not available"
                )


            # ------------------------------------------
            # GET MOVIE DETAILS
            # ------------------------------------------

            if movie_details is not None:

                rating = movie_details.get(
                    "rating",
                    "N/A"
                )

                genre = movie_details.get(
                    "genre",
                    "N/A"
                )

                year = movie_details.get(
                    "year",
                    "N/A"
                )

            else:

                rating = "N/A"

                genre = "N/A"

                year = "N/A"


            # ------------------------------------------
            # MOVIE CARD
            # ------------------------------------------

            st.markdown("---")


            # Movie name

            st.markdown(
                f"### 🎬 {movie_name}"
            )


            # Movie information

            st.markdown(
                f"""
                ⭐ **IMDb Rating:** {rating}

                🎭 **Genre:** {genre}

                📅 **Year:** {year}
                """
            )


            # Recommendation type

            st.caption(
                "🤖 Content-Based Recommendation"
            )
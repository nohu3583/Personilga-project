import streamlit as st
from transform import (
    get_average_daily_prices,
    get_current_prices,
    get_extreme_prices,
    get_todays_average_price, 
    get_tommorows_prices
)


st.title("Swedish Electricity Prices")


with st.sidebar:

    st.caption("Applies to both Historical Data and Daily Statistics")
    selected_area = st.selectbox(
        "Price Area",
        ["SE1", "SE2", "SE3", "SE4"]
    )

    st.caption("Applies to the historical chart only")
    selected_range = st.selectbox(
        "Time Range",
        ["1 week", "1 month", "1 year", "All"]
    )

range_map = {
    "1 week": 7,
    "1 month": 30,
    "1 year": 365,
    "All": None
}

days_back = range_map[selected_range]



@st.cache_data
def load_history(area, limit):
    return get_average_daily_prices(area, limit)


@st.cache_data(ttl=3600)
def load_current():
    return get_current_prices()

@st.cache_data(ttl=3600)
def load_tommorow(area):
    return get_tommorows_prices(area)


historical_df = load_history(
    selected_area,
    days_back
)


st.subheader("Historical Average Daily Price")
st.line_chart(
    historical_df.set_index("day")["avg_price_sek"]
)

tommorow_df = load_tommorow(selected_area)
st.caption("Prices are predictory, please double check tommorow that these are accurate")
st.subheader("Tommorows Prices")

if tommorow_df.empty:
      st.info("Tomorrow's prices aren't published yet — check back after 2 PM.")
else:
      st.line_chart(tommorow_df.set_index("Time_beginning_period")["Price_SEK_per_kWh"])


current_df = load_current()
current_df = current_df.sort_values("Price_Area")


st.subheader("Current Price by Area (Price per kWh)")

cols = st.columns(len(current_df))

for col, (_, row) in zip(cols, current_df.iterrows()):
    col.metric(
        label=row["Price_Area"],
        value=f"{row['Price_SEK_per_kWh']:.3f} SEK"
    )

@st.cache_data(ttl=3600)
def load_extremes(area):
    highest = get_extreme_prices(area=area, order="DESC", limit=1)
    lowest = get_extreme_prices(area=area, order="ASC", limit=1)
    return highest, lowest

@st.cache_data(ttl=3600)
def load_todays_average(area):
    return get_todays_average_price(area=area)

highest_df, lowest_df = load_extremes(selected_area)
todays_avg_df = load_todays_average(selected_area)

current_price_row = current_df[current_df["Price_Area"] == selected_area].iloc[0]

st.subheader(f"Daily Statistics — {selected_area}")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Price", f"{current_price_row['Price_SEK_per_kWh']:.3f} SEK")
col2.metric("Today's Average", f"{todays_avg_df.iloc[0]['avg_price']:.3f} SEK")
col3.metric("Highest Hour", f"{highest_df.iloc[0]['Price_SEK_per_kWh']:.3f} SEK",
            help=highest_df.iloc[0]['Time_beginning_period'])
col4.metric("Lowest Hour", f"{lowest_df.iloc[0]['Price_SEK_per_kWh']:.3f} SEK",
            help=lowest_df.iloc[0]['Time_beginning_period'])


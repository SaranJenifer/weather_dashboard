import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import date
from utils import (
    get_current_weather,
    get_historical_weather,
    get_air_quality,
    get_additional_weather_data,
    get_forecast_weather
)

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌤 Weather Dashboard")
st.caption("Real-time insights • Historical analytics • Forecast intelligence")

# =====================================================
# SIDEBAR INPUT PANEL
# =====================================================
with st.sidebar:
    st.header("🔎 Explore Weather Data")

    city = st.text_input("Enter place name")

    if st.button("Refresh Dashboard",
                 use_container_width=True):
        st.cache_data.clear()
        st.rerun()
       

    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")

    compare_city = st.text_input(
        "Optional: Compare with another city"
    )
    st.sidebar.info("💡 Example: Bengaluru, Chennai, Delhi, Mumbai")
         
    city_entered = bool(city.strip())

    if not city_entered:
        st.info("Enter a city to enable dashboard features.")

# Date validation
date_error = None
if start_date > end_date:
    date_error = "Start date must be before end date."
if start_date > date.today():
    date_error = "Start date cannot be in the future."

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "📍 Current Weather",
    "📈 Historical Analysis",
    "📅 Forecast Outlook"
])

# =====================================================
# =====================================================
# CURRENT WEATHER TAB
# =====================================================
with tab1:

    st.subheader("Current Conditions")

    if st.button("Get Current Weather", 
                 disabled=not city_entered):

        with st.spinner("Fetching real-time weather..."):
            current = get_current_weather(city)

        if current is None:
            st.error("City not found or API issue.")
            st.stop()

        weather_datetime = pd.to_datetime(current["dt"], unit="s")

        st.markdown(
            f"### {weather_datetime.strftime('%A, %d %B %Y')}"
        )

        # ============================
        # EXTRACT VALUES
        # ============================

        temp = current["main"]["temp"]
        humidity = current["main"]["humidity"]
        wind_speed = current["wind"]["speed"]
        pressure = current["main"]["pressure"]
        visibility = current.get("visibility", "N/A")  # <-- Added visibility

        lat = current["coord"]["lat"]
        lon = current["coord"]["lon"]

        # ============================
        # GET AIR QUALITY
        # ============================

        air_quality = get_air_quality(lat, lon)

        if air_quality:
            aqi = air_quality["list"][0]["main"]["aqi"]
        else:
            aqi = "N/A"

        # ============================
        # ROW 1 METRICS
        # ============================

        col1, col2, col3 = st.columns(3)
        col1.metric("🌡 Temperature (°C)", temp)
        col2.metric("💧 Humidity (%)", humidity)
        col3.metric("🌬 Wind Speed (m/s)", wind_speed)

        st.divider()

        # ============================
        # ROW 2 METRICS
        # ============================

        col4, col5, col6 = st.columns(3)
        col4.metric("🌪 Pressure (hPa)", pressure)
        col5.metric("🌫 Air Quality Index", aqi)
        col6.metric("👁️ Visibility (m)", visibility)  # <-- Replaced UV Index with Visibility

        st.divider()

        # ============================
        # Weather Summary Chart
        # ============================

        summary_df = pd.DataFrame({
            "Category": ["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)"],
            "Value": [temp, humidity, wind_speed]
        })

        fig_summary = px.bar(
            summary_df,
            x="Category",
            y="Value",
            text="Value",
            color="Category"
        )
        fig_summary.update_traces(textposition="outside")

        st.plotly_chart(fig_summary, use_container_width=True)
# =====================================================
# HISTORICAL TAB
# =====================================================
with tab2:

    st.subheader("📊 Weather Analytics")

    if date_error:
        st.warning(date_error)

    if st.button("Generate Historical Report",
                 disabled=(not city_entered or bool(date_error))):

        with st.spinner("Analyzing historical trends..."):
            history = get_historical_weather(
                city,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )

        if not history or "error" in history:
            st.error(history.get("error",
                                 "Failed to retrieve historical data."))
            st.stop()

        # =============================
        # DATAFRAME
        # =============================
        df = pd.DataFrame({
            "Date": pd.to_datetime(
                [d["datetime"] for d in history["days"]]
            ),
            "Temperature (°C)":
                [d.get("temp") for d in history["days"]],
            "Humidity (%)":
                [d.get("humidity") for d in history["days"]],
            "Precipitation (mm)":
                [d.get("precip") for d in history["days"]],
        }).sort_values("Date")

        st.subheader("📄 Historical Data")
        st.dataframe(df, use_container_width=True)

        # ======================================================
        # 🌡 TEMPERATURE ANALYTICS SECTION
        # ======================================================

        st.markdown("## 🌡 Temperature Analytics")
        st.divider()

        avg_temp = round(df["Temperature (°C)"].mean(), 2)
        max_temp = round(df["Temperature (°C)"].max(), 2)
        min_temp = round(df["Temperature (°C)"].min(), 2)

        st.markdown("### 📊 Temperature Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Average Temp (°C)", avg_temp)
        col2.metric("Maximum Temp (°C)", max_temp)
        col3.metric("Minimum Temp (°C)", min_temp)

        st.divider()
        st.subheader("📈 Temperature Trend")

        fig_temp = px.line(
            df,
            x="Date",
            y="Temperature (°C)",
            markers=True
        )

        st.plotly_chart(fig_temp, use_container_width=True)


        # =======================HUMIDITY TREND==============================
        
        st.subheader("💧 Humidity Variation")

        humidity_fig = px.line(
            df,
            x="Date",
            y="Humidity (%)",
            markers=True,
            title="Humidity Trend"
        )

        st.plotly_chart(humidity_fig, use_container_width=True)



        #comparision b/w temp and humidity
        st.markdown("### 📊 Temperature vs Humidity Comparison")
        compare_df = df[["Date", "Temperature (°C)", "Humidity (%)"]].set_index("Date")
        st.bar_chart(compare_df)

        # =====================================================
        # 🌧 PRECIPITATION LEVELS
        # =====================================================
        st.subheader("🌧 Precipitation Levels")

        precip_fig = px.bar(
            df,
            x="Date",
            y="Precipitation (mm)",
            title="Precipitation Over Time"
        )

        st.plotly_chart(precip_fig, use_container_width=True)

        

        #=====================================================
        # CORRELATION HEATMAP
        # =====================================================

        st.subheader("🔥 Correlation Heatmap")

        corr = df[[
            "Temperature (°C)",
            "Humidity (%)",
            "Precipitation (mm)"
        ]].corr()

        heatmap = alt.Chart(
            corr.reset_index().melt("index")
        ).mark_rect().encode(
            x="index:N",
            y="variable:N",
            color="value:Q"
        )

        st.altair_chart(heatmap,
                        use_container_width=True)

       
        # MULTI-CITY COMPARISON
        # =====================================================
        if compare_city.strip():

            st.markdown("---")
            st.markdown("## 🌍 Multi-City Comparison")

            city_list = [city.strip()]
            city_list += [
                c.strip() for c in compare_city.split(",")
                if c.strip()
            ]

            comparison_daily_df = pd.DataFrame()

            with st.spinner("Fetching comparison data..."):
                for city_name in city_list:

                    history_data = get_historical_weather(
                        city_name,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d")
                    )

                    if history_data and "days" in history_data:
                        temp_data = pd.DataFrame({
                            "Date": pd.to_datetime(
                                [d["datetime"] for d in history_data["days"]]
                            ),
                            "Temperature": [
                                d.get("temp")
                                for d in history_data["days"]
                            ],
                            "City": city_name
                        })

                        comparison_daily_df = pd.concat(
                            [comparison_daily_df, temp_data]
                        )

            if not comparison_daily_df.empty:

                # =========================================
                # DAILY LINE COMPARISON
                # =========================================
                st.markdown("### 📈 Daily Temperature Comparison")

                fig_line = px.line(
                    comparison_daily_df,
                    x="Date",
                    y="Temperature",
                    color="City",
                    markers=True
                )

                st.plotly_chart(fig_line, use_container_width=True)

                # =========================================
                # TEMPERATURE DISTRIBUTION (BOX)
                # =========================================
                st.markdown("Temperature Distribution")

                fig_box = px.box(
                    comparison_daily_df,
                    x="City",
                    y="Temperature",
                    color="City"
                )

                st.plotly_chart(fig_box, use_container_width=True)

                # =========================================
                # PIVOT TABLE (DATE vs CITY)
                # =========================================
                st.markdown("Comparison Table")

                pivot_df = comparison_daily_df.pivot(
                    index="Date",
                    columns="City",
                    values="Temperature"
                )

                st.dataframe(pivot_df, use_container_width=True)

                # =========================================
                # DIFFERENCE FROM PRIMARY CITY
                # =========================================
                st.markdown("### 🔎 Difference from Primary City")

                primary_city = city_list[0]

                if primary_city in pivot_df.columns:

                    diff_df = pivot_df.subtract(
                        pivot_df[primary_city],
                        axis=0
                    )

                    diff_df = diff_df.drop(
                        columns=[primary_city]
                    )

                    st.dataframe(diff_df,
                                 use_container_width=True)

                    fig_diff = px.line(
                        diff_df,
                        x=diff_df.index,
                        y=diff_df.columns,
                        title=f"Temperature Difference from {primary_city}"
                    )

                    st.plotly_chart(fig_diff,
                                    use_container_width=True)  
        


        # ========================CSV DOWNLOAD=============================
        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name="historical_weather.csv",
            mime="text/csv"
        )


# =======================FORECAST TAB==============================
with tab3:

    st.subheader("5-Day Forecast")

    if st.button("Get Forecast",
                 disabled=not city_entered):

        with st.spinner("Fetching forecast data..."):
            forecast = get_forecast_weather(city)

        if forecast is None:
            st.error("Forecast unavailable.")
            st.stop()

        daily_data = forecast["list"][::8]

        for day in daily_data:

            date_label = pd.to_datetime(
                day["dt"], unit="s"
            ).strftime("%A, %b %d")

            temp_max = day["main"]["temp_max"]
            temp_min = day["main"]["temp_min"]
            description = day["weather"][0]["description"].title()
            icon = day["weather"][0]["icon"]

            icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"

            col1, col2, col3 = st.columns([3,1,2])

            with col1:
                st.markdown(f"**{date_label}**")
                st.caption(description)

            with col2:
                st.image(icon_url, width=60)

            with col3:
                st.metric("Max / Min",
                          f"{temp_max:.1f}° / {temp_min:.1f}°")

            st.divider()

       
        # Extract forecast list safely
        forecast_list = forecast.get("list", [])

        if forecast_list:

            # Create clean forecast data
            forecast_data = []

            for item in forecast_list:
                forecast_data.append({
                    "datetime": item.get("dt_txt"),
                    "temp": item.get("main", {}).get("temp"),
                    "humidity": item.get("main", {}).get("humidity")
                })

            # Create DataFrame
            df_forecast = pd.DataFrame(forecast_data)

            # Convert datetime column
            df_forecast["datetime"] = pd.to_datetime(df_forecast["datetime"])

            # ---------------------------
            # Forecast Table
            # ---------------------------
            st.markdown("### 📋 Forecast Table")
            st.dataframe(df_forecast, use_container_width=True)

            st.markdown("---")

            # ---------------------------
            # Temperature Trend
            # ---------------------------
            st.markdown("### 🌡 Forecast Temperature Trend")
            st.line_chart(
                df_forecast.set_index("datetime")["temp"],
                use_container_width=True
            )

            st.markdown("---")

            # ---------------------------
            # Humidity Trend
            # ---------------------------
            st.markdown("### 💧 Forecast Humidity Trend")
            st.area_chart(
                df_forecast.set_index("datetime")["humidity"],
                use_container_width=True
            )

            st.markdown("---")

            # ---------------------------
            # Comparison Chart
            # ---------------------------
            st.markdown("### 📊 Temperature vs Humidity Comparison")

            compare_forecast_df = df_forecast[
                ["datetime", "temp", "humidity"]
            ].set_index("datetime")

            st.bar_chart(compare_forecast_df, use_container_width=True)

        else:
            st.error("Forecast data not available.")
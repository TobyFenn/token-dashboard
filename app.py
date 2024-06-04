import requests
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

# Function to create an interactive table
def aggrid_interactive_table(df: pd.DataFrame):
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )
    options.configure_side_bar()
    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme='alpine',
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )
    return selection

# Make an API request to get the top 10 cryptocurrencies by market cap
url = "https://min-api.cryptocompare.com/data/top/mktcapfull?limit=10&tsym=USD"
response = requests.get(url).json()

# Extract the relevant data from the API response
data = [
    {
        'Name': coin['CoinInfo']['Name'],
        'Market Cap (USD)': coin['RAW']['USD']['MKTCAP'],
        'Volume (USD)': coin['RAW']['USD']['TOTALVOLUME24HTO'],
        'Volume (Coin)': coin['RAW']['USD']['TOTALVOLUME24H']
    }
    for coin in response['Data']
]

# Create a DataFrame from the extracted data
df = pd.DataFrame(data)

# Display the title and expanders
st.set_page_config(page_title='Token filter dashboard', page_icon='🇺🇸')
st.title('🇺🇸 Token filter dashboard')
st.markdown('tfenner@usc.edu')

with st.expander('Filter criteria'):
    st.markdown('**How are tokens restricted?**')
    st.markdown('* 10m-400m mcap')
    st.markdown('* Trading on Bybit, bn, okx')    
    st.markdown('')
    st.markdown('im going to sleep now but to come next: more intelligent querying, better filtering, data viz, alerts')


# Wrap the code inside a form
with st.form(key='data_editor_form'):
    st.title('Heuristic scoring distribution')
    # User input fields for criteria
    volume_5x_cutoff = st.number_input('Volume 5x larger than past 10 days avg', value=5)
    volume_10x_cutoff = st.number_input('Volume 10x larger than past day avg', value=10)
    volume_50_pct_cutoff = st.number_input('Volume larger than % of market cap', value=0.5)
    volume_100_pct_cutoff = st.number_input('Volume larger than % of market cap', value=1)
    volume_200_pct_cutoff = st.number_input('Volume larger than % of market cap', value=2)
    
    st.title('Summary')
    st.markdown(f'* ⁠volume <u>{volume_5x_cutoff}x</u> larger than past 10 days avg', unsafe_allow_html=True)
    st.markdown(f'* ⁠⁠volume <u>{volume_10x_cutoff}x</u> larger than past day avg', unsafe_allow_html=True)
    st.markdown(f'* ⁠volume larger than <u>{volume_50_pct_cutoff*100:.0f}%</u> of market cap', unsafe_allow_html=True)
    st.markdown(f'* ⁠⁠volume larger than <u>{volume_100_pct_cutoff*100:.0f}%</u> of market cap', unsafe_allow_html=True)
    st.markdown(f'* ⁠volume larger than <u>{volume_200_pct_cutoff*100:.0f}%</u> of market cap ⁠', unsafe_allow_html=True)

    submit_button = st.form_submit_button(label='Submit')
    st.markdown('if error then resubmit')

    # Assign points based on criteria
    
    df['Volume 5x Points'] = df.apply(lambda x: 1 if x['Volume (USD)'] > volume_5x_cutoff * x['Market Cap (USD)'] / 10 else 0, axis=1)
    df['Volume 10x Points'] = df.apply(lambda x: 1 if x['Volume (USD)'] > volume_10x_cutoff * x['Market Cap (USD)'] else 0, axis=1)
    df['Volume 50% Points'] = df.apply(lambda x: 1 if x['Volume (Coin)'] > volume_50_pct_cutoff * x['Market Cap (USD)'] else 0, axis=1)
    df['Volume 100% Points'] = df.apply(lambda x: 1 if x['Volume (Coin)'] > volume_100_pct_cutoff * x['Market Cap (USD)'] else 0, axis=1)
    df['Volume 200% Points'] = df.apply(lambda x: 1 if x['Volume (Coin)'] > volume_200_pct_cutoff * x['Market Cap (USD)'] else 0, axis=1)

    # Calculate the total points for each coin
    df['Total Points'] = df['Volume 5x Points'] + df['Volume 10x Points'] + df['Volume 50% Points'] + df['Volume 100% Points'] + df['Volume 200% Points']

    # Sort the DataFrame by total points in descending order
    df = df.sort_values('Total Points', ascending=False)
    
        # Move the 'Total Points' column to the leftmost position
    total_points_column = df.pop('Total Points')
    df.insert(0, 'Total Points', total_points_column)

    # Display the interactive table with the top 10 cryptocurrencies
    edited_df = aggrid_interactive_table(df)
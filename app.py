import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from Currencies import currency_list, currencies
from config import headers


st.set_page_config(page_title="Currency Converter App")
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
        width: 325px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
        width: 500px;
        margin-left: -500px;
    }
     
    """,
    unsafe_allow_html=True,
)


st.title('Currency Converter App')
st.markdown("""
This app interconverts the value of foreign currencies!

""")

def index(curr):
    '''
    Returns the index of the currency `curr` in the currency_list
    
    '''
    for i in range(len(currency_list)):
        if curr == currency_list[i]:
            return i

# initialize session_state variables
if 'amnt' not in st.session_state:
    st.session_state.amnt = 1.
if 'bp_unit' not in st.session_state and 'sp_unit' not in st.session_state:
    st.session_state.bp_unit, st.session_state.sp_unit = "USD", "INR"
if 'gen' not in st.session_state:
    st.session_state.gen = 0


placeholder = st.sidebar.empty() # sidebar initialised

with placeholder.container():
    # initial Interface
    
    st.header('Input Options')
    amount = st.number_input('Amount', value=float(st.session_state.amnt))
    base_price_unit = st.selectbox('From', currency_list, index=index(st.session_state.bp_unit))
    swap = st.button("Swap")
    symbols_price_unit = st.selectbox('To', currency_list, index=index(st.session_state.sp_unit))
    
    st.session_state.amnt = amount
    st.session_state.bp_unit, st.session_state.sp_unit = base_price_unit, symbols_price_unit
    # Update the session_state variables
    
    st.session_state.gen += 1
     
if swap:
    # When the User wants to swap 
    
    placeholder.empty()
    
    with placeholder.container():
        st.header('Input Options')
        amount = st.number_input('Amount', value=float(st.session_state.amnt), key=0)
        base_price_unit = st.selectbox('From', currency_list, key=1, index = index(st.session_state.sp_unit) )
        switch = st.button("Switch", key=2)
        symbols_price_unit = st.selectbox('To', currency_list, key=3, index = index(st.session_state.bp_unit) )
        
        st.session_state.amnt = amount
        st.session_state.bp_unit, st.session_state.sp_unit = base_price_unit, symbols_price_unit
        
        st.experimental_rerun() # needed for proper reset of webpage

elif (st.session_state.gen%2) == 0:
    st.experimental_rerun()
    
def load_data():
    '''
    Generate the output.
    '''
    
    # Making the API Request
    url = f"https://api.apilayer.com/exchangerates_data/latest?base={base_price_unit}&symbols={symbols_price_unit}"
    response = requests.request("GET", url, headers=headers) 
    result = response.json()
    if "success" not in result.keys():
        st.info("Sorry to say, but the API Use Limit has been exceeded.")
        exit()
    
    # create the Dataframe
    from_cur = pd.Series([base_price_unit], name = "From")
    to_cur = pd.Series([symbols_price_unit], name = "To")
    amnt = pd.Series([amount], name = "Amount")
    rate = pd.Series(result["rates"][symbols_price_unit], name = "Rate")
    value = pd.Series([round(amount*rate[0], 2)][0], name = "Value")
    timestamp = result["timestamp"]
    
    time = datetime.fromtimestamp(timestamp).strftime('%I:%M:%S %p %Z %d-%m-%Y')
    conversion_date = pd.Series(time, name = "At")
    
    df = pd.concat( [amnt, from_cur, value, to_cur, rate, conversion_date], axis=1 )
    df.index = ["Result"]
    return df

expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** streamlit, pandas, requests
* **API details:** [Exchange Rates Data API](https://apilayer.com/marketplace/exchangerates_data-api#documentation-tab) 
""")

with st.spinner("Calculating..."):
    df = load_data()
    st.header('Currency conversion')
    st.dataframe(df, use_container_width=True)
    st.write(base_price_unit, " - ", currencies[base_price_unit])
    st.write(symbols_price_unit, " - ", currencies[symbols_price_unit])
    
    st.info("If the value is not visible completely, try expanding the Value column.")

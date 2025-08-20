import streamlit as st
import pandas as pd
import pyodbc
from streamlit_dynamic_filters import DynamicFilters
import datetime
from matplotlib import pyplot as mplt
import seaborn as sbn
from streamlit_option_menu import option_menu
import plotly.express as px
from streamlit_card import card

st.set_page_config(layout="wide")
#st.title("Food Waste Management System")
st.markdown("""
    <div style='
        background-color: #1E1E1E;
        padding: 10px;
        border: 1px solid #1E90FF;
        border-radius: 1px;
        text-align: center;
        color: #13dfd5ff;
        font-size: 50px;
        font-weight: bold;
        margin-bottom: 10px;
    '>
        Food Waste Management System
    </div>
""", unsafe_allow_html=True)

def get_connection():
    secrets = st.secrets["sqlserver"]
    conn = pyodbc.connect(
        f'DRIVER={secrets["driver"]};'
        f'SERVER={secrets["server"]};'
        f'DATABASE={secrets["database"]};'
    )
    return conn 

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query,conn)
    conn.close()
    return df 

with st.sidebar:
    selected = option_menu(
    "Navigation", ["Home", "Food Waste Management", "Contact"],
    icons=['house', 'recycle', 'person'], default_index=0)

#st.markdown(f"## Welcome to the {selected} Page")

if selected == "Home":
    try:
#     #background image
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(
                rgba(0, 0, 0, 0.4), 
                rgba(0, 0, 0, 0.4)
            ), 
            url("https://info.ehl.edu/hubfs/Blog-EHL-Insights/Blog-Header-EHL-Insights/AdobeStock_264542845.jpeg");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }
        </style>
    """, unsafe_allow_html=True)

        #card
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        .card {
            background-color: rgba(255, 255, 255, 0.1);  /* semi-transparent white */
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            backdrop-filter: blur(10px);  /* adds a frosted-glass effect */
            -webkit-backdrop-filter: blur(10px); /* for Safari */
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            color: white;
            text-align: center;
            margin-top: 20px;
        }
        .card-title {
            font-size: 18px;
            font-weight: 400;
            color: #13dfd5ff;
            margin-bottom: 0.5rem;
        }
        .card-value {
            font-size: 32px;
            font-weight: 700;
            color: #13dfd5ff;
        }
        </style>
        """, unsafe_allow_html=True)

        
        query = "select sum(quantity) as TotalQuantity from food_listings"
        df_quantity = run_query(query)
        quantity = df_quantity['TotalQuantity'].tolist()

        query = "select count(claim_ID) as ClaimCount from Claims where status='Completed'"
        df_clcount = run_query(query)
        clcount = df_clcount['ClaimCount'].tolist()

        query = "select count(provider_ID) as count from providers"
        df_provcount = run_query(query)
        provcount = df_provcount['count'].tolist()

        query = "select count(receiver_ID) as count from receivers"
        df_recvcount = run_query(query)
        recvcount = df_recvcount['count'].tolist()

        cols = st.columns(4)

        with cols[0]:
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">Total Food Quantity</div>
                    <div class="card-value">{quantity[0]:,}</div>
                </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">No. of Successful Claims</div>
                    <div class="card-value">{clcount[0]:,}</div>
                </div>
            """, unsafe_allow_html=True)

        with cols[2]:
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">Total No. of Providers</div>
                    <div class="card-value">{provcount[0]:,}</div>
                </div>
            """, unsafe_allow_html=True)   

        with cols[3]:
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">Total No. of Receivers</div>
                    <div class="card-value">{recvcount[0]:,}</div>
                </div>
            """, unsafe_allow_html=True)   
            
    except Exception as e:        
        st.error("An unexpected error occurred: {e}")
          

if selected == "Food Waste Management":
    tab1, tab2, tab3, tab4 = st.tabs(["Food Listings","Manage Food Claims", "Listing Details", "Data Visualisations",])


    with tab1:
    #filter data
        try:
            col1, col2 = st.columns([1.75, 6])  # Adjust ratio as needed

            with col1:
                
                query = "select * from food_listings"
                df_FoodListing = run_query(query)

                filters = ['Provider_Type', 'Food_Type', 'Location', 'Food_Name']  
                dynamic_filters = DynamicFilters(df_FoodListing, filters=filters)

                #Display UI
                st.write(":primary[Filter Options]")
                dynamic_filters.display_filters()


            with col2:
                           
                #Show results
                st.subheader("Food Listings")
                dynamic_filters.display_df()
        
        except Exception as e:        
            st.error("An unexpected error occurred: {e}")

    with tab3:
    #1. Food providers in each city
        try:
            
            st.subheader("Food providers count in each city")
            query = "select City, count(name) as ProviderCount from providers group by city order by ProviderCount desc"
            df_provider = run_query(query)
            st.dataframe(df_provider, hide_index=True)        

            #Food receivers in each city
            st.subheader("Food receivers count in each city")
            query = "select City, count(name) as ReceiverCount from receivers group by city order by ReceiverCount desc"
            df = run_query(query)
            st.dataframe(df, hide_index=True)

            #2.Which type of food provider (restaurant, grocery store, etc.) contributes the most food?
            st.subheader("Food provider type that contributes the most food")
            query = "select Provider_type, count(provider_type) as FoodProvidedCount from food_listings group by Provider_Type order by FoodProvidedCount desc"
            df_foodProvider = run_query(query)
            st.dataframe(df_foodProvider, hide_index=True)

            #4.Which receivers have claimed the most food?
            st.subheader("Receivers who have claimed the most food")
            query = "select City, count(name) as ReceiverCount from receivers group by city order by ReceiverCount desc"
            df = run_query(query)
            st.dataframe(df, hide_index=True)

            #5. Food Listings & Availability 
            #total quantity of food available from all providers
            st.subheader("Total quantity of food available from all providers")
            query = "select sum(quantity) as TotalQuantity from food_listings"
            df_quantity = run_query(query)
            st.dataframe(df_quantity, hide_index=True)

            #6.Which city has the highest number of food listings?
            st.subheader("Cities with highest number of food listings")
            query = "select top 10 Location, count(location) as Count from food_listings group by location order by Count desc"
            df_cities = run_query(query)
            st.dataframe(df_cities, hide_index=True)

            #7.most commonly available food types
            st.subheader("Most commonly available food types")
            query = "select Food_type, count(food_type) as Count from food_listings group by Food_Type order by Count desc"
            df_foodType = run_query(query)
            st.dataframe(df_foodType, hide_index=True)
            
            #8.How many food claims have been made for each food item
            st.subheader("Food claims for each food item")
            query = "select Food_Name, count(Food_Name) as Claims from food_listings group by Food_Name order by Claims desc"
            df_FoodClaims = run_query(query)
            st.dataframe(df_FoodClaims, hide_index=True)

             #9 Which provider has had the highest number of successful food claims
            st.subheader("Provider with highest number of successful food claims")
            query = "select top 1 p.name as ProviderName, count(f.Provider_ID) as FoodClaimCount, c.Status from claims c join food_listings f on c.Food_ID = f.Food_ID join providers p on p.Provider_ID = f.Provider_ID group by p.name,c.Status having c.Status = 'Completed' order by FoodClaimCount desc"
            df = run_query(query)
            st.dataframe(df, hide_index=True)

            #10 What percentage of food claims are completed vs. pending vs. canceled
            st.subheader("Percentage of food claim status")
            query = "select status, cast((cast(count(status) as decimal(10,2))/1000)*100 as decimal(10,2)) as Percentage from claims group by status"
            df_claimstatus = run_query(query)
            st.dataframe(df_claimstatus, hide_index=True)
           
            #11 What is the average quantity of food claimed per receiver
            st.subheader("Average quantity of food claimed per receiver")
            query = "select r.name as ReceiverName,avg(f.quantity) as AvgQuantity from claims c join food_listings f on c.Food_ID = f.Food_ID join receivers r on r.Receiver_ID = c.Receiver_ID group by r.name "
            df = run_query(query)
            st.dataframe(df, hide_index=True)

            #12 Which meal type (breakfast, lunch, dinner, snacks) is claimed the most
            st.subheader("Meal type that was claimed the most")
            query = "select f.Meal_Type, count(c.Claim_ID) as ClaimCount from food_listings f join claims c on f.Food_ID = c.Food_ID group by f.Meal_Type order by ClaimCount desc"
            df_mealtype= run_query(query)
            st.dataframe(df_mealtype, hide_index=True)
            
            #13 total quantity of food donated by each provider
            st.subheader("Total quantity of food donated by each provider")
            query = "select p.name as ProviderName,sum(f.Quantity) as TotalQuantity from providers p join food_listings f on p.Provider_ID = f.Provider_ID group by p.name "
            df = run_query(query)
            st.dataframe(df, hide_index=True)

        except Exception as e:
            st.error("Unexpected error occurred!")
            #st.exception(e)

    with tab4:
        try:
            col1, col2, col3 = st.columns([3, 3, 3])  # Adjust ratio as needed

            with col1:    
                #Most commonly available food types
                fig = px.pie(df_foodType, names='Food_type', values='Count', title='Most commonly available food types')
                st.plotly_chart(fig)
                                     
                #Food claims for each food item        
                st.write("**Food claims for each food item**")
                st.bar_chart(df_FoodClaims.set_index('Food_Name'), color='#3357FF')
        
            with col2:
                
                #Cities with highest number of food listings
                st.write("**Cities with highest number of food listings**")
                st.bar_chart(df_cities.set_index('Location'), color='#33FF57')  
                 
                #Percentage of food claim status
                fig = px.pie(df_claimstatus, names='status', values='Percentage', title='Percentage of food claim status')
                st.plotly_chart(fig)
                
            with col3:
                #Meal type that got claimed the most                
                fig = px.pie(df_mealtype, names='Meal_Type', values='ClaimCount', title='Meal type that got claimed the most')
                st.plotly_chart(fig)

                #Food provider type that contributes the most food
                st.write("**Food provider type that contributes the most food**")
                st.bar_chart(df_foodProvider.set_index('Provider_type'),color='#FF5733')  
        
        except Exception as e:
            st.error("Unexpected error occurred!")
           # st.exception(e)


    with tab2:
    #CRUD
        try:
            def insert_claim( food_ID, receiver_ID, status):
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO claims ( food_ID, receiver_ID, status, timestamp) VALUES ( ?, ?, ?, getdate())", ( food_ID, receiver_ID, status))
                    conn.commit()
                                    
        except Exception as e:
            st.error("Database error occurred while adding claim.")
            st.exception(e)

        try:
            def get_claims():
                with get_connection() as conn:
                    df = pd.read_sql("SELECT * FROM claims", conn)
                return df
            
        except Exception as e:
            st.error("Database error occurred while fetching claim.")
            st.exception(e)

        try:
            def get_foodID():
                with get_connection() as conn:
                    df = pd.read_sql("select distinct Food_ID from food_listings", conn)
                return df
            
        except Exception as e:
            st.error("Database error occurred while fetching food ID.")
            st.exception(e)
            
        try:
            def get_ReceiverID():
                with get_connection() as conn:
                    df = pd.read_sql("select distinct Receiver_ID from receivers", conn)
                return df
            
        except Exception as e:
            st.error("Database error occurred while fetching Receiver ID.")
            st.exception(e)

        try:
            def get_ClaimStatus():
                with get_connection() as conn:
                    df = pd.read_sql("select distinct Status from Claims", conn)
                return df
            
        except Exception as e:
            st.error("Database error occurred while fetching Claim Status.")
            st.exception(e)

        try:
            def update_claim(claim_ID, food_ID, receiver_ID, status):
                with get_connection() as conn:
                    cursor = conn.cursor()
                    current_timestamp = datetime.datetime.now()
                    print(current_timestamp)
                    cursor.execute("UPDATE claims SET Food_ID = ?, Receiver_ID = ?, Status = ?, timestamp = ? WHERE claim_ID = ?", (food_ID, receiver_ID, status,current_timestamp,claim_ID))
                    conn.commit()
                    
        except Exception as e:
                st.error("Database error occurred.")
                st.exception(e)
        
        try:
            def delete_claim(claim_ID):
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM claims WHERE claim_ID = ?", (claim_ID))
                    conn.commit()

        except Exception as e:
                st.error("Database error occurred while deleting claim.")
                st.exception(e)

        #menu = st.sidebar.selectbox("Menu", ["Create", "Read", "Update", "Delete"])
        menu_Claim = st.selectbox("Menu", ["Create Claim", "Read Claims", "Update Claim", "Delete Claim"])

        try:
            if menu_Claim == "Create Claim":
                    st.subheader("Add New Claim")
                    #claim_ID = st.text_input("Claim ID")
                    df_food = get_foodID()
                    food_ID = df_food['Food_ID'].tolist()
                    selected_FoodID = st.selectbox("Select Food ID", food_ID)
                    #selected_foodID = df[df['Food_ID'] == select_FoodID].iloc[0]
                    #food_ID = st.text_input("Food ID")
                    df_receiver = get_ReceiverID()
                    receiver_ID = df_receiver['Receiver_ID'].tolist()
                    selected_ReceiverID = st.selectbox("Select Receiver ID", receiver_ID)
                    #receiver_ID = st.text_input("Receiver ID")#, min_value=0, max_value=120
                    df_status = get_ClaimStatus()
                    claim_status = df_status['Status'].tolist()
                    selected_Status = st.selectbox("Select Claim Status", claim_status)
                    #status = st.text_input("Claim Status")
                    if st.button("Add Claim"):
                        insert_claim( selected_FoodID, selected_ReceiverID, selected_Status)
                        st.success("Claim added!")
        
            elif menu_Claim == "Read Claims":
                    st.subheader("Food Claims List")
                    df = get_claims()
                    st.dataframe(df, hide_index=True)

            elif menu_Claim == "Update Claim":
                    st.subheader("Update Claims")
                    df = get_claims()
                    claim_ID = df['Claim_ID'].tolist()
                    selected_id = st.selectbox("Select Claim ID to update", claim_ID)
                    selected_claim = df[df['Claim_ID'] == selected_id].iloc[0]  

                    current_FoodID = selected_claim['Food_ID']
                    current_RecID = selected_claim['Receiver_ID']
                    current_status = selected_claim['Status']
                    #st.write(f":primary[Current Food ID: {selected_claim['Food_ID']} \t Current Receiver ID: {selected_claim['Receiver_ID']}]")
                    claim = {'Selected Claim ID': [selected_id],
                            'Food ID': [current_FoodID],
                            'Receiver ID': [current_RecID],
                            'Status': [current_status]
                            }
                    df_CurrentClaim = pd.DataFrame(claim)
                    st.dataframe(df_CurrentClaim, hide_index=True)

                    df_food = get_foodID()
                    food_ID = df_food['Food_ID'].tolist()
                    selected_FoodID = st.selectbox("New Food ID", food_ID)
                    df_receiver = get_ReceiverID()
                    receiver_ID = df_receiver['Receiver_ID'].tolist()
                    selected_ReceiverID = st.selectbox("New Receiver ID", receiver_ID)
                    df_status = get_ClaimStatus()
                    claim_status = df_status['Status'].tolist()
                    selected_Status = st.selectbox("New Claim Status", claim_status)
                    
                    if st.button("Update"):
                        update_claim(selected_id, selected_FoodID, selected_ReceiverID, selected_Status)
                        st.success("Claim updated!")
                

            elif menu_Claim == "Delete Claim":
                    st.subheader("Delete Claim")
                    df = get_claims()
                    user_ids = df['Claim_ID'].tolist()
                    selected_id = st.selectbox("Select ID to delete", user_ids)
                    #selected_id = st.text_input("ID")
                    selected_claim = df[df['Claim_ID'] == selected_id].iloc[0] 
                    current_FoodID = selected_claim['Food_ID']
                    current_RecID = selected_claim['Receiver_ID']
                    current_status = selected_claim['Status']
                    #st.write(f":primary[Current Food ID: {selected_claim['Food_ID']} \t Current Receiver ID: {selected_claim['Receiver_ID']}]")
                    claim = {'Selected Claim ID': [selected_id],
                            'Food ID': [current_FoodID],
                            'Receiver ID': [current_RecID],
                            'Status': [current_status]
                            }
                    df_CurrentClaim = pd.DataFrame(claim)
                    st.dataframe(df_CurrentClaim, hide_index=True)

                    if st.button("Delete"):
                        delete_claim(selected_id)
                        st.warning("Claim deleted!")

        except pyodbc.IntegrityError as e:
            st.error("Cannot enter duplicate values, Values already present!")
        except pyodbc.Error as e:
            st.error("Database error occurred.")
            #st.exception(e)    
        except Exception as e:
            st.error("An unexpected exception occurred.")
            #st.exception(e)

if selected == "Contact":
    try:

        tab1, tab2 = st.tabs(["Providers Contact", "Receivers List"])

        with tab1:
            
            st.subheader("Contact information of food providers")
            query = "select City,name as ProviderName,Address,Contact,Type from providers"
            df = run_query(query)
            st.dataframe(df, hide_index=True)

        with tab2:
            
            st.subheader("List of Receivers")
            query = "select Name, Type, City, Contact from receivers"
            df = run_query(query)
            st.dataframe(df, hide_index=True)

    except Exception as e:
            st.error("An unexpected error occured!.")
            #st.exception(e)

    



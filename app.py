import streamlit as st
import pandas as pd
from openai import *
import pandas_profiling
import folium
import requests
from streamlit_pandas_profiling import st_profile_report
import os 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder


def main():
    page_bg_img = '''
    <style>
    body {
    background-image:"sibiu.jpg";
    background-size: cover;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

def get_route_geometry(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    response = requests.get(url)
    if response.status_code == 200:
        route = response.json()
        if 'routes' in route and len(route['routes']) > 0:
            geometry = route['routes'][0]['geometry']
            return geometry
    return None


if __name__=="main":
   main()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'option' not in st.session_state:
    st.session_state.option = 'login'    
def promptopenai(prompt):
    OPENAI_API_KEY="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"
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": prompt}
  ]
)
    st.write(completion.choices[0].message.content)
if os.path.exists("dataset.csv"):
    df = pd.read_csv('dataset.csv', index_col=None)
with open("dataset.csv",'r') as f:
    setdedate=f.read()

def predictive_analytics(file_path, target_column, categorical_columns):
    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        return "File not found. Please provide a valid file path."

    if target_column not in data.columns:
        return f"Target column '{target_column}' not found in the dataset."

    # Separate features (X) and target (y)
    X = data.drop(columns=[target_column])
    y = data[target_column]

    # Apply label encoding to categorical columns
    label_encoders = {}
    for col in categorical_columns:
        if col in X.columns:
            label_encoders[col] = LabelEncoder()
            X[col] = label_encoders[col].fit_transform(X[col])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    return predictions
example_route = [
    (45.792784,24.152069)
    # Add more coordinates as needed
]
example_waypoints = [
        {'name': 'street Alba Iulia', 'location': [45.792669466818985, 24.11050065876004]},  
        {'name': 'street Metalurgistilor', 'location': [45.79502049176556, 24.131995145671116]},  
        {'name':'street Dealului','location':[45.79121908096157, 24.14194594146985]},
        {'name':'street George Cosbuc','location':[45.7906090862689, 24.143331189614138]},
        {'name':'street Bulevardul Victoriei','location':[45.79172354806361, 24.14696087238784]},
        {'name':'street Bulevardul Corneliu Coposu','location':[45.791518717676894, 24.149379423017265]},
    ]

def display_route_preview(route,waypoints):
    # Create a map centered around the route
    route_map = folium.Map(location=[route[0][0], route[0][1]], zoom_start=12)
    for waypoint in waypoints:
        folium.Marker(waypoint['location'], popup=waypoint['name']).add_to(route_map)
    for i in range(len(waypoints)):
        for j in range(i + 1, len(waypoints)):
            start = waypoints[i]['location']
            end = waypoints[j]['location']
            # Example: You'd replace this with your actual shortest path algorithm and route data
            shortest_path = [(start[0], start[1]), ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2), (end[0], end[1])]
            folium.PolyLine(locations=shortest_path, color='blue').add_to(route_map)

    # Add route points to the map
    folium.PolyLine(locations=route, color='blue').add_to(route_map)

    # Display the map
    return route_map


with st.sidebar:
    st.title("navigatie")
    st.image("sibiulogo.jpg")
    choice=st.radio("",["login","upload data","profiling","best route","map","predictii"])
    


def getusercreditancials():
   st.title("Login or Sign up")
   st.session_state.option  = st.selectbox("",("Login","Signup"),index=None,)
       
   if st.session_state.option == "Login":
    with open("creditentials.txt", 'r') as basef:
        emailuser = basef.readline().strip()  
        passworduser = basef.readline().strip()  

    email = st.text_input("E-mail: ").strip()  # Remove leading/trailing whitespaces
    password = st.text_input("Parola: ", type='password').strip()  # Remove leading/trailing whitespaces

    if st.button("Enter"):
        if not email or not password:
            st.write("Missing info")
        elif email == emailuser and password == passworduser:
            st.session_state.logged_in = True
            st.write("Login successful")
        else:
            st.write("Wrong details")

  
   if st.session_state.option == "Signup":
    st.write("Please read and accept the End User License Agreement (EULA) below:")
    eula_accepted = st.checkbox("I accept the EULA")

    if eula_accepted:
        email = st.text_input("E-mail: ")
        password = st.text_input("Parola: ", type='password')
        newsletter_subscribe = st.checkbox("Subscribe to newsletter")

        try:
            with open("credentials.txt", 'w') as savedcredi:
                savedcredi.write(email)
                savedcredi.writelines('\n')
                savedcredi.write(password)

                if newsletter_subscribe:
                    # Here you might want to handle the newsletter subscription logic
                    # For example, save the email to a separate file for newsletter subscribers
                    newsletteremail=email

               
        except Exception as e:
            st.error(f"Failed to write to file: {e}")
    else:
        st.warning("Please accept the EULA to proceed with signup.")

if choice=="login":
    if st.session_state.logged_in==False or st.session_state.option == "Signup" :
        getusercreditancials()
     
 
    #upload baza de data in format .csv
if st.session_state.logged_in==True:
    if choice=="upload data":
      st.title("upload data")
      file = st.file_uploader("Upload Your Dataset")
      if file: 
        df = pd.read_csv(file, index_col=None)
        df.to_csv('dataset.csv', index=None)
        st.dataframe(df)


    #profiling
    if choice=="profiling":
     st.title("profiling")
     minimal_elements = {
      "nr case":False,
      "duplicates": False,
      "Alerts":False,
      "ore de varf":False,
}
     profile_df = df.profile_report(minimal=minimal_elements)
     st_profile_report(profile_df)
    

    #"best route"
    if choice =="best route":
     prompt="what's the best route from street "
     st.write("promtul sa fie de forma street A to street B")
     user_input1=st.text_input("dati strata de pornire: ")
     user_input2=st.text_input("dati strada care v-a fi destinatia:")
     user_input3=st.text_input("cu ce vehicul v-a transportati: ")
     user_input4=st.text_input("laguage: ")
     st.write("ex camion, masina mica, autobuz")
     user_input=user_input1+",Sibiu, to street "+user_input2+", Sibiu"+"while using the "+user_input3+" in "+user_input4+" ?"
    
     if st.button("trimiteti promptul"):
       promptopenai(prompt+user_input)






    if choice=="map":
     st.title("MAP")
     route_map = display_route_preview(example_route,example_waypoints)
     route_map.save('route_preview.html')  # Save the map to an HTML file
     #st.write(route_map)  # Display the map in the notebook or streamlit app
     with open('route_preview.html', 'r') as f:
        html_string = f.read()
     st.components.v1.html(html_string, width=700, height=500)



    if choice=="predictii":
       st.title("Predictii")
       userinput=st.text_input("Ce criteriu v-a fi folosit la predictii:")
       file_path="dataset.csv"
       categorical_columns = ['nr case', 'lungimea strazi in km']
       if st.button("ENTER!"):
          results = predictive_analytics(file_path,userinput,categorical_columns)
          st.write(results)


    



#st.write(f"Session State - Logged in: {choice}")
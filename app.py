import streamlit as st
import pandas as pd
from openai import *
import pandas_profiling
import folium
import requests
import polyline
from streamlit.components.v1 import html
from streamlit_pandas_profiling import st_profile_report
import os 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder


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
]
example_waypoints = [
        {'name': 'street Alba Iulia', 'location': [45.792669466818985, 24.11050065876004]},  
        {'name': 'street Metalurgistilor', 'location': [45.79502049176556, 24.131995145671116]},  
        {'name':'street Dealului','location':[45.79121908096157, 24.14194594146985]},
        {'name':'street George Cosbuc','location':[45.7906090862689, 24.143331189614138]},
        {'name':'street Bulevardul Victoriei','location':[45.79172354806361, 24.14696087238784]},
        {'name':'street Bulevardul Corneliu Coposu','location':[45.791518717676894, 24.149379423017265]},
        {'name':'street Constitutiei ','location':[45.79701966358754, 24.158525042372943]},
        {'name':'street Balea','location':[45.79593533877033, 24.15908307370339]},
        {'name':'street Intersectie Balea cu Fabrici ','location':[45.794848857012994, 24.16004723883584]},
        {'name':'street Izvorului ','location':[45.79426018581551, 24.160005545208673]},
        {'name':'street  Urlea ','location':[45.79551019626466, 24.16292409915046]},
        {'name':'street Ghetariei ','location':[45.795586504133084, 24.16407067389763]},
        {'name':'street Intersectie Socului ','location':[45.79656032872566, 24.16484200603392]},
        {'name':'Gara ','location':[45.79985452366536, 24.161275083737873]},
        {'name':'street General Magheru ','location':[45.799506550878895, 24.159481146599997]},
        {'name':'street Uzinei ','location':[45.79867829210272, 24.160065304111786]},
        {'name':'street Pescarilor ','location':[45.798116560734265, 24.15898069002962]},
        {'name':'street Constitutiei ','location':[45.79902829108386, 24.15735686779285]},
        {'name':'street Avram Iancu ','location':[45.79829791968353, 24.154419212986234]},
        {'name':'street Moviliei ','location':[45.79904557888336, 24.15362688834847]},
        {'name':'street 9 Mai ','location':[45.799911412227196, 24.15243655876094]},
        {'name':'street Ocnei ','location':[45.800379008027136, 24.15042442270393]},
        {'name':'street Plopilor','location':[45.80028101857664, 24.149697924216895]},
        {'name':'street Vopsitorilor','location':[45.80015021604529, 24.148535714349094]},
        {'name':'street Faurului ','location':[45.799281824778625, 24.150172189211656]},
        {'name':'street Zidului ','location':[45.80156359382426, 24.150203459413074]},
        {'name':'street Raului ','location':[45.8045744382801, 24.149273355826498]},
        {'name':'street Scoala de Inot ','location':[45.78526037355237, 24.14556887668649]},
        {'name':'street Octavian Goga','location':[45.782054301978, 24.143626749961957]},
        {'name':'street Bulevardul Mihai Viteazul ','location':[45.780498814655076, 24.152791160603325]},
        {'name':'street Semaforului ','location':[45.782555347765694, 24.167977789032378]},
        {'name':'street Rahovei ','location':[45.781320785708814, 24.165070274516754]},
        {'name':'street Fratii Buzesti','location':[45.781061108913796, 24.149597660416944]},
        #{'name':'street ','location':[]},
        #{'name':'street ','location':[]},
        #{'name':'street ','location':[]},
        #{'name':'street ','location':[]},
        #{'name':'street ','location':[]},
        #{'name':'street ','location':[]},
    ]

def get_route_geometry(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    response = requests.get(url)
    if response.status_code == 200:
        route = response.json()
        if 'routes' in route and len(route['routes']) > 0:
            geometry = route['routes'][0]['geometry']
            return geometry
    return None

def get_route_info(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    response = requests.get(url)
    if response.status_code == 200:
        route = response.json()
        if 'routes' in route and len(route['routes']) > 0:
            duration = route['routes'][0]['duration'] 
            geometry = route['routes'][0]['geometry']
            return geometry, duration
    return None, None



def display_route_preview(route_data, waypoints):
    
    route_map = folium.Map(location=(45.792784,24.152069), zoom_start=10)  

    for waypoint in waypoints:
        folium.Marker(waypoint['location'], popup=waypoint['name']).add_to(route_map)

    for i in range(len(waypoints)):
        for j in range(i + 1, len(waypoints)):
            start = waypoints[i]['location']
            end = waypoints[j]['location']
            geometry, duration = get_route_info(start, end)
            if geometry and duration:
                line = folium.PolyLine(locations=polyline.decode(geometry), color='blue')
                line.add_to(route_map)              
                time_minutes = duration / 60  
                distance = 35 * (time_minutes / 60)  
                mid_point = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)  
                folium.Marker(mid_point, popup=f"Estimated Time: {time_minutes:.2f} mins\nDistance: {distance:.2f} km",
                              icon=folium.DivIcon(icon_size=(150,36), icon_anchor=(0,0), html=f"<div style='font-size: 16px; color: lime;'>{time_minutes:.2f} mins</div>")).add_to(route_map)

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

    email = st.text_input("E-mail: ").strip()  
    password = st.text_input("Parola: ", type='password').strip()  

    if st.button("Login"):
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
            with open("creditentials.txt", 'w') as savedcredi:
                savedcredi.write(email)
                savedcredi.writelines('\n')
                savedcredi.write(password)

                if newsletter_subscribe:
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
     
     with open('route_preview.html', 'r') as f:
        html_string = f.read()
        f.close()
     with open('previousstring.txt','r') as r:
        previousString=r.read()
        r.close()

           
     if html_string==previousString:
       st.components.v1.html(html_string, width=700, height=500)
     elif html_string!=previousString:
       route_map = display_route_preview(example_route,example_waypoints)
       route_map.save('route_preview.html')  
       st.write(route_map)  
       with open('route_preview.html', 'r') as f:
        html_string = f.read()
        st.components.v1.html(html_string, width=700, height=500)
        previousString=html_string



    if choice=="predictii":
       st.title("Predictii")
       userinput=st.text_input("Ce criteriu v-a fi folosit la predictii:")
       file_path="dataset.csv"
       categorical_columns = ['nr case', 'lungimea strazi in km']
       if st.button("ENTER!"):
          results = predictive_analytics(file_path,userinput,categorical_columns)
          st.write(results)


    



#st.write(f"Session State - Logged in: {choice}")
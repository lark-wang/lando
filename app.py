from google import genai
from google.genai import types
from PIL import Image
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import streamlit as st


from google.api_core import retry
is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code 
in {429, 503})
genai.models.Models.generate_content = retry.Retry(
    predicate=is_retriable)(genai.models.Models.generate_content)

# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]


client = genai.Client(api_key=GOOGLE_API_KEY)

def get_article_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    paragraphs = [p.get_text() for p in soup.find_all("p")]

    if len(paragraphs) > 1:
        paragraphs = paragraphs[1:]
        
    text = "\n".join(paragraphs).strip()
    
    return text

few_shot_prompt = """ Use an ESPN article summarizing a Grand Prix to 
answer some questions about Formula 1 Driver Lando Norris. Only use
information from the article. If the information is not in the article, 
respond with N/A. 

EXAMPLE: 

Article: 'BUDAPEST, Hungary -- Lando Norris narrowly beat McLaren teammate 
Oscar Piastri to victory at the Hungarian Grand Prix following a titanic 
battle between the championship rivals in the closing laps.\nThe race 
ended in a showdown between the McLaren drivers on Lap 69 of 70, with 
Piastri closing on Norris on the pit straight and narrowly missing his 
teammate as he attempted to pass under braking at Turn 1 and locked a 
tire.\nThe tight finish came about after McLaren put the two drivers on 
different strategies, with Norris -- who dropped to fifth on the opening 
lap -- making a one-stop strategy work in his favor while Piastri, who was 
second on the opening lap, was put on a two-stop.\nWith the two drivers 
split on strategy, Piastri had fresher tires in the closing stages and 
narrowed a 10-second gap to a matter of centimeters in the final 20 
laps.\nThe race hinged on a move by Piastri on the inside of Turn 1 on Lap 
69 that saw the Australian narrowly avoid a collision and Norris retain 
the lead.\nAs McLaren took their 200th F1 victory, Norris is now nine 
points behind his teammate in the championship ahead of Formula 1\'s 
summer break.\n"I\'m dead. I\'m dead. It was tough," Norris said 
afterward. "We weren\'t really planning on the one-stop but after the 
first lap it was kind of our only option to get back into things.\n"The 
final stint with Oscar catching I was pushing flat out ... [it was] 
rewarding even more because of that. The perfect result today."\nPiastri 
said: "I pushed as hard as I could. After I saw Lando going for a 
one-stop, I knew I was going to have to overtake on track, which is much 
easier said than done around here.\n"It was a gamble either way. Today, 
unfortunately, we were just on the wrong side of it.\n"The team did a 
great job, the car came alive in the second half of the race."\nThe battle 
between the McLaren drivers had been complicated by the presence of 
Charles Leclerc starting from pole position, but the Ferrari driver faded 
in the final stint of the race and finished fourth behind George Russell 
in third.\nLeclerc led Piastri through Turn 1 following a clean start as 
Norris, who had looked to pass Piastri on the inside, fell to fifth place 
in the opening corners.\nNorris set about recovering positions in the 
early phase of the race as McLaren\'s strategists put their focus on 
Piastri undercutting Leclerc for the lead by pitting the championship 
leader on Lap 18.\nThe Italian team reacted by pitting their driver a lap 
later and managed to keep Leclerc ahead of Piastri when the Ferrari 
reemerged on track.\nNorris stayed out on track and soon committed to a 
one-stop strategy, meaning he effectively took the lead of the race by 
making one fewer stop.\nNorris\' sole pit stop came on Lap 30, and he 
emerged close enough behind the battle between Leclerc and Piastri to 
retake the lead when Leclerc made his second stop on Lap 40 and Piastri 
made his on Lap 45.\nPiastri was still running third after his second 
stop, but as Leclerc\'s pace faded the McLaren driver passed the Ferrari 
for second place on Lap 51 and started his pursuit of Norris.\nLando 
Norris makes it nine career wins and five this season...\nAfter closing 
the gap lap by lap, Piastri was one second off Norris as the lead McLaren 
hit lapped traffic on Lap 65.\nThe traffic seemed to work in Norris\' 
favor, allowing him use of the DRS overtaking aid to defend from his 
teammate.\nWith three laps to go, the two McLarens emerged from the 
traffic, putting them in a straight fight for victory.\nPiastri came 
closest with his move on Lap 69, but ultimately just fell short of making 
it stick.\nLeclerc lost third place to Russell on Lap 63 at Turn 1 and 
squeezed the Mercedes to the inside of the track.\nThe Ferrari driver, who 
was clearly frustrated by his lack of performance in the final stint, was 
penalized five seconds for cutting across on Russell but still finished 
fourth.\nFernando Alonso secured fifth place for Aston Martin ahead of 
another impressive performance by Brazilian rookie Gabriel Bortoleto in 
sixth.\nLance Stroll took seventh in the second Aston Martin ahead of Liam 
Lawson in eighth and Max Verstappen in ninth, who rounded off a 
disappointing weekend for Red Bull.\nAndrea Kimi Antonelli secured the 
final point on offer for Mercedes, with Lewis Hamilton starting and 
finishing the race in 12th place for Ferrari.\nThe next round of the F1 
championship will take place in the Netherlands on Aug. 31.'

Response: 

Race: Hungarian Grand Prix

Where did Lando finish? 
First place!

Did Lando do better than Oscar? 
Yes :)

Is Lando higher than Oscar now in the overall driver's championship 
standings? 
No :(

How did Lando feel about the race? 
Ecstatic

Notable events in the race for Lando: 
Lando made one stops instead of two after falling into fifth place in the 
first lap. 

Notable quotes: 
N/A

Article: 
"""

left_col, right_col = st.columns([4, 1])
with right_col:
    # Load your images
    
    lando_image1 = Image.open("lando2.png")
    lando_image2 = Image.open("lando1.jpg")
    
    # Stack images vertically at the top of right column
    st.write("")
    st.write("")
    st.image(lando_image1)
    st.image(lando_image2)

with left_col:
    st.title("Where's Lando? ESPN Article + Gemini LLM")
    
    url = st.text_input("Paste ESPN article URL here:")
    
    if st.button("Analyze"):
        if url:
            with st.spinner("Fetching article and generating response..."):
                try:
                    article_text = get_article_text(url)
                    # Call Gemini API
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        config=types.GenerateContentConfig(
                            temperature=0,
                            top_p=1,
                            max_output_tokens=250,
                        ),
                        contents=[few_shot_prompt, article_text]
                    )
                    st.subheader("Gemini Response")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a valid URL.")

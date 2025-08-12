from google import genai
from google.genai import types
import os
import requests
from bs4 import BeautifulSoup
import streamlit as st


from google.api_core import retry
is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code 
in {429, 503})
genai.models.Models.generate_content = retry.Retry(
    predicate=is_retriable)(genai.models.Models.generate_content)

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

few_shot_prompt = """ Use an ESPN article summarizing a Grand Prix to answer some questions about Formula 1 Driver Lando Norris. Only use
information from the article. If the information is not in the article, respond with N/A. 

General instructions: For every question except for the first question, put a blank line between the question and answer. Indent the answer.

Specfic instructions by question: 
1. Race: If the name of the Grand Prix refers to the country, put the city in parentheses next to it. For instance, for the Hungarian Grand Prix, put "Hungarian Grand Prix (Budapest)". For the Miami Grand Prix, just put "Miami Grand Prix". 
2. Where did Lando finish? If Lando finished in the top three, put an exclamation mark at the end (ex. First place!). If Lando did not finish the race, put "Did not finish :(". Otherwise, don't put any punctuation at the end. 
3. Did Lando do better than Oscar? Put "Yes :)" or "No :(" or "Not Mentioned". 
4. Is Lando higher than Oscar now (as of this race) in the overall driver's championship standings? Put "Yes :)" or "No :(" or "Not Mentioned". 
5. How did Lando feel about the race? Restrict this output to a one-word adjective. 
6. Notable events in the race for Lando: Restrict this output to one sentence. Put N/A if there were not any notable events. Failing to catch the race leader from second place is not a notable event. 
7. Notable quotes: Restrict output to five total sentences or less. Lean toward only choosing quotes which contain a punchy sentiment, as opposed to technical commentary. If there are not any punchy quotes, lean toward putting less or none. Put a blank line between each separate quote. Important: only put direct quotations of what was said - do not include dialogue tags or any descriptions of what was said.  

EXAMPLE: 

Article: 'BUDAPEST, Hungary -- Lando Norris narrowly beat McLaren teammate Oscar Piastri to victory at the Hungarian Grand Prix following a titanic battle between the championship rivals in the closing laps.\nThe race ended in a showdown between the McLaren drivers on Lap 69 of 70, with Piastri closing on Norris on the pit straight and narrowly missing his teammate as he attempted to pass under braking at Turn 1 and locked a tire.\nThe tight finish came about after McLaren put the two drivers on different strategies, with Norris -- who dropped to fifth on the opening lap -- making a one-stop strategy work in his favor while Piastri, who was second on the opening lap, was put on a two-stop.\nWith the two drivers split on strategy, Piastri had fresher tires in the closing stages and narrowed a 10-second gap to a matter of centimeters in the final 20 laps.\nThe race hinged on a move by Piastri on the inside of Turn 1 on Lap 69 that saw the Australian narrowly avoid a collision and Norris retain the lead.\nAs McLaren took their 200th F1 victory, Norris is now nine points behind his teammate in the championship ahead of Formula 1\'s summer break.\n"I\'m dead. I\'m dead. It was tough," Norris said afterward. "We weren\'t really planning on the one-stop but after the first lap it was kind of our only option to get back into things.\n"The final stint with Oscar catching I was pushing flat out ... [it was] rewarding even more because of that. The perfect result today."\nPiastri said: "I pushed as hard as I could. After I saw Lando going for a one-stop, I knew I was going to have to overtake on track, which is much easier said than done around here.\n"It was a gamble either way. Today, unfortunately, we were just on the wrong side of it.\n"The team did a great job, the car came alive in the second half of the race."\nThe battle between the McLaren drivers had been complicated by the presence of Charles Leclerc starting from pole position, but the Ferrari driver faded in the final stint of the race and finished fourth behind George Russell in third.\nLeclerc led Piastri through Turn 1 following a clean start as Norris, who had looked to pass Piastri on the inside, fell to fifth place in the opening corners.\nNorris set about recovering positions in the early phase of the race as McLaren\'s strategists put their focus on Piastri undercutting Leclerc for the lead by pitting the championship leader on Lap 18.\nThe Italian team reacted by pitting their driver a lap later and managed to keep Leclerc ahead of Piastri when the Ferrari reemerged on track.\nNorris stayed out on track and soon committed to a one-stop strategy, meaning he effectively took the lead of the race by making one fewer stop.\nNorris\' sole pit stop came on Lap 30, and he emerged close enough behind the battle between Leclerc and Piastri to retake the lead when Leclerc made his second stop on Lap 40 and Piastri made his on Lap 45.\nPiastri was still running third after his second stop, but as Leclerc\'s pace faded the McLaren driver passed the Ferrari for second place on Lap 51 and started his pursuit of Norris.\nLando Norris makes it nine career wins and five this season...\nAfter closing the gap lap by lap, Piastri was one second off Norris as the lead McLaren hit lapped traffic on Lap 65.\nThe traffic seemed to work in Norris\' favor, allowing him use of the DRS overtaking aid to defend from his teammate.\nWith three laps to go, the two McLarens emerged from the traffic, putting them in a straight fight for victory.\nPiastri came closest with his move on Lap 69, but ultimately just fell short of making it stick.\nLeclerc lost third place to Russell on Lap 63 at Turn 1 and squeezed the Mercedes to the inside of the track.\nThe Ferrari driver, who was clearly frustrated by his lack of performance in the final stint, was penalized five seconds for cutting across on Russell but still finished fourth.\nFernando Alonso secured fifth place for Aston Martin ahead of another impressive performance by Brazilian rookie Gabriel Bortoleto in sixth.\nLance Stroll took seventh in the second Aston Martin ahead of Liam Lawson in eighth and Max Verstappen in ninth, who rounded off a disappointing weekend for Red Bull.\nAndrea Kimi Antonelli secured the final point on offer for Mercedes, with Lewis Hamilton starting and finishing the race in 12th place for Ferrari.\nThe next round of the F1 championship will take place in the Netherlands on Aug. 31.'

Response: 

Race: Hungarian Grand Prix (Budapest)

Where did Lando finish? 

    First place!

Did Lando do better than Oscar? 

    Yes :)

Is Lando higher than Oscar now in the overall driver's championship standings? 

    No :(

How did Lando feel about the race? 

    Ecstatic

Notable events in the race for Lando: 

    Lando made one stops instead of two after falling into fifth place in the first lap. 

Notable quotes: 

    N/A

EXAMPLE: 

Article: 'MIAMI GARDENS, Fla. -- Oscar Piastri extended his championship lead to 16 points with a victory ahead of teammate Lando Norris at the Miami Grand Prix on Sunday.\nNo other driver, including reigning champion Max Verstappen who started from pole position, had the pace to match the two McLarens, with Piastri securing his fourth victory of the season by 4.6 seconds ahead of Norris.\nNorris, who started from second position, attempted to pass Verstappen for the lead in the opening corner of the race but found himself hung out to dry on the outside of Turn 2 and dropped to fifth as Piastri moved up to third from fourth on the grid.\nPiastri passed Andrea Kimi Antonelli for second place on Lap 4, and Norris recovered to third place by Lap 9.\nOver the next nine laps, Verstappen provided a defensive masterclass, holding off Piastri until Lap 14 and Norris until Lap 18.\nThe superior pace of the McLarens was clear to see, but Verstappen positioned his Red Bull in all the right places to delay the inevitable.\nOnce the two McLarens were in clear air at the front of the pack, their one-two never looked in doubt, with Piastri managing the closing gap to his teammate.\nNorris attempted to close in and chipped away at his teammate\'s lead over the second half of the race but ultimately was unable to muster a genuine challenge.\nThe result means Piastri has extended his championship lead for the second race since taking the lead of the standings at the Bahrain Grand Prix.\nPiastri said in a postrace interview he knew to avoid Verstappen at Turn 1.\n"I won the race that I really wanted to after a tricky day on Saturday," Piastri said.\n"To come away with a win is an impressive result. I was aware enough to avoid Max in Turn 1 and I knew I had a pace advantage. I was struggling on the hard tyres but I had built a gap, there is still stuff to work on. We are constantly learning.\n"Two years ago at Miami we were the slowest team. I think we were lapped twice. Now to have won the Grand Prix by over 35 seconds to third is an unbelievable result."\nSimilarly, Norris said Verstappen put up a good fight as always: "I paid the price, but it\'s the way it is. What can I say? If I don\'t go for it, people complain. If I go for it, people complain, so you can\'t win.\n"But it is the way it is with Max, it\'s crash or don\'t pass. Unless you get it really right and you put him in the perfect position, then you can just about get there. I paid the price for not doing a good enough job today, but I\'m still happy with second."\nOscar Piastri is the first McLaren driver to win four of the first six races in a season since Mika Häkkinen in 1998.\nGeorge Russell secured third place for Mercedes after benefitting from a pit stop under a virtual safety car, which was deployed to remove the broken-down Haas of Oliver Bearman from the side of the race track.\nRussell said he was pleased with a podium result.\n"Really happy to come away with P3," he said afterward. "I\'ve been struggling this weekend personally and always on the backfoot."\nHours after the race, Red Bull lodged a protest over Russell\'s result for allegedly failing to slow under yellow flags.\nVerstappen, who had pitted under normal racing conditions, had to settle for fourth place despite his heroics in the opening laps, meaning he is now 32 points behind Piastri after losing 20 points to the McLaren driver over the course of the entire Miami Grand Prix sprint race weekend.\nAlex Albon matched his best result of the season with a fifth-place finish ahead of Antonelli, who also lost out on track position in the pit stops.\nA disappointing weekend for Ferrari concluded with a tense battle between its drivers over seventh and eighth.\nRunning differing tyre strategies, Lewis Hamilton cruised up behind Charles Leclerc on Lap 36 as his medium tires offered better performance than Leclerc\'s hards.\nFerrari initially told Hamilton to remain one-second behind Leclerc to benefit from DRS while maintaining position, but the driver of car 44 replied saying: "This is not good teamwork, that\'s all I\'m going to say."\nHamilton added in a separate message: "In China I got out the way [for Leclerc]. Have a tea break while you\'re at it, come on."\nOn hearing that, Ferrari agreed to tell Leclerc to let Hamilton past, which he did on Lap 39.\nLess than 15 laps later, Hamilton\'s tyres had started to go off and Leclerc was now on the radio asking to repass Hamilton so that he could chase Antonelli for sixth.\nAgain, the order took several laps to be enacted, with Leclerc finishing 3.1 seconds off the Mercedes at the finish.\nCarlos Sainz secured ninth for Williams after attempting to pass Hamilton on the final lap, with Red Bull\'s Yuki Tsunoda in 10th place.\n- How Lego built life-size F1 cars for Miami GP driver parade'

Response: 

Race: Miami Grand Prix

Where did Lando finish? 

    Second place!

Did Lando do better than Oscar? 

    No :(

Is Lando higher than Oscar now in the overall driver's championship standings? 

    No :(

How did Lando feel about the race? 

    Okay

Notable events in the race for Lando: 

    N/A

Notable quotes: 

    "What can I say? If I don't go for it, people complain. If I go for it, people complain, so you can't win."

    "I paid the price for not doing a good enough job today, but I'm still happy with second."


EXAMPLE: 

Article: 'MONTREAL -- George Russell won a Canadian Grand Prix that exploded into drama when Lando Norris collided with title rival and teammate Oscar Piastri.\nThe buildup had been all about a contest between Russell and Max Verstappen, who had been irritated by talk of his penalty points after qualifying, but a close duel between them never materialized. However, after the race Red Bull lodged a protest over Russell\'s result, but it was later thrown out by stewards.\nIt fell to the McLaren drivers to provide the key talking point -- the incident was under investigation by stewards and Norris was handed a five-second time penalty.\nThe stewards are also looking into a protest lodged by Red Bull over Russell\'s victory, in relation to conduct under the safety car.\nNorris slammed into the back of the other McLaren on Lap 66 as they vied for fourth position late in the race.\nNorris got a run on Piastri down the start-finish straight, but as the road kinked to the right, he drifted too wide and closed the gap with the Australian\'s car, ending up in the wall.\nThe crash put Norris out of the race, and Piastri extended his championship lead to 22 points.\nAlthough the first incident between the two will generate headlines, there was no contention over what had happened -- Norris refused to point the finger of blame at anyone but himself.\n"Sorry," Norris said on the radio immediately afterwards. "All my bad. All my fault. Stupid from me."\nThe incident also meant the race finished under the safety car.\nA dramatic end to the race as Russell won from pole...\nIt helped Russell\'s teammate, teenage wunderkind Andrea Kimi Antonelli, secure the first podium of his Formula 1 career, thus becoming the third youngest driver on the podium after Verstappen and Lance Stroll.\n"It was so stressful but [I\'m] super happy," Antonelli said. "I had a good start, managed to jump into P3 and just stayed up there at the front."\nRussell said it\'s "amazing" to be back on the top step.\n"The last time for us was back in Vegas. I felt last year was a victory lost and probably got the victory today due to the incredible pole lap yesterday. Obviously so happy to see Kimi on the podium as well."\nPiastri avoided major damage and managed to drag his car home for fourth, with Ferrari\'s Charles Leclerc and Lewis Hamilton fifth and sixth.\nHamilton, who compared driving his car to dancing with someone who doesn\'t have rhythm, had another race where he seemed was confused about his lack of pace.\n"I\'m nowhere in this race, mate," Hamilton complained at one point. Hamilton had hit a groundhog and said said he was "devastated" about it. The incident also damaged the floor of the car.\nAston Martin driver Fernando Alonso continued the turnaround of his season by finishing seventh, ahead of the in-form Nico Hulkenberg for Sauber.\nEsteban Ocon finished ninth for Haas, while Carlos Sainz grabbed the final point on offer for Williams.'

Response: 

Race: Canadian Grand Prix (Montreal)

Where did Lando finish? 

    Did not finish :( 

Did Lando do better than Oscar? 

    No :(

Is Lando higher than Oscar now in the overall driver's championship standings? 

    No :(

How did Lando feel about the race? 

    Self-reflective

Notable events in the race for Lando: 

    Lando crashed into Oscar and had to retire, while Oscar still finished the race. 

Notable quotes: 

    "Sorry...All my bad. All my fault. Stupid from me."

"""


st.image("lando2.png", use_container_width=True)
st.title("Where's Lando? ")
st.write("In the ongoing 2025 Formula 1 season, drivers Lando Norris and Oscar Piastri are competing in an intense battle for the championship. This app takes an ESPN race report URL and outputs some information about Lando’s performance, using the Google Gemini API with few-shot prompting. ")
st.write("")
st.write("""Sample race report links:
1. https://www.espn.com/f1/story/_/id/44220323/lando-norris-holds-max-verstappen-win-thrilling-race  
2. https://www.espn.com/f1/story/_/id/45645622/norris-beats-piastri-wet-dramatic-british-gp  
3. https://www.espn.com/f1/story/_/id/45803070/dominant-oscar-piastri-wins-belgian-gp-extends-f1-championship-lead""")
st.write("")
st.write("")
#url = st.text_input("Paste ESPN article URL here:")
url = st.text_input(r"$\text{\normalsize Paste ESPN article URL here:}$")
                    
if st.button("Find Lando!"):
    if url:
        with st.spinner("Fetching article and generating response..."):
            try:
                article_text = get_article_text(url)
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




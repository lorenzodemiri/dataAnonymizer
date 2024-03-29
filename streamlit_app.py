from google.protobuf.descriptor import EnumValueDescriptor
from presidio_anonymizer.entities import engine
import streamlit as st
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities.engine import OperatorConfig
from presidio_evaluator.data_generator.presidio_perturb import PresidioPerturb
from presidio_image_redactor import ImageRedactorEngine
from PIL import Image
import pandas as pd
import spacy

st.set_page_config(layout="wide")


def show_pipeline(analyzer_results, perturbed_text, original_text: str):
    TEXT_LINE = """
            <head>
            <style>
            body {{
                font-family: 'Poiret One';font-size: 22px;
                }}
            h3 {{
            text-align: center;
            }}
            .center {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            height: 50%;
            }}
            .loading {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            }}
            </style>
            </head>
            <body>
            <img src="https://s6.gifyu.com/images/input-onlinegiftools.gif" width="25" class="loading">
            <h3>{}</h3 >           
            <img src="https://media.giphy.com/media/ZbfHMCu2BCuEdZCjBC/giphy.gif" width="155" class="center">
            <img src="https://s6.gifyu.com/images/input-onlinegiftools.gif" width="25" class="loading">
            </body >
            """
    

    st.markdown(TEXT_LINE.format("Tokenizer"), unsafe_allow_html=True)

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(original_text)
    
    with st.beta_expander("Check the analyzed Token:"):
        for token in doc:
            temp_str = """
                <head>
                <style>
                p {{
                text-align: center;
                }}
                </style>
                </head>
                <body>
                <p>{}</p>
                <p>Token: {}</p>
                <p>Lemma: {}</p>
                <p>Pos: {}</p>
                </body >
                """.format("_"*50,token.text, token.lemma_, token.pos_)
            st.markdown(temp_str, unsafe_allow_html=True)
    
    st.markdown(TEXT_LINE.format("Analyzer Engine and NER"), unsafe_allow_html=True)

    with st.beta_expander("Check Analyzed Result"):
        for entity in analyzer_results:
            if entity.score > 0.05:
                temp_str = """
                    <head>
                    <style>
                    p {{
                    text-align: center;
                    }}
                    </style>
                    </head>
                    <body>
                    <p>{}</p>
                    <p>     Entity Type: {}</p> 
                    <p>     Start: {}</p>
                    <p>     End: {}</p>
                    <p>     Score: {}</p>
                    </body >
                    """.format("_"*50, entity.entity_type, entity.start, entity.end, entity.score)
                st.markdown(temp_str, unsafe_allow_html=True)

    st.markdown(TEXT_LINE.format("Perturbator Engine"), unsafe_allow_html=True)

    with st.beta_expander("Check Perturbator Result"):
        temp_str = """
                    <head>
                    <style>
                    p {{
                    text-align: center;
                    }}
                    </style>
                    </head>
                    <body>
                    <h3>{}</h3>
                    </body >
                    """.format(perturbed_text)
        st.markdown(temp_str ,unsafe_allow_html=True)
    return

def anon_text(text, pipeline = False):

    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    fake_pii_df = pd.read_csv(
        'raw_data/FakeNameGenerator.com_3000.csv', encoding='utf-8')
    presidio_perturb = PresidioPerturb(fake_pii_df=fake_pii_df)

    analyzer_results = analyzer.analyze(text = text, language ='en')
    anonymized_results = anonymizer.anonymize(
        text = text,
        analyzer_results = analyzer_results,
        operators = {
            "PERSON": OperatorConfig("replace", {"new_value": "-PERSON-"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "-PHONE_NUMBER-"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "-EMAIL_ADDRESS-"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "-LOCATION-"}),
            "DATE_TIME": OperatorConfig("replace", {"new_value": "-DATE_TIME-"}),
            "NRP": OperatorConfig("replace", {"new_value": "-MISC_DATA-"})
        }
    )

    text_perturbed = presidio_perturb.perturb(original_text=text, presidio_response=analyzer_results, count=1)
    if pipeline:
        show_pipeline(analyzer_results, text_perturbed[0], text)
    else:
        st.markdown(
            """
            <p><h3 style="color:#E67E22;">Analysis Result:</h3></p>

            ### {}
            
            <p><h3 style="color:#E67E22;">Perturbed:</h3></p>

            ### {}
            ###
            ### Check entities detected:
            """.format(str(anonymized_results.text), text_perturbed[0]), 
            unsafe_allow_html=True)

        for entity in analyzer_results:
            if entity.score > 0.05:
                with st.beta_expander("Entity type: {}".format(entity.entity_type)):
                    st.markdown(
                        """
                        Start: {} | End: {} | Score: {}
                        """.format(entity.start, entity.end, entity.score)
                        )

def anon_image(image):
    image = Image.open(image)
    ImageEngine = ImageRedactorEngine()
    redacted_image = ImageEngine.redact(image, (255, 128, 0))
    st.image(redacted_image)

st.sidebar.markdown(
    """
    # S E C R E T U M
    #### Additional info:
    ###
    <img src="https://media.giphy.com/media/lhwgPv0AuJehQ2S8cb/giphy.gif"  width="300" />

    ## Tehcnologies Used for this project: 
    ##
    <a href="https://microsoft.github.io/presidio/"><img src="https://microsoft.github.io/presidio/assets/ms_icon.png"  width="60" /></a>
    
    ### ► Microsoft Presidio
    ##
    <a href="https://spacy.io/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/SpaCy_logo.svg/1200px-SpaCy_logo.svg.png"  width="90" /></a>
    
    ### ► Spacy
    ##
    <a href="https://spacy.io/"><img src="https://stanfordnlp.github.io/stanza/assets/images/stanza.png"  width="120" /></a>
    
    ### ► Stanza
    #

    ## Project backed by:
    <a href="https://positivus.io/"><img src="https://res-2.cloudinary.com/crunchbase-production/image/upload/c_lpad,f_auto,q_auto:eco/c0f2ff7q0txvf7gzzedf"  width="150" /></a>
    <a href="https://strive.school/"><img src="https://strive.school/assets/strive_white.png"  width="120" /></a>
    

    ## Repo Link :
    #  
    <a href=""><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"  width="120" /></a>
    #

    #### About Me :
    # Lorenzo Demiri
    ### AI Engineer
   <a href="https://ibb.co/DrXkpvD"><img src="https://i.ibb.co/8Y32cfD/DSC06306.jpg" width="200" border="0"></a>
   ###  📫 : [lorenzo.demiri96@gmail.com]()
    <a href="https://www.linkedin.com/in/lorenzo-demiri/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"  width="120" /></a>
    <a href="https://twitter.com/LorenzoDemiri"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" /></a>
    
    """, 
    unsafe_allow_html=True)

st.markdown("""
                    <head>
                    <link href='https://fonts.googleapis.com/css?family=Poiret One' rel='stylesheet'>
                    <style>
                    <style>
                    body {
                        font-family: 'Poiret One';
                    }
                    h1 {
                    font-family: 'Poiret One';
                    text-align: center;
                    font-size: 75px;
                    }
                    h2 {
                    font-family: 'Poiret One';
                    text-align: center;
                    }
                    h3 {
                    font-family: 'Poiret One';
                    text-align: center;
                    }
                    h4 {
                    font-family: 'Poiret One';
                    text-align: center;
                    }
                    h5 {
                    font-family: 'Poiret One';
                    text-align: center;
                    } 
                    h6 {
                    font-family: 'Poiret One';
                    text-align: center;
                    color: #E67E22;
                    }
                    p {
                    font-family: 'Poiret One';
                    text-align: center;
                    font-weight: bold;
                    }                                                       
                    .center {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    height: 50%;
                    }
                    .loading {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    }
                    </style>
                    </head>
                    <body>
                    <h1>S E C R E T U M</p> 
                    <p>(    Data Anonymization Tool)</p>
                    <img src="https://media.giphy.com/media/lhwgPv0AuJehQ2S8cb/giphy.gif" width="300" class="loading">
                    </body >
""", unsafe_allow_html=True)

st.markdown("""
    S E C R E T U M (Data Anonymization Tool) is a software that finds and hides all the sensitive data in a text
    such as: Name, Email, Telephone Number and etc.

    The data inserted on the app are not stored or memorized, 
    data privacy first priority ;)
""")

st.markdown("""
Try our tool, insert a text or an image containing sensitive information then press the button Anonymize Data.
\n(Ex. Hi I'm Mark Spencer and I live in Whashington)
""")
file_upload = st.file_uploader(
    "Upload an image containing a documente to Anonymize or with your smartphone snap a photo to document.")
st.markdown("""
                <head>
                <style>
                p {{
                text-align: center;
                }}
                </style>
                </head>
                <body>
                <p>Or</p>
                </body >
                """, unsafe_allow_html=True)
text = st.text_area("Insert text to Anonymize")
show_pl = st.checkbox("Show Pipeline")
button = st.button("Anonymize Data")

if button  and text != "":
    anon_text(text, show_pl)
elif button and file_upload is not None:
    anon_image(file_upload)

st.markdown("More info about this project")
with st.beta_expander("Why do we need Data Anonymization?"):
    st.markdown("""
    ### "Data is the new oil" 
    \nIs concept behind this project. 
    Today we live in society where the Data are a new technology assets for companies and goverments, by analyzing and processing those data
    we can build new technologies and products that can improve our lives drastically. 
    However, such as all the new disruptive technologies, there's always a negative side,
    as Data is an important asset and protecting those has become a priority in the tech industry and for
    goverments as well, one example is the General Data Protection Regulation (GDPR) from EU that guide the private
    entities on how to store and process the data collected from the users.
    The aim of this tool is to find, hide or replace with fake synthetic data all the sensitive information
    contained in a text such as: emails, contracts, bills, databases, text datasets etc..
    
    \nWe define as sensitive information all of those kind of data that are gathered from private entities:
    Name, Surname, Location, Dates, Nationalities, Emails, Telephone Numbers, Domains, Credid Card Numbers, Fiscal Code and etc.
    \nFor any other information, feel free to check out the github repo (on the sidebar) or contact me via LinkedIn or Email.
            """
                )
with st.beta_expander("Engines in Details"):
    st.markdown("""<a href="https://ibb.co/KLPdCYy"><img src="https://i.ibb.co/2s9xXwK/Screenshot-from-2021-06-07-10-15-42.png" border="0"></a>""", unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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


def anon_text(text):

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
    print("_"*100, anonymized_results.text)
    text_perturbed = presidio_perturb.perturb(original_text=text, presidio_response=analyzer_results, count=1)
    st.markdown(
        """
        <p><h3 style="color:LightCoral;">Analysis Result:</h3></p>

        ### {}
        
        <p><h3 style="color:LightCoral;">Perturbed:</h3></p>

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
    redacted_image = ImageEngine.redact(image, (255, 192, 203))
    st.image(redacted_image)

st.sidebar.markdown(
    """
    # Data Anonymization Tool
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

    ## Repo Link :
    #  
    <a href=""><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"  width="120" /></a>
    #

    ## Contact Me :
    #  
    <a href="https://www.linkedin.com/in/lorenzo-demiri/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"  width="120" /></a>
    <a href="https://twitter.com/LorenzoDemiri"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" /></a>
    
    """, 
    unsafe_allow_html=True
)

st.title("D.ANON")

st.markdown("""
    D.ANON (Data Anonymization Tool) is a software that finds and hides all the sensitive data
    such as: Name, Email, Telephone Number and etc. from a text.

    The data inserted on the app are not stored or memorized, 
    data privacy first priority ;)
""")
st.image("strem_img/dataprotection_shutterstock_382458778.jpg")

st.markdown("""
Try our tool, insert a text or an image containing sensitive information then press the button Anonymize Data.
\n(Ex. Hi I'm Mark Spencer and I live in Whashington)
""")

text = st.text_area("Insert text to Anonymize")
st.markdown("""
## or
## """)
file_upload = st.file_uploader("Upload an image containing a documente to Anonymize or with your smartphone snap a photo to document.")

button = st.button("Anonymize Data")


if button  and text != "":
    anon_text(text)
elif button and file_upload is not None:
    anon_image(file_upload)

st.markdown("More info")
with st.beta_expander("Why do we need Data Anonymization?"):
    st.markdown("""
    ### "Data is the new oil" 
    \nThe concept behind this project. 
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
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

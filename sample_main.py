import streamlit as st
import requests
import json

# Base URL for the ClinicalTrials.gov API v2 server.
BASE_URL = "https://clinicaltrials.gov/api/v2"

def fetch_trial_details(nct_id):
    """
    Fetch full details for a study with the given NCT ID.
    """
    url = f"{BASE_URL}/studies/{nct_id}"
    try:
        response = requests.get(url, params={"format": "json", "markupFormat": "markdown"})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching details for {nct_id}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while fetching details for {nct_id}: {e}")
        return None

# Initialize session state for storing fetched trial details.
if "trial_details" not in st.session_state:
    st.session_state.trial_details = {}

# Initialize session state for chat history (grouped by NCT ID).
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

def view_details_callback(nct_id):
    """Callback function for fetching trial details."""
    details = fetch_trial_details(nct_id)
    if details:
        st.session_state.trial_details[nct_id] = details

def chat_with_trial(user_message, trial_context):
    """
    Chat with the clinical trial using Ollama and the Llama3.2:latest model.
    
    Combines trial context with the user's message and sends it to Llama3.2 running locally.
    Uses streaming mode to accumulate chunks until done.
    """
    full_prompt = (
        f"Clinical Trial Details:\n{trial_context}\n\n"
        f"User: {user_message}\n"
        "Assistant:"
    )
    
    payload = {
        "model": "llama3.2",  # Model name as specified.
        "prompt": full_prompt,
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True)
        full_response = ""
        # Iterate over the streaming chunks
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    full_response += chunk.get("response", "")
                    if chunk.get("done", False):
                        break
                except Exception as ex:
                    st.error("Error parsing streaming chunk: " + str(ex))
        return full_response
    except Exception as e:
        st.error("Error communicating with the Llama model on Ollama: " + str(e))
        return ""

st.title("ClinicalTrials.gov Search and Chat App")

# Sidebar: Choose search type.
search_mode = st.sidebar.radio("Select search type", ["NCT ID", "Condition", "Advanced Search"])

def display_study_summary(study, button_key_prefix=""):
    """
    Display a study summary along with a 'View Details' button.
    If details are already fetched, show them in an expanded expander.
    """
    identification = study.get("protocolSection", {}).get("identificationModule", {})
    status = study.get("protocolSection", {}).get("statusModule", {})
    nct_id = identification.get("nctId", "N/A")
    title = identification.get("briefTitle", "N/A")
    overall_status = status.get("overallStatus", "N/A")

    st.markdown(f"**NCT ID:** {nct_id}  |  **Title:** {title}  |  **Status:** {overall_status}")
    
    st.button("View Details",
              key=f"{button_key_prefix}btn_{nct_id}",
              on_click=view_details_callback,
              args=(nct_id,))
    
    if nct_id in st.session_state.trial_details:
        with st.expander(f"Details for {nct_id}", expanded=True):
            st.json(st.session_state.trial_details[nct_id])
    st.markdown("---")

# --- Search Mode: NCT ID ---
if search_mode == "NCT ID":
    st.header("Search by NCT ID")
    nct_id_input = st.text_input("Enter a single NCT ID (e.g., NCT00841061):")
    if st.button("Search by NCT ID"):
        if nct_id_input:
            url = f"{BASE_URL}/studies/{nct_id_input}"
            st.info(f"Calling: {url}")
            try:
                response = requests.get(url, params={"format": "json", "markupFormat": "markdown"})
                if response.status_code == 200:
                    study = response.json()
                    st.subheader("Study Details")
                    st.json(study)
                    # Store the fetched details for chat.
                    st.session_state.trial_details[nct_id_input] = study
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter an NCT ID.")

# --- Search Mode: Condition ---
elif search_mode == "Condition":
    st.header("Search by Condition/Disease")
    condition = st.text_input("Enter condition/disease (e.g., 'lung cancer'):")
    page_size = st.number_input("Page Size", min_value=1, max_value=100, value=10)
    if st.button("Search by Condition"):
        if condition:
            url = f"{BASE_URL}/studies"
            params = {
                "query.cond": condition,
                "pageSize": page_size,
                "format": "json",
                "markupFormat": "markdown"
            }
            st.info(f"Calling: {url} with parameters: {params}")
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    studies = data.get("studies", [])
                    total_count = data.get("totalCount", "N/A")
                    st.write(f"Total studies found: {total_count}")
                    if studies:
                        st.subheader("Studies")
                        for study in studies:
                            display_study_summary(study)
                    else:
                        st.write("No studies found for the given condition.")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a condition/disease.")

# --- Search Mode: Advanced Search ---
elif search_mode == "Advanced Search":
    st.header("Advanced Search")
    st.write("Fill in any of the fields below to perform an advanced search. Leave a field blank to ignore it.")
    condition = st.text_input("Condition (query.cond):")
    title_search = st.text_input("Title / Acronym (query.titles):")
    term_search = st.text_input("Other Terms (query.term):")
    nct_ids = st.text_input("NCT IDs (comma separated, will be used with filter.ids):")
    page_size = st.number_input("Page Size", min_value=1, max_value=100, value=10)
    if st.button("Advanced Search"):
        url = f"{BASE_URL}/studies"
        params = {
            "pageSize": page_size,
            "format": "json",
            "markupFormat": "markdown"
        }
        if condition:
            params["query.cond"] = condition
        if title_search:
            params["query.titles"] = title_search
        if term_search:
            params["query.term"] = term_search
        if nct_ids:
            ids = "|".join([s.strip() for s in nct_ids.split(",") if s.strip()])
            params["filter.ids"] = ids

        st.info(f"Calling: {url} with parameters: {params}")
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                studies = data.get("studies", [])
                total_count = data.get("totalCount", "N/A")
                st.write(f"Total studies found: {total_count}")
                if studies:
                    st.subheader("Studies")
                    for study in studies:
                        display_study_summary(study, button_key_prefix="adv_")
                else:
                    st.write("No studies found.")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

st.markdown("---")
st.header("Chat with a Clinical Trial")

# Display chat section only if at least one trial's details are available.
if st.session_state.trial_details:
    # Let the user select which trial (NCT ID) to chat about.
    trial_options = list(st.session_state.trial_details.keys())
    selected_nct_id = st.selectbox("Select a trial to chat about", trial_options)
    
    # Create a trial context summary (customize as needed).
    trial_details = st.session_state.trial_details[selected_nct_id]
    #print(trial_details)
    identification = trial_details.get("protocolSection", {}).get("identificationModule", {})
    status = trial_details.get("protocolSection", {}).get("statusModule", {})
    description = trial_details.get("protocolSection", {}).get("descriptionModule", {})
    eligibility = trial_details.get("protocolSection", {}).get("eligibilityModule", {})
    outcomes = trial_details.get("protocolSection", {}).get("outcomesModule", {})


    # trial_context = (
    #      f"NCT ID: {selected_nct_id}\n"
    #      f"Title: {identification.get('briefTitle', 'N/A')}\n"
    #      f"Status: {status.get('overallStatus', 'N/A')}\n"
    #      f"Details: {trial_details}"
    #  )

    trial_context = (
         f"NCT ID: {selected_nct_id}\n"
         f"Title: {identification.get('briefTitle', 'N/A')}\n"
         f"Status: {status.get('overallStatus', 'N/A')}\n"
         f"Details: {description.get('briefSummary', 'N/A')}\n"
         f"Eligibility: {eligibility.get('eligibilityCriteria', 'N/A')}\n"
         f"Outcomes: {outcomes.get('primaryOutcome', 'N/A')}"         
     )    

    #st.markdown(trial_context)
    user_message = st.text_input("Your message for the trial:", key="chat_input")
    if st.button("Send Message"):
        if user_message:
            # Ensure chat history exists for this trial.
            if selected_nct_id not in st.session_state.chat_history:
                st.session_state.chat_history[selected_nct_id] = []
            
            st.session_state.chat_history[selected_nct_id].append({"role": "user", "content": user_message})
            
            response_text = chat_with_trial(user_message, trial_context)
            st.session_state.chat_history[selected_nct_id].append({"role": "assistant", "content": response_text})
    
    if selected_nct_id in st.session_state.chat_history:
        st.markdown("### Conversation")
        for chat in st.session_state.chat_history[selected_nct_id]:
            if chat["role"] == "user":
                st.markdown(f"**You:** {chat['content']}")
            else:
                st.markdown(f"**Assistant:** {chat['content']}")
else:
    st.info("No trial details available to chat with. Please fetch trial details using one of the search modes.")

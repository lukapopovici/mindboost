# Instructions for Running Bedrock Monitor and Connecting with Bedrock Client Microservice

1. **Install dependencies:**
   ```
   pip install streamlit
   ```

2. **Run the Streamlit app:**
   ```
   streamlit run app.py
   ```

3. **Access the app:**
   The app will start on http://localhost:8501 by default.

4. **Connect with bedrock-client-microservice:**
   In your bedrock-client-microservice, set the following environment variable:
   ```
   BEDROCK_MONITOR_URL=http://localhost:8501/log
   ```

5. **Monitor Bedrock calls:**
   The bedrock-client-microservice will POST Bedrock call logs to this monitor app.
   You can view, list, and monitor Bedrock calls and costs in the Streamlit UI.

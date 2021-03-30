from td.client import TDClient
"""
Follow the tutorial below:
https://www.youtube.com/watch?v=8N1IxYXs4e8&ab_channel=SigmaCoding
"""

# Create a new session, credentials path is required.
TDSession = TDClient(
    client_id='WPT2HCPQWAPY3TPSXDQTNTNXPGSW8ZOH',
    redirect_uri='http://localhost/StrategicOptions',
    credentials_path='C:/Users/chena/Desktop/Trading/TD Ameritrade/API/td_state.json'
)

TDSession.login()
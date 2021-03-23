from td.client import TDClient

# Create a new session, credentials path is required.
TDSession = TDClient(
    client_id='WPT2HCPQWAPY3TPSXDQTNTNXPGSW8ZOH',
    redirect_uri='http://localhost/StrategicOptions',
    credentials_path='C:/Users/chena/Desktop/Trading/TD Ameritrade/API/td_state.json'
)

TDSession.login()

